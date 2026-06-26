"""Top-level astronomy engine orchestration skeleton.

The AstronomyEngine will coordinate specialized engines while keeping each
calculation responsibility isolated and replaceable.
"""

from dataclasses import dataclass, field

from app.engine.coordinates import CoordinateEngine
from app.engine.events import EventEngine
from app.engine.observation import ObservationEngine
from app.engine.observer import Observer
from app.engine.propagation import PropagationEngine
from app.engine.visibility import VisibilityEngine
from app.engine.zenith import ZenithEngine


@dataclass
class AstronomyEngine:
    """Orchestrates future astronomy computation engines."""

    coordinate_engine: CoordinateEngine = field(default_factory=CoordinateEngine)
    event_engine: EventEngine = field(default_factory=EventEngine)
    observation_engine: ObservationEngine = field(default_factory=ObservationEngine)
    propagation_engine: PropagationEngine = field(default_factory=PropagationEngine)
    visibility_engine: VisibilityEngine = field(default_factory=VisibilityEngine)
    zenith_engine: ZenithEngine = field(default_factory=ZenithEngine)

    def evaluate_observer(self, observer: Observer) -> None:
        """Run the future end-to-end astronomy evaluation pipeline.

        TODO: Coordinate propagation, coordinate transforms, visibility,
        zenith ranking, event prediction, and observation aggregation.
        """
        raise NotImplementedError("Astronomy orchestration is not implemented yet.")
