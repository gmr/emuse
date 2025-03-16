import datetime

import pydantic
from pydantic_extra_types import timezone_name, ulid

from emuse import common


class Account(pydantic.BaseModel):
    """User Account"""
    model_config = pydantic.ConfigDict(extra='forbid')

    id: ulid.ULID = pydantic.Field(default=common.new_uuid7)
    signup_at: datetime.datetime = pydantic.Field(
        default_factory=common.current_timestamp)
    last_login_at: datetime.datetime | None = None
    first_name: str
    surname: str
    display_name: str
    email: pydantic.EmailStr
    password: pydantic.SecretStr
    date_of_birth: datetime.date | None = None
    locale: str = 'en_US'
    timezone: timezone_name.TimeZoneName = 'UTC'
    activated: bool = False
    locked: bool = False
    memorial: bool = False
    administrator: bool = False
