"""Observer models for astronomy calculations.

This module defines the observer context that future engines will use when
computing local sky positions, visibility, zenith proximity, and events.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Observer:
    """Represents an observer's location and observation time.

    Attributes:
        latitude: Observer latitude in decimal degrees.
        longitude: Observer longitude in decimal degrees.
        elevation: Observer elevation above sea level in meters.
        observed_at: Timestamp used as the calculation context.
    """

    latitude: float
    longitude: float
    elevation: float
    observed_at: datetime

    def validate(self) -> None:
        """Validate observer coordinates and timestamp.

        TODO: Add bounds checks for latitude, longitude, elevation, and
        timezone-aware timestamps before calculations consume this object.
        """
        raise NotImplementedError("Observer validation is not implemented yet.")
