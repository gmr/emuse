import datetime
import re

import fastapi
import psycopg.errors
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

    @pydantic.field_validator('password')
    @classmethod
    def validate_password_strength(
        cls, v: pydantic.SecretStr
    ) -> pydantic.SecretStr:
        """Validate password meets complexity requirements."""
        password = v.get_secret_value()
        if len(password) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not re.search(r'[A-Z]', password):
            raise ValueError(
                'Password must contain at least one uppercase letter'
            )
        if not re.search(r'[a-z]', password):
            raise ValueError(
                'Password must contain at least one lowercase letter'
            )
        if not re.search(r'[0-9]', password):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValueError(
                'Password must contain at least one special character'
            )
        return v

    @pydantic.field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: datetime.date) -> datetime.date:
        """Validate user is at least 13 years old."""
        today = datetime.datetime.now(datetime.UTC).date()
        age = (
            today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        )
        if age < 13:
            raise ValueError('You must be at least 13 years old to register')
        if v > today:
            raise ValueError('Date of birth cannot be in the future')
        return v


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
    try:
        await account.save(postgres)
    except psycopg.errors.UniqueViolation:
        # Handle race condition where email was registered between
        # check and save
        raise fastapi.HTTPException(
            status_code=400, detail='Email already registered'
        ) from None

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
