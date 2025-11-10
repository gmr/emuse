import datetime
import uuid

import fastapi
import pydantic
from fastapi import responses

from emuse import database, models, session, turnstile

router = fastapi.APIRouter()


class Credentials(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: pydantic.SecretStr
    turnstile_token: str = pydantic.Field(
        min_length=1, description='CloudFlare Turnstile verification token'
    )


class PublicAccount(pydantic.BaseModel):
    """Account data safe for public consumption (excludes password/salt)"""

    id: uuid.UUID
    signup_at: datetime.datetime
    last_login_at: datetime.datetime | None
    first_name: str
    surname: str
    display_name: str
    email: pydantic.EmailStr
    date_of_birth: datetime.date | None
    locale: str
    timezone: str
    activated: bool
    locked: bool
    memorial: bool
    administrator: bool


@router.post('/api/login')
async def login(
    credentials: Credentials,
    postgres: database.InjectConnection,
    response: responses.Response,
    fastapi_request: fastapi.Request,
) -> PublicAccount:
    # Verify Turnstile token before attempting authentication
    client_ip = fastapi_request.client.host if fastapi_request.client else None
    if not await turnstile.verify_token(
        credentials.turnstile_token, client_ip
    ):
        raise fastapi.HTTPException(
            status_code=400,
            detail='CAPTCHA verification failed. Please try again.',
        )

    result = await models.Account.authenticate(
        postgres, credentials.email, credentials.password.get_secret_value()
    )
    if isinstance(result, models.Account):
        # Validate account status
        if not result.activated:
            raise fastapi.HTTPException(
                status_code=403,
                detail='Please verify your email address before logging in',
            )
        if result.locked:
            raise fastapi.HTTPException(
                status_code=403,
                detail='This account has been locked. Please contact support.',
            )
        if result.memorial:
            raise fastapi.HTTPException(
                status_code=403,
                detail='This is a memorial account and cannot be accessed',
            )
        await session.create(response, result.id)
        return PublicAccount(**result.model_dump(exclude={'password', 'salt'}))
    raise fastapi.HTTPException(
        status_code=403, detail='Invalid email or password'
    )
