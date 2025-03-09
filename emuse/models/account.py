import datetime

import pydantic
import sqlmodel
from pydantic_extra_types import timezone_name, ulid

from emuse import common


class Account(sqlmodel.SQLModel, table=True):
    id: ulid.ULID | None = sqlmodel.Field(default=common.new_uuid7,
                                          primary_key=True)
    first_name: str
    surname: str
    display_name: str
    email: pydantic.EmailStr
    password: pydantic.SecretStr
    date_of_birth: datetime.date | None = None
    locale: str = sqlmodel.Field(default='en_US')
    timezone: timezone_name = sqlmodel.Field(default='UTC')
    activated: bool = False
    locked: bool = False
    memorial: bool = False
    administrator: bool = False
