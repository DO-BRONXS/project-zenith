"""Satellite observation service.

This module owns CelesTrak HTTP access and keeps a short in-memory cache for
ACTIVE satellite TLE data.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.schemas.satellite import SatelliteTLE


logger = logging.getLogger(__name__)


class SatelliteServiceError(Exception):
    """Raised when active satellite TLE data cannot be fetched or parsed."""


class SatelliteService:
    """Async CelesTrak client for active satellite TLE data."""

    _cache_data: list[SatelliteTLE] | None = None
    _cache_expires_at: datetime | None = None
    _cache_lock = asyncio.Lock()

    def __init__(self, base_url: str, timeout_seconds: float = 12.0) -> None:
        self._endpoint = f"{base_url.rstrip('/')}/NORAD/elements/gp.php"
        self._timeout_seconds = timeout_seconds

    async def get_active_satellites(self) -> list[SatelliteTLE]:
        """Fetch ACTIVE satellite TLEs, using a 10 minute in-memory cache."""
        cached = self._get_cached_satellites()
        if cached is not None:
            return cached

        async with self._cache_lock:
            cached = self._get_cached_satellites()
            if cached is not None:
                return cached

            satellites = await self._fetch_active_satellites()
            self._set_cache(satellites)
            return satellites

    def _get_cached_satellites(self) -> list[SatelliteTLE] | None:
        """Return cached TLEs when the cache is still fresh."""
        if self._cache_data is None or self._cache_expires_at is None:
            return None

        if datetime.now(timezone.utc) >= self._cache_expires_at:
            return None

        return self._cache_data

    def _set_cache(self, satellites: list[SatelliteTLE]) -> None:
        """Store TLEs for a short period to protect CelesTrak and latency."""
        self.__class__._cache_data = satellites
        self.__class__._cache_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    async def _fetch_active_satellites(self) -> list[SatelliteTLE]:
        """Download and parse ACTIVE satellite TLE data from CelesTrak."""
        params = {"GROUP": "active", "FORMAT": "tle"}

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(self._endpoint, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch active satellite TLE data", exc_info=exc)
            raise SatelliteServiceError("Unable to fetch active satellite data.") from exc

        return self._parse_tle(response.text)

    def _parse_tle(self, tle_text: str) -> list[SatelliteTLE]:
        """Parse CelesTrak TLE triplets into schema objects."""
        lines = [line.strip() for line in tle_text.splitlines() if line.strip()]
        if len(lines) < 3 or len(lines) % 3 != 0:
            logger.warning("Invalid active satellite TLE payload")
            raise SatelliteServiceError("Invalid active satellite response.")

        satellites: list[SatelliteTLE] = []
        for index in range(0, len(lines), 3):
            name, line1, line2 = lines[index : index + 3]
            if not line1.startswith("1 ") or not line2.startswith("2 "):
                logger.warning("Invalid TLE line pair", extra={"satellite_name": name})
                raise SatelliteServiceError("Invalid active satellite response.")

            satellites.append(
                SatelliteTLE(
                    satellite_name=name,
                    tle_line1=line1,
                    tle_line2=line2,
                )
            )

        return satellites
