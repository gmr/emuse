import fastapi
import pydantic
from fastapi import responses

from emuse import database, models, session

router = fastapi.APIRouter()


class Credentials(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: pydantic.SecretStr


@router.post('/login')
async def login(credentials: Credentials, postgres: database.InjectConnection,
                response: responses.Response) -> models.Account | None:
    result = await models.Account.authenticate(
        postgres, credentials.email, credentials.password.get_secret_value())
    if isinstance(result, models.Account):
        await session.create(response, result.id)
        return result
    raise fastapi.HTTPException(status_code=403, detail='Forbidden')
