"""Zenith ranking engine skeleton.

This module will eventually compute angular distance from the observer's
zenith and rank candidate objects by proximity.
"""

from app.engine.coordinates import AltAz
from app.engine.observer import Observer


class ZenithEngine:
    """Computes future zenith proximity scores and rankings."""

    def angular_distance_from_zenith(self, object_position: AltAz) -> float:
        """Compute angular distance from local zenith.

        TODO: Derive angular distance using local altitude and return degrees.
        """
        raise NotImplementedError("Zenith distance calculation is not implemented yet.")

    def rank_by_zenith_proximity(self, observer: Observer, object_positions: list[AltAz]) -> None:
        """Rank objects by proximity to the observer's zenith.

        TODO: Return typed ranked results with object identity, angular
        distance, and supporting observation metadata.
        """
        raise NotImplementedError("Zenith ranking is not implemented yet.")
