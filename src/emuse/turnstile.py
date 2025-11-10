"""CloudFlare Turnstile verification."""

import logging

import httpx
import pydantic
import pydantic_settings

LOGGER = logging.getLogger(__name__)


class _Settings(pydantic_settings.BaseSettings):
    model_config = {
        'case_sensitive': False,
        'env_file': '.env',
        'env_prefix': 'TURNSTILE_',
        'extra': 'ignore',
    }

    site_key: str
    secret_key: str


class TurnstileResponse(pydantic.BaseModel):
    """Response from Turnstile verification API."""

    success: bool
    challenge_ts: str | None = None
    hostname: str | None = None
    error_codes: list[str] = pydantic.Field(
        default_factory=list, alias='error-codes'
    )
    action: str | None = None
    cdata: str | None = None


async def verify_token(token: str, remote_ip: str | None = None) -> bool:
    """Verify a Turnstile token with CloudFlare.

    Args:
        token: The Turnstile response token from the client
        remote_ip: Optional IP address of the user for additional validation

    Returns:
        True if the token is valid, False otherwise

    """
    settings = _Settings()

    data = {'secret': settings.secret_key, 'response': token}
    if remote_ip:
        data['remoteip'] = remote_ip

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://challenges.cloudflare.com/turnstile/v0/siteverify',
                data=data,
                timeout=10.0,
            )
            response.raise_for_status()

            result = TurnstileResponse(**response.json())

            if not result.success:
                LOGGER.warning(
                    'Turnstile verification failed: %s', result.error_codes
                )
                return False

            LOGGER.debug('Turnstile verification successful')
            return True

    except httpx.HTTPError as exc:
        LOGGER.exception('Turnstile verification request failed: %s', exc)
        return False
    except Exception as exc:
        LOGGER.exception(
            'Unexpected error during Turnstile verification: %s', exc
        )
        return False
