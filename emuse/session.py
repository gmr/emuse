import logging
import typing
import uuid

import fastapi
import pydantic
import pydantic_settings
from fastapi_sessions import session_verifier
from fastapi_sessions.backends import implementations as backends
from fastapi_sessions.frontends import implementations as frontends

from emuse import common

LOGGER = logging.getLogger(__name__)


class _Settings(pydantic_settings.BaseSettings):
    model_config = {'env_prefix': 'cookie', 'case_sensitive': False}
    secret: str = 'secret'  # noqa: S105


class SessionData(pydantic.BaseModel):
    session_id: uuid.UUID
    account_id: uuid.UUID


class _Verifier(session_verifier.SessionVerifier[uuid.UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: backends.InMemoryBackend[uuid.UUID, SessionData],
        auth_http_exception: fastapi.HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


class Session:

    _instance: typing.Self | None = None

    def __init__(self):
        _settings = _Settings()
        self.backend = backends.InMemoryBackend[uuid.UUID, SessionData]()
        self.cookie_params = frontends.CookieParameters()
        self.cookie = frontends.SessionCookie(cookie_name="cookie",
                                              identifier="general_verifier",
                                              auto_error=True,
                                              secret_key=_settings.secret,
                                              cookie_params=self.cookie_params)
        self.verifier = _Verifier(identifier="general_verifier",
                                  auto_error=True,
                                  backend=self.backend,
                                  auth_http_exception=fastapi.HTTPException(
                                      status_code=403,
                                      detail='Invalid Session'))

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    async def create(self, response: fastapi.Response,
                     account_id: uuid.UUID) -> None:
        session_id = common.new_uuid7()
        data = SessionData(account_id=account_id, session_id=session_id)
        await self.backend.create(session_id, data)
        self.cookie.attach_to_response(response, session_id)

    async def delete(self, response: fastapi.Response,
                     session_id: uuid.UUID) -> None:
        await self.backend.delete(session_id)
        self.cookie.delete_from_response(response)


async def create(response: fastapi.Response, account_id: uuid.UUID) -> None:
    """Create the session cookie"""
    await Session.get_instance().create(response, account_id)


async def delete(response: fastapi.Response, session_id: uuid.UUID) -> None:
    """Delete the session cookie"""
    instance = Session.get_instance()
    await instance.delete(response, session_id)


def cookie() -> frontends.SessionCookie:
    """Return the session cookie object."""
    return Session.get_instance().cookie
