from fastapi import APIRouter

router = APIRouter(
    prefix='',
    tags=['Прочее',]
)


@router.api_route(
    '/',
    methods=['GET', 'HEAD'],
    summary='Приветственная страница API.'
)
async def api_root():
    """Главная страница API с приветствием."""
    return {
        'message': 'Welcome to BrainAPI!',
        'Swagger url': '/docs/',
        'ReDoc url': '/redoc/'
    }
