import uuid

import fastapi

from emuse import database, models, session
from emuse.endpoints.login import PublicAccount

router = fastapi.APIRouter()


@router.get('/api/me')
async def me(
    postgres: database.InjectConnection,
    session_id: uuid.UUID = fastapi.Depends(session.cookie()),
) -> PublicAccount:
    """Get current authenticated user account information."""
    session_data = await session.Session().backend.read(str(session_id))
    if not session_data or not session_data.account_id:
        raise fastapi.HTTPException(
            status_code=401, detail='Not authenticated'
        )

    account = await models.Account.get(postgres, session_data.account_id)
    if not account:
        raise fastapi.HTTPException(
            status_code=401, detail='Account not found'
        )

    return PublicAccount(**account.model_dump(exclude={'password', 'salt'}))
