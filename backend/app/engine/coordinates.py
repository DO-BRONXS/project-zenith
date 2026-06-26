"""Coordinate transformation utilities for Project Zenith.

This module is the single source of truth for coordinate conversions used by
the astronomy engine. It deliberately contains only deterministic mathematical
transformations: no HTTP calls, no provider access, no API routing, and no
domain workflow decisions.
"""

from dataclasses import dataclass

import numpy as np
from astropy import units as u
from astropy.coordinates import EarthLocation

from app.engine.observer import Observer


@dataclass(frozen=True)
class GeodeticCoordinate:
    """Observer or surface location in geodetic coordinates.

    Geodetic coordinates describe a point using latitude, longitude, and height
    above the WGS84 reference ellipsoid. Latitude and longitude are expressed in
    degrees; elevation is expressed in meters.
    """

    latitude: float
    longitude: float
    elevation: float = 0.0


@dataclass(frozen=True)
class Cartesian3:
    """Three-dimensional Cartesian vector in meters.

    For ECEF and CesiumJS use cases, ``x``, ``y``, and ``z`` represent meters in
    an Earth-fixed frame. For ENU use cases, the same fields represent east,
    north, and up components in meters.
    """

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class AltAz:
    """Local horizon altitude/azimuth coordinate.

    Altitude is the angle above the observer's horizon in degrees. Azimuth is
    measured clockwise from true north in degrees and normalized to ``[0, 360)``.
    ``distance`` is an optional slant range in meters from the observer.
    """

    altitude: float
    azimuth: float
    distance: float | None = None


class CoordinateEngine:
    """Reusable coordinate transformation engine.

    Each method is intentionally independent and side-effect free so tests can
    validate individual transformations with known reference vectors.
    """

    def geodetic_to_ecef(self, coordinate: GeodeticCoordinate) -> Cartesian3:
        """Convert geodetic latitude, longitude, and elevation to ECEF.

        Earth-Centered, Earth-Fixed coordinates place the origin at Earth's
        center of mass. The ``x`` axis intersects latitude ``0`` and longitude
        ``0``; the ``z`` axis points toward the north pole; the ``y`` axis
        completes the right-handed frame.

        Astropy's ``EarthLocation`` performs the WGS84 ellipsoid conversion:
        geodetic ``(lat, lon, height)`` is projected onto an Earth-fixed ITRS
        Cartesian coordinate. ITRS and ECEF are equivalent for this engine's
        Earth-fixed vector needs.
        """
        location = EarthLocation.from_geodetic(
            lon=coordinate.longitude * u.deg,
            lat=coordinate.latitude * u.deg,
            height=coordinate.elevation * u.m,
        )
        x, y, z = location.itrs.cartesian.xyz.to_value(u.m)
        return Cartesian3(x=float(x), y=float(y), z=float(z))

    def observer_to_ecef(self, observer: Observer) -> Cartesian3:
        """Convert an ``Observer`` into an ECEF Cartesian vector.

        This is a convenience wrapper around ``geodetic_to_ecef`` so later
        engines can pass their shared observer model directly.
        """
        return self.geodetic_to_ecef(
            GeodeticCoordinate(
                latitude=observer.latitude,
                longitude=observer.longitude,
                elevation=observer.elevation,
            )
        )

    def to_ecef(self, coordinate: GeodeticCoordinate | Observer | Cartesian3) -> Cartesian3:
        """Return an ECEF vector from a supported coordinate representation.

        ``GeodeticCoordinate`` and ``Observer`` inputs are converted from
        geodetic coordinates. ``Cartesian3`` inputs are treated as already ECEF
        and returned unchanged, which keeps this method useful for pipelines
        that normalize mixed inputs before downstream transformations.
        """
        if isinstance(coordinate, Cartesian3):
            return coordinate

        if isinstance(coordinate, Observer):
            return self.observer_to_ecef(coordinate)

        return self.geodetic_to_ecef(coordinate)

    def ecef_to_enu(self, target_ecef: Cartesian3, observer: Observer) -> Cartesian3:
        """Convert an ECEF target vector to local ENU coordinates.

        The transformation first subtracts the observer's ECEF vector from the
        target's ECEF vector, producing ``delta = target - observer``. That
        vector is then rotated by the observer's latitude ``phi`` and longitude
        ``lambda``:

        ``east  = -sin(lambda) * dx + cos(lambda) * dy``

        ``north = -sin(phi) * cos(lambda) * dx
                  -sin(phi) * sin(lambda) * dy
                  +cos(phi) * dz``

        ``up    =  cos(phi) * cos(lambda) * dx
                  +cos(phi) * sin(lambda) * dy
                  +sin(phi) * dz``

        The returned ``Cartesian3`` stores ``x=east``, ``y=north``, and
        ``z=up`` in meters.
        """
        observer_ecef = self.observer_to_ecef(observer)
        delta = self._as_array(target_ecef) - self._as_array(observer_ecef)

        latitude = np.deg2rad(observer.latitude)
        longitude = np.deg2rad(observer.longitude)
        sin_latitude = np.sin(latitude)
        cos_latitude = np.cos(latitude)
        sin_longitude = np.sin(longitude)
        cos_longitude = np.cos(longitude)

        rotation = np.array(
            [
                [-sin_longitude, cos_longitude, 0.0],
                [
                    -sin_latitude * cos_longitude,
                    -sin_latitude * sin_longitude,
                    cos_latitude,
                ],
                [
                    cos_latitude * cos_longitude,
                    cos_latitude * sin_longitude,
                    sin_latitude,
                ],
            ],
            dtype=float,
        )
        east, north, up = rotation @ delta
        return Cartesian3(x=float(east), y=float(north), z=float(up))

    def to_enu(self, coordinate: Cartesian3, observer: Observer) -> Cartesian3:
        """Convert an ECEF coordinate into observer-relative ENU.

        This method preserves the original public skeleton name while delegating
        to ``ecef_to_enu``. The input is expected to be an ECEF ``Cartesian3`` in
        meters.
        """
        return self.ecef_to_enu(target_ecef=coordinate, observer=observer)

    def enu_to_alt_az(self, enu: Cartesian3) -> AltAz:
        """Convert local ENU coordinates to altitude and azimuth.

        In a local horizon frame, altitude is the angle between the ENU vector
        and the horizontal east-north plane:

        ``altitude = atan2(up, sqrt(east^2 + north^2))``

        Azimuth is measured clockwise from north. Because ``atan2`` normally
        measures counter-clockwise from the positive x-axis, the arguments are
        swapped so east is the numerator and north is the reference axis:

        ``azimuth = atan2(east, north)``
        """
        horizontal_distance = float(np.hypot(enu.x, enu.y))
        slant_range = float(np.linalg.norm(self._as_array(enu)))

        altitude = np.rad2deg(np.arctan2(enu.z, horizontal_distance))
        azimuth = np.rad2deg(np.arctan2(enu.x, enu.y)) % 360.0

        return AltAz(
            altitude=float(altitude),
            azimuth=float(azimuth),
            distance=slant_range,
        )

    def to_alt_az(self, coordinate: Cartesian3, observer: Observer) -> AltAz:
        """Convert an ECEF coordinate directly to local altitude/azimuth.

        This composes the independent ECEF -> ENU and ENU -> Alt/Az methods
        without adding new astronomy behavior. The input coordinate is expected
        to be Earth-fixed and expressed in meters.
        """
        enu = self.ecef_to_enu(target_ecef=coordinate, observer=observer)
        return self.enu_to_alt_az(enu)

    def ecef_to_cesium_cartesian(self, coordinate: Cartesian3) -> Cartesian3:
        """Return an ECEF vector compatible with CesiumJS ``Cartesian3``.

        CesiumJS ``Cartesian3.fromDegrees`` ultimately represents positions as
        Earth-fixed Cartesian meters. Project Zenith's ECEF ``Cartesian3`` uses
        the same unit and axis convention, so this method is an explicit
        boundary marker for frontend handoff rather than a numerical transform.
        """
        return coordinate

    def geodetic_to_cesium_cartesian(self, coordinate: GeodeticCoordinate) -> Cartesian3:
        """Convert geodetic coordinates to a CesiumJS-compatible vector.

        The transformation is Geodetic -> ECEF. The returned vector can be
        serialized as ``{x, y, z}`` for CesiumJS ``Cartesian3`` consumers.
        """
        return self.ecef_to_cesium_cartesian(self.geodetic_to_ecef(coordinate))

    def _as_array(self, coordinate: Cartesian3) -> np.ndarray:
        """Represent a ``Cartesian3`` as a NumPy vector for matrix operations."""
        return np.array([coordinate.x, coordinate.y, coordinate.z], dtype=float)
