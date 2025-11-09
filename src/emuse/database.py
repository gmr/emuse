import contextlib
import logging
import typing
from collections import abc

import fastapi
import psycopg
import psycopg_pool
import pydantic
import pydantic_settings
from psycopg import rows

LOGGER = logging.getLogger(__name__)

CursorType = psycopg.AsyncCursor[rows.DictRow]
ConnectionType = psycopg.AsyncConnection[rows.DictRow]
ModelType = type[pydantic.BaseModel]
PoolType = psycopg_pool.AsyncConnectionPool[ConnectionType]


class _Settings(pydantic_settings.BaseSettings):
    url: pydantic.PostgresDsn = 'postgres://localhost/emuse'
    max_size: int = 10
    min_size: int = 2
    model_config = {'env_prefix': '_postgres', 'case_sensitive': False}


@contextlib.asynccontextmanager
async def lifespan() -> abc.AsyncIterator[psycopg_pool.AsyncConnectionPool]:
    settings = _Settings()  # type: ignore[call-arg]
    async with psycopg_pool.AsyncConnectionPool(
        settings.url.unicode_string(),
        min_size=settings.min_size,
        max_size=settings.max_size,
        configure=_configure,
        check=psycopg_pool.AsyncConnectionPool.check_connection,
    ) as pool:
        yield pool


async def _configure(conn: ConnectionType) -> None:
    await conn.set_autocommit(True)
    conn.prepare_threshold = None
    conn.row_factory = rows.dict_row


async def connection(
    request: fastapi.Request,
) -> abc.AsyncIterator[ConnectionType]:
    pool = typing.cast(PoolType, request.state.postgres)
    async with pool.connection(timeout=5.0) as conn:
        yield conn


InjectConnection = typing.Annotated[
    ConnectionType, fastapi.Depends(connection)
]


@contextlib.asynccontextmanager
async def cursor(
    conn: ConnectionType, row_factory_class: ModelType | None = None
) -> abc.AsyncGenerator[psycopg.AsyncCursor]:
    """Get a cursor for Postgres."""
    kwargs = {}
    if row_factory_class:
        kwargs['row_factory'] = rows.class_row(row_factory_class)
    async with conn.cursor(**kwargs) as value:
        yield value
