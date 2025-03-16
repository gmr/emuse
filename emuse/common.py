import datetime
import logging
import pathlib
import uuid
from logging import config as logging_config

import fastapi
import logfire
import psycopg
import pydantic_settings
import uuid_utils
import yaml


class Settings(pydantic_settings.BaseSettings):
    model_config = {'case_sensitive': False}

    debug: bool = False
    environment: str = 'development'
    cors_origin: str = '*'
    logfire_token: str | None = None
    sentry_dsn: str | None = None


class StatusEndpointFilter(logging.Filter):
    """Filter out /status endpoint requests from uvicorn logs."""
    def filter(self, record: logging.LogRecord) -> bool:
        if 'GET' in record.args and '/status' in record.args:
            return False
        return True


def configure_logfire(app: fastapi.FastAPI) -> None:  # pragma: nocover
    settings = Settings()
    if settings.logfire_token:
        logfire.configure(token=settings.logfire_token,
                          environment=settings.environment,
                          service_name='eMuse')
        logfire.instrument_fastapi(app,
                                   capture_headers=True,
                                   excluded_urls='^https?://[^/]+/status$')
        logfire.instrument_httpx()
        logfire.instrument_pydantic()
        logfire.instrument_psycopg(psycopg)


def log_config(verbose: bool = False) -> dict:
    with open(pathlib.Path(__file__).parent / 'log-config.yaml') as f:
        value = yaml.safe_load(f)
        value['filters'] = {'status_endpoint': {'()': StatusEndpointFilter}}
        value['handlers']['default']['filters'] = ['status_endpoint']
        if verbose:
            value['loggers']['emuse']['level'] = logging.DEBUG
            value['handlers']['default']['level'] = logging.DEBUG
    return value


def configure_logging(verbose: bool = False) -> None:  # pragma: nocover
    """Configure logging for the application."""
    logging_config.dictConfig(log_config(verbose))


def current_date() -> datetime.date:
    """Return the current date in UTC"""
    return current_timestamp().date()


def current_timestamp() -> datetime.datetime:
    """Return the current timestamp in UTC"""
    return datetime.datetime.now(datetime.UTC)


def new_uuid7() -> uuid.UUID:
    """Return a UUID object that will work with psycopg."""
    return uuid.UUID(str(uuid_utils.uuid7()))
