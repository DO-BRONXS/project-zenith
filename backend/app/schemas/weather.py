"""Pydantic schemas for weather observation data."""

from pydantic import BaseModel, Field


class CurrentWeather(BaseModel):
    """Current weather conditions for an observer location."""

    temperature: float = Field(..., description="Current air temperature in Celsius.")
    relative_humidity: int = Field(..., description="Current relative humidity percentage.")
    cloud_cover: int = Field(..., description="Current cloud cover percentage.")
    wind_speed: float = Field(..., description="Current wind speed in kilometers per hour.")
    weather_code: int = Field(..., description="Open-Meteo weather condition code.")
