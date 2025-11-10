import fastapi

from emuse import common, database, models, template

router = fastapi.APIRouter()


async def _render_index(postgres: database.InjectConnection) -> str:
    """Render the index HTML template."""
    settings = common.Settings()
    async with database.cursor(postgres, models.Account) as cursor:
        await cursor.execute('SELECT * FROM v1.accounts')
        accounts = await cursor.fetchall()
        return template.render(
            'index.html.j2',
            title='Home',
            accounts=accounts,
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
