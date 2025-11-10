import fastapi

from emuse import common, database, template

router = fastapi.APIRouter()


async def _render_index(_postgres: database.InjectConnection) -> str:
    """Render the index HTML template."""
    # Leave the _postgres connection as we're going to use it for real data
    # at some point in the development process when we add things to the
    # homepage
    settings = common.Settings()
    return await template.render_async(
        'index.html.j2',
        title='Home',
        debug=settings.debug,
        vite_dev_url=settings.vite_dev_url,
    )


@router.get('/')
async def get_index(postgres: database.InjectConnection) -> fastapi.Response:
    html = await _render_index(postgres)
    return fastapi.Response(content=html, media_type='text/html')


@router.get('/{full_path:path}')
async def spa_catchall(
    full_path: str, postgres: database.InjectConnection
) -> fastapi.Response:
    """Catch-all route to serve the SPA for any non-API route."""
    # Only serve HTML for routes that don't start with /api or /static
    if full_path.startswith('api/') or full_path.startswith('static/'):
        raise fastapi.HTTPException(status_code=404, detail='Not Found')

    html = await _render_index(postgres)
    return fastapi.Response(content=html, media_type='text/html')
