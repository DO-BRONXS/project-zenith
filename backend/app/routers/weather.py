"""Weather observation API router."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.config import settings
from app.schemas.response import APIResponse
from app.schemas.weather import CurrentWeather
from app.services.weather_service import WeatherService, WeatherServiceError


router = APIRouter(prefix="/weather", tags=["weather"])


def get_weather_service() -> WeatherService:
    """Create the weather service dependency."""
    return WeatherService(base_url=settings.OPEN_METEO_URL)


@router.get(
    "/current",
    response_model=APIResponse[CurrentWeather],
    summary="Get current weather",
    description=(
        "Fetch current weather conditions from Open-Meteo for an observer "
        "latitude and longitude."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Current weather returned successfully."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid coordinates."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Open-Meteo is unavailable or returned invalid data.",
        },
    },
)
async def get_current_weather(
    request: Request,
    latitude: float = Query(..., ge=-90, le=90, description="Observer latitude."),
    longitude: float = Query(..., ge=-180, le=180, description="Observer longitude."),
    weather_service: WeatherService = Depends(get_weather_service),
) -> APIResponse[CurrentWeather]:
    """Return current weather for the requested observer location."""
    try:
        weather = await weather_service.get_current_weather(latitude, longitude)
    except WeatherServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        message="Current weather fetched successfully.",
        data=weather,
        request_id=getattr(request.state, "request_id", None),
    )
