import datetime

import fastapi
import pydantic
from pydantic_extra_types import timezone_name

from emuse import database, email, models

router = fastapi.APIRouter()


class SignupRequest(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: pydantic.SecretStr
    first_name: str = pydantic.Field(min_length=1, max_length=100)
    surname: str = pydantic.Field(min_length=1, max_length=100)
    display_name: str = pydantic.Field(min_length=1, max_length=100)
    date_of_birth: datetime.date
    locale: str = pydantic.Field(
        default='en_US', pattern=r'^[a-z]{2}_[A-Z]{2}$'
    )
    timezone: timezone_name.TimeZoneName = 'UTC'


class SignupResponse(pydantic.BaseModel):
    message: str
    email: pydantic.EmailStr


@router.post('/api/signup')
async def signup(
    request: SignupRequest, postgres: database.InjectConnection
) -> SignupResponse:
    """Register a new user account and send verification email."""

    # Check if email already exists
    async with database.cursor(postgres) as cursor:
        await cursor.execute(
            'SELECT id FROM v1.accounts WHERE email = %(email)s',
            {'email': str(request.email)},
        )
        if cursor.rowcount > 0:
            raise fastapi.HTTPException(
                status_code=400, detail='Email already registered'
            )

    # Create account
    account = models.Account(
        email=request.email,
        password=pydantic.SecretStr(''),  # Will be set below
        first_name=request.first_name,
        surname=request.surname,
        display_name=request.display_name,
        date_of_birth=request.date_of_birth,
        locale=request.locale,
        timezone=request.timezone,
        activated=False,  # Requires email verification
    )

    # Set password with proper hashing
    account.set_password(request.password.get_secret_value())

    # Save account to database
    await account.save(postgres)

    # Send verification email
    await email.send_verification_email(
        postgres, account.id, account.email, account.first_name
    )

    return SignupResponse(
        message=(
            'Account created successfully. '
            'Please check your email to verify your account.'
        ),
        email=account.email,
    )
