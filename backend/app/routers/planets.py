"""Planetary observation API router."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import settings
from app.schemas.planet import PlanetPositions
from app.schemas.response import APIResponse
from app.services.planet_service import PlanetService, PlanetServiceError


router = APIRouter(prefix="/planets", tags=["planets"])


def get_planet_service() -> PlanetService:
    """Create the planet service dependency."""
    return PlanetService(endpoint=settings.NASA_HORIZONS_URL)


@router.get(
    "/current",
    response_model=APIResponse[PlanetPositions],
    summary="Get current planetary positions",
    description=(
        "Fetch current Earth-relative vector positions for the Moon, Mercury, "
        "Venus, Mars, Jupiter, and Saturn from NASA Horizons."
    ),
    responses={
        status.HTTP_200_OK: {"description": "Current planetary positions returned successfully."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "NASA Horizons is unavailable or returned invalid data.",
        },
    },
)
async def get_current_planet_positions(
    request: Request,
    planet_service: PlanetService = Depends(get_planet_service),
) -> APIResponse[PlanetPositions]:
    """Return current positions for supported Solar System bodies."""
    try:
        positions = await planet_service.get_current_positions()
    except PlanetServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        message="Current planetary positions fetched successfully.",
        data=positions,
        request_id=getattr(request.state, "request_id", None),
    )
