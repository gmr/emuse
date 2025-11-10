import datetime
import uuid

import fastapi
import pydantic
from fastapi import responses

from emuse import database, models, session

router = fastapi.APIRouter()


class Credentials(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: pydantic.SecretStr


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
) -> PublicAccount:
    result = await models.Account.authenticate(
        postgres, credentials.email, credentials.password.get_secret_value()
    )
    if isinstance(result, models.Account):
        await session.create(response, result.id)
        return PublicAccount(**result.model_dump(exclude={'password', 'salt'}))
    raise fastapi.HTTPException(status_code=403, detail='Forbidden')
