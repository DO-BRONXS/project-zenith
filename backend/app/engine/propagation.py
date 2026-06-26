"""Satellite orbital propagation engine.

This module owns only orbit propagation: turning a satellite TLE and a requested
timestamp into Earth-centered position and velocity vectors. It performs no
HTTP calls, no API routing, no visibility checks, and no observer-relative
altitude/azimuth calculations.

TLE
    A Two-Line Element set is a compact text format published for Earth-orbiting
    objects. The two lines encode the satellite's orbital elements at a specific
    epoch plus drag and correction terms required by the SGP4 model.

SGP4
    Simplified General Perturbations 4 is the standard propagation model used
    with TLE data. It estimates a satellite state at a requested time while
    accounting for the perturbation terms represented by the TLE.

ECI
    Earth-Centered Inertial coordinates represent the satellite in a geocentric
    inertial frame. This is the natural output frame for orbital propagation and
    is useful for later astronomy and event engines that need inertial state.

ECEF
    Earth-Centered, Earth-Fixed coordinates rotate with Earth. ECEF output is
    the handoff point for later coordinate work: the CoordinateEngine can turn
    an ECEF position into observer-relative ENU and Alt/Az without duplicating
    orbital propagation logic here.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from sgp4.api import Satrec
from skyfield.api import EarthSatellite, load
from skyfield.framelib import itrs


@dataclass(frozen=True)
class PropagationVector:
    """Three-dimensional vector returned by satellite propagation.

    Position vectors use kilometers. Velocity vectors use kilometers per second.
    These units match the native conventions exposed by Skyfield and SGP4.
    """

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class PropagationResult:
    """Earth-centered satellite state at a requested timestamp.

    Attributes:
        eci_position: Satellite position in an Earth-centered inertial frame.
        ecef_position: Satellite position in the Earth-fixed ITRS/ECEF frame.
        velocity: Satellite velocity in the same inertial frame as
            ``eci_position``.
        timestamp: Time used for propagation, normalized to UTC.

    Later engines can consume this result as follows:
        - CoordinateEngine can use ``ecef_position`` for observer-relative
          transformations.
        - VisibilityEngine can consume downstream Alt/Az values, not this raw
          orbital state directly.
        - EventEngine can propagate repeated timestamps to detect passes,
          rise/set windows, and closest approaches.
    """

    eci_position: PropagationVector
    ecef_position: PropagationVector
    velocity: PropagationVector
    timestamp: datetime


class PropagationError(ValueError):
    """Raised when a TLE cannot be propagated to the requested timestamp."""


class PropagationEngine:
    """Stateless SGP4/Skyfield satellite propagation engine.

    The engine stores no per-satellite or per-request state. Batch propagation
    methods reuse local objects within a single call so future workflows can
    process thousands of satellites without leaking state across requests.
    """

    def propagate_satellite(
        self,
        tle_line1: str,
        tle_line2: str,
        timestamp: datetime,
    ) -> PropagationResult:
        """Propagate one TLE to a requested timestamp.

        Args:
            tle_line1: First line of the satellite TLE.
            tle_line2: Second line of the satellite TLE.
            timestamp: Requested propagation time. Naive datetimes are treated
                as UTC; timezone-aware datetimes are converted to UTC.

        Returns:
            A ``PropagationResult`` containing ECI position, ECEF position,
            inertial velocity, and the normalized UTC timestamp.

        Raises:
            PropagationError: If the TLE is malformed or SGP4 cannot propagate
                the satellite state for the requested time.
        """
        timescale = load.timescale(builtin=True)
        timestamp_utc = self._normalize_timestamp(timestamp)
        skyfield_time = self._to_skyfield_time(timestamp_utc, timescale)
        satellite = self._build_satellite(tle_line1, tle_line2, timescale)

        return self._propagate(satellite, skyfield_time, timestamp_utc)

    def propagate_many(
        self,
        tle_pairs: Iterable[tuple[str, str]],
        timestamp: datetime,
    ) -> list[PropagationResult]:
        """Propagate many TLEs to one timestamp.

        This method is designed for future high-volume satellite workflows. It
        creates the Skyfield timescale and timestamp once per batch, then
        propagates each TLE independently without retaining state afterward.
        """
        timescale = load.timescale(builtin=True)
        timestamp_utc = self._normalize_timestamp(timestamp)
        skyfield_time = self._to_skyfield_time(timestamp_utc, timescale)

        results: list[PropagationResult] = []
        for tle_line1, tle_line2 in tle_pairs:
            satellite = self._build_satellite(tle_line1, tle_line2, timescale)
            results.append(self._propagate(satellite, skyfield_time, timestamp_utc))

        return results

    def _build_satellite(self, tle_line1: str, tle_line2: str, timescale) -> EarthSatellite:
        """Validate TLE text with SGP4 and build a Skyfield satellite object."""
        try:
            Satrec.twoline2rv(tle_line1, tle_line2)
            return EarthSatellite(tle_line1, tle_line2, ts=timescale)
        except Exception as exc:
            raise PropagationError("Invalid TLE lines; satellite cannot be initialized.") from exc

    def _propagate(
        self,
        satellite: EarthSatellite,
        skyfield_time,
        timestamp_utc: datetime,
    ) -> PropagationResult:
        """Propagate a Skyfield satellite and map vectors into immutable output."""
        geocentric = satellite.at(skyfield_time)
        message = getattr(geocentric, "message", None)
        if message:
            raise PropagationError(f"SGP4 propagation failed: {message}")

        eci_position = geocentric.position.km
        ecef_position = geocentric.frame_xyz(itrs).km
        velocity = geocentric.velocity.km_per_s

        return PropagationResult(
            eci_position=PropagationVector(
                x=float(eci_position[0]),
                y=float(eci_position[1]),
                z=float(eci_position[2]),
            ),
            ecef_position=PropagationVector(
                x=float(ecef_position[0]),
                y=float(ecef_position[1]),
                z=float(ecef_position[2]),
            ),
            velocity=PropagationVector(
                x=float(velocity[0]),
                y=float(velocity[1]),
                z=float(velocity[2]),
            ),
            timestamp=timestamp_utc,
        )

    def _normalize_timestamp(self, timestamp: datetime) -> datetime:
        """Return a UTC timestamp suitable for deterministic propagation."""
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            return timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)

    def _to_skyfield_time(self, timestamp: datetime, timescale):
        """Convert a UTC ``datetime`` into a Skyfield time object."""
        return timescale.from_datetime(timestamp)
