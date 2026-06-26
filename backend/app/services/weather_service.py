"""Weather observation service.

This module owns all Open-Meteo HTTP calls and maps provider data into the
weather schemas consumed by API routers and future astronomy workflows.
"""

import logging

import httpx

from app.schemas.weather import CurrentWeather


logger = logging.getLogger(__name__)


class WeatherServiceError(Exception):
    """Raised when current weather data cannot be fetched or parsed."""


class WeatherService:
    """Async Open-Meteo client for observer weather conditions."""

    def __init__(self, base_url: str, timeout_seconds: float = 8.0) -> None:
        self._endpoint = f"{base_url.rstrip('/')}/v1/forecast"
        self._timeout_seconds = timeout_seconds

    async def get_current_weather(self, latitude: float, longitude: float) -> CurrentWeather:
        """Fetch current weather for a latitude and longitude."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "cloud_cover",
                    "wind_speed_10m",
                    "weather_code",
                ]
            ),
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(self._endpoint, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning(
                "Failed to fetch current weather",
                extra={"latitude": latitude, "longitude": longitude},
                exc_info=exc,
            )
            raise WeatherServiceError("Unable to fetch current weather data.") from exc

        try:
            current = response.json()["current"]
            return CurrentWeather(
                temperature=float(current["temperature_2m"]),
                relative_humidity=int(current["relative_humidity_2m"]),
                cloud_cover=int(current["cloud_cover"]),
                wind_speed=float(current["wind_speed_10m"]),
                weather_code=int(current["weather_code"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("Invalid current weather payload", exc_info=exc)
            raise WeatherServiceError("Invalid current weather response.") from exc
