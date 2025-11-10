import fastapi

from emuse import database, models, session
from emuse.endpoints.login import PublicAccount

router = fastapi.APIRouter()


@router.get('/api/me')
async def me(
    postgres: database.InjectConnection,
    session_data: session.SessionData = fastapi.Depends(
        session.Session.get_instance().verifier
    ),
) -> PublicAccount:
    """Get current authenticated user account information."""
    account = await models.Account.get(postgres, session_data.account_id)
    if not account:
        raise fastapi.HTTPException(
            status_code=401, detail='Account not found'
        )

    return PublicAccount(**account.model_dump(exclude={'password', 'salt'}))
