"""Turnstile configuration endpoint."""

import fastapi
import pydantic

from emuse import turnstile

router = fastapi.APIRouter()


class TurnstileConfig(pydantic.BaseModel):
    """Public Turnstile configuration."""

    site_key: str


@router.get('/api/turnstile/config')
async def get_turnstile_config() -> TurnstileConfig:
    """Get public Turnstile configuration (site key only)."""
    settings = turnstile._Settings()
    return TurnstileConfig(site_key=settings.site_key)
