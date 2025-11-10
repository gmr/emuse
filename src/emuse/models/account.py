import base64
import datetime
import hashlib
import logging
import os
import re
import secrets
import typing
import uuid

import pydantic
from pydantic_extra_types import timezone_name

from emuse import common, database

LOGGER = logging.getLogger(__name__)


def _generate_salt() -> pydantic.SecretBytes:
    """Generate a cryptographically secure random salt."""
    return pydantic.SecretBytes(os.urandom(16))


class Account(pydantic.BaseModel):
    """User Account"""

    model_config = pydantic.ConfigDict(extra='forbid')

    id: uuid.UUID = pydantic.Field(default_factory=common.new_uuid7)
    signup_at: datetime.datetime = pydantic.Field(
        default_factory=common.current_timestamp
    )
    last_login_at: datetime.datetime | None = None
    first_name: str
    surname: str
    display_name: str
    email: pydantic.EmailStr
    password: pydantic.SecretStr
    salt: pydantic.SecretBytes = pydantic.Field(default_factory=_generate_salt)
    date_of_birth: datetime.date | None = None
    locale: str = 'en_US'
    timezone: timezone_name.TimeZoneName = 'UTC'
    activated: bool = False
    locked: bool = False
    memorial: bool = False
    administrator: bool = False

    @classmethod
    async def authenticate(
        cls,
        postgres: database.ConnectionType,
        email: pydantic.EmailStr,
        password: str,
    ) -> typing.Self | None:
        """Authenticate an account, returning an account if successful."""
        async with database.cursor(postgres) as cursor:
            await cursor.execute(_AUTHENTICATE_SQL, {'email': str(email)})
            if not cursor.rowcount:
                # Perform dummy hash to maintain consistent timing
                dummy_salt = os.urandom(16)
                cls._hash_password(password, dummy_salt)
                return None
            data = await cursor.fetchone()
            value = cls._hash_password(password, data['salt'])
            # Use constant-time comparison to prevent timing attacks
            if secrets.compare_digest(value, data['password']):
                # Fetch full account and update last_login_at
                account = await cls.get(postgres, data['id'])
                if account:
                    account.last_login_at = common.current_timestamp()
                    await account.save(postgres)
                return account
            return None

    @classmethod
    async def get(
        cls, postgres: database.ConnectionType, account_id: uuid.UUID
    ) -> typing.Self | None:
        """Fetch an account by ID."""
        async with database.cursor(postgres) as cursor:
            await cursor.execute(_GET_SQL, {'id': account_id})
            if cursor.rowcount > 0:
                data = await cursor.fetchone()
                return cls(**data)
        return None

    async def save(self, postgres: database.ConnectionType) -> bool:
        """Save the model to the database"""
        LOGGER.debug('Saving account %s', self.id)
        async with database.cursor(postgres) as cursor:
            data = self.model_dump()
            data['password'] = self.password.get_secret_value()
            data['salt'] = self.salt.get_secret_value()
            await cursor.execute(_UPSERT_SQL, data)
            return cursor.rowcount > 0

    def set_password(self, password: str) -> None:
        """Set the password to the specified value"""
        hashed = self._hash_password(password, self.salt.get_secret_value())
        self.password = pydantic.SecretStr(hashed)

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> str:
        """Hash a password with a user-specific salt using PBKDF2.

        Args:
            password: The plaintext password to hash
            salt: Pre-existing salt, generates a new one if None

        Returns:
            A tuple of (encoded_salt, encoded_key) as strings

        """
        # Use PBKDF2 with 100,000 iterations and SHA-256
        key = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt, 100000
        )
        return base64.b64encode(key).decode('utf-8')


_GET_SQL = re.sub(
    r'\s+',
    ' ',
    """\
    SELECT id,
           signup_at,
           last_login_at,
           first_name,
           surname,
           display_name,
           email,
           password,
           salt,
           date_of_birth,
           locale,
           timezone,
           activated,
           locked,
           memorial,
           administrator
      FROM v1.accounts
     WHERE id = %(id)s
""",
)

_UPSERT_SQL = re.sub(
    r'\s+',
    ' ',
    """\
  INSERT INTO v1.accounts
              (id, signup_at, last_login_at, first_name, surname, display_name,
               email, password, salt, date_of_birth, locale, timezone,
               activated, locked, memorial, administrator)
       VALUES (%(id)s, %(signup_at)s, %(last_login_at)s, %(first_name)s,
               %(surname)s, %(display_name)s, %(email)s, %(password)s,
               %(salt)s, %(date_of_birth)s, %(locale)s, %(timezone)s,
               %(activated)s, %(locked)s, %(memorial)s, %(administrator)s)
  ON CONFLICT (id)
DO UPDATE SET signup_at = %(signup_at)s,
                 last_login_at = %(last_login_at)s,
                 first_name = %(first_name)s,
                 surname = %(surname)s,
                 display_name = %(display_name)s,
                 email = %(email)s,
                 password = %(password)s,
                 salt = %(salt)s,
                 date_of_birth = %(date_of_birth)s,
                 locale = %(locale)s,
                 timezone = %(timezone)s,
                 activated = %(activated)s,
                 locked = %(locked)s,
                 memorial = %(memorial)s,
                 administrator = %(administrator)s
""",
)

_AUTHENTICATE_SQL = re.sub(
    r'\s+',
    ' ',
    """\
SELECT id,
       salt,
       password
  FROM v1.accounts
 WHERE email = %(email)s;
""",
)
