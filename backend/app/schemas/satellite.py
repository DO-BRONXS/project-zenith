"""Pydantic schemas for satellite observation data."""

from pydantic import BaseModel, Field


class SatelliteTLE(BaseModel):
    """Two-line element set for an active satellite."""

    satellite_name: str = Field(..., description="Satellite name from the TLE catalog.")
    tle_line1: str = Field(..., description="First TLE orbital element line.")
    tle_line2: str = Field(..., description="Second TLE orbital element line.")
