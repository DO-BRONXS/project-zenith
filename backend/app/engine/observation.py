"""Observation aggregation engine skeleton.

This module will combine provider observations and computed astronomy results
into higher-level observation snapshots for the product experience.
"""

from app.engine.observer import Observer


class ObservationEngine:
    """Aggregates weather, satellite, planet, zenith, and event data."""

    def build_observation_snapshot(self, observer: Observer) -> None:
        """Build a complete observation snapshot for an observer.

        TODO: Combine weather conditions, satellite tracks, planetary
        positions, zenith rankings, and event predictions into one typed model.
        """
        raise NotImplementedError("Observation snapshot aggregation is not implemented yet.")

    def score_observation_quality(self, observer: Observer) -> None:
        """Score observation quality for the observer context.

        TODO: Use weather, daylight, object altitude, and visibility decisions
        to produce an observation quality score.
        """
        raise NotImplementedError("Observation quality scoring is not implemented yet.")
