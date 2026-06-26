"""Astronomical event engine skeleton.

Future implementation will predict notable sky events such as satellite passes,
rise and set times, and conjunctions.
"""

from datetime import datetime

from app.engine.observer import Observer


class EventEngine:
    """Predicts future astronomy events for an observer."""

    def predict_satellite_passes(self, observer: Observer) -> None:
        """Predict satellite passes for the observer.

        TODO: Use propagated satellite tracks to calculate pass start, peak,
        end, maximum altitude, and visibility quality.
        """
        raise NotImplementedError("Satellite pass prediction is not implemented yet.")

    def predict_rise_set(self, observer: Observer, target_name: str) -> None:
        """Predict rise and set times for a celestial target.

        TODO: Calculate rise, transit, and set windows for supported bodies.
        """
        raise NotImplementedError("Rise/set prediction is not implemented yet.")

    def predict_conjunctions(self, observer: Observer, start_at: datetime, end_at: datetime) -> None:
        """Predict conjunctions within a time range.

        TODO: Search future ephemerides for close angular separations between
        supported targets.
        """
        raise NotImplementedError("Conjunction prediction is not implemented yet.")
