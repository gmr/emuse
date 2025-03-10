import argparse
import contextlib
import logging
import pathlib

import fastapi
import uvicorn
from fastapi import staticfiles
from fastapi.middleware import cors

from emuse import __version__, common, config, database, endpoints

BASE_PATH = pathlib.Path(__file__).parent
LOGGER = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def fastapi_lifespan(*_args, **_kwargs):  # pragma: nocover
    """This is invoked by FastAPI for us to control startup and shutdown."""
    LOGGER.info('emuse v%s Starting Up', __version__.version)
    await database.open_pool()
    yield
    await database.close_pool()
    LOGGER.info('Shutdown complete')


def create_app() -> fastapi.FastAPI:
    """Wrap the top-level mess in a function as much as possible"""
    app = fastapi.FastAPI(title='eMuse.org', lifespan=fastapi_lifespan)
    app.add_middleware(cors.CORSMiddleware,
                       allow_origins=[config.env_vars.get('cors_origin', '*')],
                       allow_credentials=True,
                       allow_methods=['*'],
                       allow_headers=['*'],
                       expose_headers=['Content-Range'])
    app.include_router(endpoints.index_router)
    app.mount('/static',
              staticfiles.StaticFiles(directory=BASE_PATH / 'static'),
              name='static')
    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        action='store_true',
                        default=config.env_vars.get('debug', False) == '1')
    parser.add_argument('--version')
    args = parser.parse_args()
    app = create_app()
    common.configure_logfire(app)
    try:
        uvicorn.run(
            app,
            host='0.0.0.0',  # noqa: S104
            port=8000,
            forwarded_allow_ips='10.0.0.0/8',
            log_config=common.log_config(args.verbose),
            proxy_headers=True,
            headers=[('Server', f'emuse/{__version__.version}')],
            date_header=True,
            server_header=False,
            ws='none')
    except KeyboardInterrupt:
        LOGGER.info('Exiting due to user interrupt')
