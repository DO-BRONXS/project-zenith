"""Visibility engine skeleton.

Future implementation will determine whether satellites, planets, and other
celestial objects are observable from a given observer context.
"""

from app.engine.coordinates import AltAz
from app.engine.observer import Observer


class VisibilityEngine:
    """Evaluates future object visibility rules."""

    def is_above_horizon(self, alt_az: AltAz) -> bool:
        """Determine whether an object is above the local horizon.

        TODO: Implement horizon checks and refraction-aware altitude thresholds.
        """
        raise NotImplementedError("Horizon visibility is not implemented yet.")

    def is_visible(self, observer: Observer, object_position: AltAz) -> bool:
        """Determine whether an object is visible to an observer.

        TODO: Combine horizon, daylight, weather, magnitude, and obstruction
        rules into a typed visibility decision.
        """
        raise NotImplementedError("Visibility evaluation is not implemented yet.")
