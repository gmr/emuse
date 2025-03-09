import fastapi

from emuse import database, template

router = fastapi.APIRouter()


@router.get('/')
async def get_index() -> fastapi.Response:
    async with database.cursor() as cursor:
        await cursor.execute('SELECT count(*) FROM accounts')
        accounts = len(await cursor.fetchall())
        html = template.render('index.html.j2',
                               title='Home',
                               accounts=accounts)
    return fastapi.Response(content=html, media_type='text/html')
