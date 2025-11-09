import argparse
import contextlib
import logging
import pathlib

import fastapi
import uvicorn
from fastapi import staticfiles
from fastapi.middleware import cors

from emuse import __version__, common, database, endpoints, template

BASE_PATH = pathlib.Path(__file__).parent
LOGGER = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def fastapi_lifespan(*_args, **_kwargs):  # pragma: nocover
    """This is invoked by FastAPI for us to control startup and shutdown."""
    LOGGER.info('emuse v%s', __version__)
    template.initialize()
    async with database.lifespan() as pool:
        yield {'postgres': pool}
    LOGGER.debug('Shutdown complete')


def create_app() -> fastapi.FastAPI:
    """Wrap the top-level mess in a function as much as possible"""
    settings = common.Settings()
    app = fastapi.FastAPI(
        title='eMuse.org', lifespan=fastapi_lifespan, version=__version__
    )
    app.add_middleware(
        cors.CORSMiddleware,
        allow_origins=[settings.cors_origin],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        expose_headers=['Content-Range'],
    )
    app.include_router(endpoints.index_router)
    app.include_router(endpoints.login_router)
    app.include_router(endpoints.logout_router)
    app.mount(
        '/static',
        staticfiles.StaticFiles(directory=BASE_PATH / 'static'),
        name='static',
    )
    return app


def main():
    settings = common.Settings()
    parser = argparse.ArgumentParser(prog='eMuse')
    parser.add_argument(
        '--verbose', action='store_true', default=settings.debug
    )
    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {__version__}'
    )
    args = parser.parse_args()
    app = create_app()
    try:
        uvicorn.run(
            app,
            host='0.0.0.0',  # noqa: S104
            port=8000,
            forwarded_allow_ips='10.0.0.0/8',
            log_config=common.log_config(args.verbose),
            proxy_headers=True,
            headers=[('Server', f'emuse/{__version__}')],
            date_header=True,
            server_header=False,
            ws='none',
        )
    except KeyboardInterrupt:
        LOGGER.info('Exiting due to user interrupt')
