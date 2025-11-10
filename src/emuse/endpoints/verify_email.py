import fastapi
import pydantic

from emuse import database, email, models

router = fastapi.APIRouter()


class VerifyEmailResponse(pydantic.BaseModel):
    success: bool
    message: str


@router.get('/api/verify-email/{token}')
async def verify_email(
    token: str, postgres: database.InjectConnection
) -> VerifyEmailResponse:
    """Verify email address using the token from the verification email."""

    # Verify token and get account ID
    account_id = await email.verify_token(postgres, token)

    if not account_id:
        raise fastapi.HTTPException(
            status_code=400, detail='Invalid or expired verification token'
        )

    # Activate the account
    account = await models.Account.get(postgres, account_id)
    if not account:
        raise fastapi.HTTPException(
            status_code=404, detail='Account not found'
        )

    if account.activated:
        return VerifyEmailResponse(
            success=True, message='Email already verified'
        )

    account.activated = True
    await account.save(postgres)

    return VerifyEmailResponse(
        success=True,
        message='Email verified successfully! You can now log in.',
    )
