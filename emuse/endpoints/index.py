import fastapi

from emuse import database, models, template

router = fastapi.APIRouter()


@router.get('/')
async def get_index(postgres: database.InjectConnection) -> fastapi.Response:
    async with database.cursor(postgres, models.Account) as cursor:
        await cursor.execute('SELECT * FROM v1.accounts')
        accounts = await cursor.fetchall()
        html = template.render('index.html.j2',
                               title='Home',
                               accounts=accounts)
    return fastapi.Response(content=html, media_type='text/html')
