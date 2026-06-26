"""Pydantic schemas for planetary observation data."""

from pydantic import BaseModel, Field


class PlanetPosition(BaseModel):
    """Earth-relative position vector for a Solar System body."""

    name: str = Field(..., description="Planet or lunar body name.")
    target_id: str = Field(..., description="NASA Horizons target identifier.")
    timestamp_utc: str = Field(..., description="UTC timestamp used for the ephemeris query.")
    x_au: float = Field(..., description="Earth-relative X coordinate in astronomical units.")
    y_au: float = Field(..., description="Earth-relative Y coordinate in astronomical units.")
    z_au: float = Field(..., description="Earth-relative Z coordinate in astronomical units.")
    distance_au: float = Field(..., description="Earth-relative range in astronomical units.")


class PlanetPositions(BaseModel):
    """Collection of current Solar System body positions."""

    timestamp_utc: str = Field(..., description="UTC timestamp shared by this position snapshot.")
    positions: list[PlanetPosition] = Field(..., description="Current positions for supported bodies.")
