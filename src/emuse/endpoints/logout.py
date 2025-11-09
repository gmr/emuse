import uuid

import fastapi
from fastapi import responses

from emuse import session

router = fastapi.APIRouter()


@router.get('/logout', dependencies=[fastapi.Depends(session.cookie())])
async def logout(
    response: responses.Response,
    session_id: uuid.UUID = fastapi.Depends(session.cookie()),
) -> responses.RedirectResponse:
    await session.delete(response, session_id)
    return responses.RedirectResponse('/')
