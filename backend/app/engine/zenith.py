"""Zenith ranking engine.

The zenith is the point directly above an observer, corresponding to altitude
90 degrees in the local Alt/Az sky frame. This engine ranks already-visible
celestial objects by how close they are to that overhead point.

Ranking algorithm
    ZenithEngine consumes VisibleObject domain instances produced by earlier
    pipeline stages. It ignores objects that are explicitly marked as not
    visible, ignores objects without Alt/Az coordinates, computes
    ``zenith_distance = 90 - altitude``, and sorts by the smallest distance.

Why altitude is sufficient
    After visibility filtering, each candidate is already known to be above the
    horizon. In the local Alt/Az frame, zenith proximity depends only on angular
    separation from altitude 90 degrees. Azimuth does not affect distance from
    zenith because every azimuth direction converges at the overhead point.

Architecture decisions
    This module performs no propagation, coordinate transformation, visibility
    calculation, API access, or HTTP communication. It is stateless and can be
    used by the future ObservationEngine after VisibilityEngine has enriched the
    context with visible objects.
"""

from dataclasses import dataclass
from typing import Iterable

from app.engine.coordinates import AltAz
from app.engine.models import VisibleObject


@dataclass(frozen=True)
class ZenithRanking:
    """Ranked visible object and its angular distance from zenith.

    Attributes:
        visible_object: Visible object being ranked.
        rank: One-based rank after sorting by zenith proximity.
        zenith_distance: Angular distance from local zenith in degrees.
    """

    visible_object: VisibleObject
    rank: int
    zenith_distance: float


@dataclass(frozen=True)
class ZenithResult:
    """Complete zenith ranking result for a collection of visible objects.

    Attributes:
        closest_object: Object nearest to zenith, or None when no visible
            candidates have usable Alt/Az coordinates.
        rankings: Ordered rankings from nearest to farthest from zenith.
    """

    closest_object: VisibleObject | None
    rankings: list[ZenithRanking]


class ZenithEngine:
    """Stateless engine for ranking visible objects by zenith proximity."""

    def rank_visible_objects(self, visible_objects: Iterable[VisibleObject]) -> ZenithResult:
        """Rank visible objects by smallest angular distance from zenith.

        Args:
            visible_objects: Domain objects produced by the visibility stage.
                Objects explicitly marked as not visible, or missing Alt/Az
                coordinates, are excluded from ranking.

        Returns:
            ZenithResult containing the closest object and all ordered rankings.

        Complexity:
            ``O(n log n)`` because candidates are filtered in linear time and
            sorted by zenith distance.
        """
        candidates = [
            (visible_object, self.angular_distance_from_zenith(visible_object.alt_az))
            for visible_object in visible_objects
            if self._can_rank(visible_object)
        ]
        candidates.sort(key=lambda candidate: candidate[1])

        rankings = [
            ZenithRanking(
                visible_object=visible_object,
                rank=index,
                zenith_distance=zenith_distance,
            )
            for index, (visible_object, zenith_distance) in enumerate(candidates, start=1)
        ]

        closest_object = rankings[0].visible_object if rankings else None
        return ZenithResult(closest_object=closest_object, rankings=rankings)

    def top_n(self, visible_objects: Iterable[VisibleObject], limit: int) -> list[ZenithRanking]:
        """Return the top N visible objects nearest to zenith.

        Args:
            visible_objects: Domain objects produced by the visibility stage.
            limit: Maximum number of ranked objects to return. Values less than
                or equal to zero return an empty list.

        Returns:
            A list of at most ``limit`` rankings ordered by zenith proximity.
        """
        if limit <= 0:
            return []

        return self.rank_visible_objects(visible_objects).rankings[:limit]

    def closest_object(self, visible_objects: Iterable[VisibleObject]) -> VisibleObject | None:
        """Return the visible object closest to zenith, if one exists."""
        return self.rank_visible_objects(visible_objects).closest_object

    def angular_distance_from_zenith(self, object_position: AltAz) -> float:
        """Compute angular distance from local zenith in degrees.

        Zenith has altitude 90 degrees. Once an object has an Alt/Az coordinate,
        its angular distance from zenith is simply ``90 - altitude``.
        """
        return 90.0 - float(object_position.altitude)

    def rank_by_zenith_proximity(self, visible_objects: Iterable[VisibleObject]) -> ZenithResult:
        """Compatibility wrapper for ranking visible objects.

        This preserves the skeleton method name while aligning the API with the
        architecture: ZenithEngine consumes VisibleObject instances, not raw
        observer coordinates or propagated states.
        """
        return self.rank_visible_objects(visible_objects)

    def _can_rank(self, visible_object: VisibleObject) -> bool:
        """Return whether a VisibleObject has enough data for zenith ranking."""
        if visible_object.alt_az is None:
            return False

        if visible_object.visibility is None:
            return True

        return visible_object.visibility.is_visible
