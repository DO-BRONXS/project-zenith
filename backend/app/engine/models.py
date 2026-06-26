"""Shared astronomy domain models.

These dataclasses define the pure domain objects exchanged between engine
components. They contain no HTTP, database, provider, AI, or calculation logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.engine.coordinates import AltAz, Cartesian3


@dataclass(frozen=True)
class WeatherSnapshot:
    """Weather conditions relevant to observation quality.

    Attributes:
        temperature: Air temperature in Celsius.
        relative_humidity: Relative humidity percentage.
        cloud_cover: Cloud cover percentage.
        wind_speed: Wind speed in kilometers per hour.
        weather_code: Provider-specific weather condition code.
        captured_at: Timestamp when the weather snapshot was captured.
        metadata: Extra provider or normalization metadata for future engines.
    """

    temperature: float
    relative_humidity: int
    cloud_cover: int
    wind_speed: float
    weather_code: int
    captured_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanetPosition:
    """Domain position for a planet or lunar body.

    Attributes:
        name: Body name, such as Moon, Mars, or Jupiter.
        target_id: External ephemeris target identifier.
        position: Cartesian position vector for future coordinate transforms.
        distance_au: Distance from the observer or reference center in AU.
        observed_at: Timestamp represented by this position.
        alt_az: Optional local horizon coordinate once transformed.
        metadata: Extra ephemeris or reference-frame metadata.
    """

    name: str
    target_id: str
    position: Cartesian3 | None = None
    distance_au: float | None = None
    observed_at: datetime | None = None
    alt_az: AltAz | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SatellitePosition:
    """Domain position for an artificial satellite.

    Attributes:
        satellite_name: Human-readable satellite name.
        norad_id: Optional NORAD catalog identifier.
        tle_line1: Optional first TLE line used for propagation.
        tle_line2: Optional second TLE line used for propagation.
        position: Cartesian position vector for future coordinate transforms.
        velocity: Optional Cartesian velocity vector.
        observed_at: Timestamp represented by this position.
        alt_az: Optional local horizon coordinate once transformed.
        metadata: Extra propagation or catalog metadata.
    """

    satellite_name: str
    norad_id: str | None = None
    tle_line1: str | None = None
    tle_line2: str | None = None
    position: Cartesian3 | None = None
    velocity: Cartesian3 | None = None
    observed_at: datetime | None = None
    alt_az: AltAz | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VisibilityResult:
    """Visibility decision for a celestial or satellite object.

    Attributes:
        is_visible: Whether the object is expected to be visible.
        reason: Human-readable reason for the visibility decision.
        confidence: Optional confidence score for future ranking.
        limiting_factors: Conditions that reduced visibility.
        metadata: Extra details produced by future visibility algorithms.
    """

    is_visible: bool
    reason: str | None = None
    confidence: float | None = None
    limiting_factors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VisibleObject:
    """Object candidate visible from an observer context.

    Attributes:
        object_id: Stable identifier for the object.
        name: Display name for the object.
        object_type: Category such as planet, satellite, star, or event.
        alt_az: Local horizon coordinate when available.
        magnitude: Optional apparent magnitude for future visibility scoring.
        distance_from_zenith: Optional angular distance from local zenith.
        visibility: Optional visibility decision attached by VisibilityEngine.
        metadata: Extra object-specific details.
    """

    object_id: str
    name: str
    object_type: str
    alt_az: AltAz | None = None
    magnitude: float | None = None
    distance_from_zenith: float | None = None
    visibility: VisibilityResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObservationScore:
    """Scoring output for an observation session or object.

    Attributes:
        overall_score: Aggregate score reserved for future ranking.
        visibility_score: Visibility-specific score.
        weather_score: Weather-specific score.
        zenith_score: Zenith-proximity score.
        recommendation: Optional recommendation text for clients.
        factors: Named scoring factors produced by future algorithms.
        metadata: Extra scoring details.
    """

    overall_score: float | None = None
    visibility_score: float | None = None
    weather_score: float | None = None
    zenith_score: float | None = None
    recommendation: str | None = None
    factors: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SatellitePass:
    """Predicted satellite pass event placeholder.

    Attributes:
        satellite_name: Human-readable satellite name.
        starts_at: Predicted pass start time.
        peaks_at: Predicted maximum-altitude time.
        ends_at: Predicted pass end time.
        max_altitude: Maximum altitude in degrees.
        visibility: Optional visibility decision for the pass.
        metadata: Extra pass prediction details.
    """

    satellite_name: str
    starts_at: datetime | None = None
    peaks_at: datetime | None = None
    ends_at: datetime | None = None
    max_altitude: float | None = None
    visibility: VisibilityResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CelestialEvent:
    """Future astronomical event representation.

    Attributes:
        event_id: Stable event identifier.
        event_type: Category such as rise, set, conjunction, or satellite_pass.
        title: Human-readable event title.
        starts_at: Event start timestamp.
        ends_at: Optional event end timestamp.
        objects: Names or identifiers of involved objects.
        score: Optional observation score for the event.
        metadata: Extra prediction details.
    """

    event_id: str
    event_type: str
    title: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    objects: list[str] = field(default_factory=list)
    score: ObservationScore | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObservationReport:
    """Aggregated report produced by the future observation pipeline.

    Attributes:
        generated_at: Timestamp when the report was generated.
        summary: Human-readable report summary.
        visible_objects: Objects considered visible or noteworthy.
        upcoming_events: Events relevant to the observer.
        score: Optional aggregate observation score.
        metadata: Extra report details for downstream clients.
    """

    generated_at: datetime
    summary: str | None = None
    visible_objects: list[VisibleObject] = field(default_factory=list)
    upcoming_events: list[CelestialEvent] = field(default_factory=list)
    score: ObservationScore | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
