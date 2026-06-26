"""Shared celestial context for engine orchestration.

CelestialContext is the mutable domain object passed between astronomy engine
components. Each engine can enrich it by setting or appending results without
overwriting unrelated data produced earlier in the pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.engine.models import (
    CelestialEvent,
    ObservationReport,
    ObservationScore,
    PlanetPosition,
    SatellitePosition,
    VisibleObject,
    WeatherSnapshot,
)
from app.engine.observer import Observer


@dataclass
class CelestialContext:
    """Shared state object for the future astronomy engine pipeline.

    Attributes:
        observer: Observer location and timestamp context.
        weather: Weather conditions attached by weather-aware components.
        iss_position: ISS position represented as a satellite domain object.
        satellite_positions: Satellite positions enriched by propagation.
        planet_positions: Planetary positions enriched by ephemeris components.
        visible_objects: Objects marked as visible or noteworthy.
        zenith_object: Object currently closest to the observer's zenith.
        observation_report: Aggregated observation report.
        observation_score: Aggregate observation score.
        upcoming_events: Predicted events relevant to the observer.
        current_datetime: Processing timestamp for the context.
        metadata: Shared non-critical metadata for engine coordination.
    """

    observer: Observer
    weather: WeatherSnapshot | None = None
    iss_position: SatellitePosition | None = None
    satellite_positions: list[SatellitePosition] = field(default_factory=list)
    planet_positions: list[PlanetPosition] = field(default_factory=list)
    visible_objects: list[VisibleObject] = field(default_factory=list)
    zenith_object: VisibleObject | None = None
    observation_report: ObservationReport | None = None
    observation_score: ObservationScore | None = None
    upcoming_events: list[CelestialEvent] = field(default_factory=list)
    current_datetime: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_visible_object(self, visible_object: VisibleObject) -> None:
        """Append a visible object without modifying existing results.

        TODO: Add duplicate handling or stable merge semantics when object
        identifiers become finalized.
        """
        self.visible_objects.append(visible_object)

    def set_weather(self, weather: WeatherSnapshot) -> None:
        """Attach the current weather snapshot to the context.

        TODO: Preserve weather source metadata and quality flags when the
        observation pipeline starts normalizing provider payloads.
        """
        self.weather = weather

    def set_observation_score(self, score: ObservationScore) -> None:
        """Attach an aggregate observation score to the context.

        TODO: Track score provenance once multiple scoring engines contribute
        partial scores.
        """
        self.observation_score = score

    def add_event(self, event: CelestialEvent) -> None:
        """Append an upcoming celestial event without modifying prior events.

        TODO: Add ordering, de-duplication, and event-window merge rules when
        event prediction is implemented.
        """
        self.upcoming_events.append(event)

    def add_satellite_position(self, satellite_position: SatellitePosition) -> None:
        """Append a satellite position to the context.

        TODO: Merge positions by satellite identifier when propagation produces
        multi-timestamp tracks.
        """
        self.satellite_positions.append(satellite_position)

    def add_planet_position(self, planet_position: PlanetPosition) -> None:
        """Append a planetary position to the context.

        TODO: Merge positions by target identifier when time-series ephemerides
        are introduced.
        """
        self.planet_positions.append(planet_position)

    def set_zenith_object(self, visible_object: VisibleObject) -> None:
        """Attach the object currently closest to zenith.

        TODO: Include ranking provenance once ZenithEngine produces scored
        candidate lists.
        """
        self.zenith_object = visible_object

    def set_observation_report(self, report: ObservationReport) -> None:
        """Attach an aggregated observation report.

        TODO: Track report generation version once report formatting evolves.
        """
        self.observation_report = report
