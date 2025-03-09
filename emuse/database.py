import contextlib
import logging
import typing

import psycopg
import psycopg_pool
import yarl
from psycopg import rows

from emuse import config

LOGGER = logging.getLogger(__name__)

_url = yarl.URL(config.env_vars['postgres_url'])
_pool = psycopg_pool.AsyncConnectionPool(str(_url),
                                         kwargs={
                                             'autocommit': True,
                                             'row_factory': rows.dict_row
                                         },
                                         max_size=10,
                                         min_size=2,
                                         open=False)


async def open_pool() -> None:
    """Open the connection pool"""
    LOGGER.debug('Opening connection pool to %s', _url)
    await _pool.open(True, timeout=3.0)
    LOGGER.debug('Connection pool opened')


async def close_pool() -> None:
    """Close the connection pool"""
    if not _pool.closed:
        LOGGER.debug('Closing connection pool')
        await _pool.close()


@contextlib.asynccontextmanager
async def cursor(row_factory_class: typing.Generic | None =None) \
        -> typing.AsyncContextManager[psycopg.AsyncCursor]:
    """Get a cursor for Postgres."""
    kwargs = {}
    if row_factory_class:
        kwargs["row_factory"] = rows.class_row(row_factory_class)
    async with _pool.connection() as conn:
        async with conn.cursor(**kwargs) as value:
            yield value
