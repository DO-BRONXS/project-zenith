"""Observation scoring engine skeleton.

This module defines the pure-domain scoring API used by future astronomy
components. It intentionally contains no scoring algorithms yet.
"""

from app.engine.context import CelestialContext
from app.engine.models import ObservationScore, VisibilityResult, VisibleObject


class ScoringEngine:
    """Computes future visibility and observation quality scores."""

    def compute_visibility_score(
        self,
        visible_object: VisibleObject,
        context: CelestialContext,
    ) -> VisibilityResult:
        """Compute a visibility score for one object.

        TODO: Combine altitude, weather, light pollution, daylight, magnitude,
        and object type into a typed visibility decision.
        """
        raise NotImplementedError("Visibility scoring is not implemented yet.")

    def compute_observation_score(self, context: CelestialContext) -> ObservationScore:
        """Compute an aggregate score for the full observation context.

        TODO: Blend weather, visible objects, zenith proximity, and upcoming
        events into a single normalized observation score.
        """
        raise NotImplementedError("Observation scoring is not implemented yet.")

    def generate_recommendation(self, score: ObservationScore) -> str:
        """Generate a recommendation from a future observation score.

        TODO: Convert score factors into user-facing guidance without using AI
        or external providers.
        """
        raise NotImplementedError("Recommendation generation is not implemented yet.")
