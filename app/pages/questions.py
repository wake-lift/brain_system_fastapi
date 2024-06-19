from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.config import templates

router = APIRouter(
    prefix='/questions',
    tags=['Базовые страницы сайта',]
)


@router.get('/random-qustions/', response_class=HTMLResponse)
async def random_questions(request: Request):
    return 'random_questions'


@router.get('/random-package/', response_class=HTMLResponse)
async def random_package(request: Request):
    return 'random_package'


@router.get('/telegram-bot/', response_class=HTMLResponse)
async def tg_bot(request: Request):
    return 'tg_bot'


@router.get('/api/', response_class=HTMLResponse)
async def api_info(request: Request):
    return 'api_info'
