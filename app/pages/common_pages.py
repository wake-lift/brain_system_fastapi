from typing import Annotated
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.core.config import templates

router = APIRouter(
    prefix='',
    tags=['Базовые страницы сайта',]
)


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name='/common_pages/main.html'
    )


@router.get('/legal/', response_class=HTMLResponse)
async def legal(request: Request):
    return templates.TemplateResponse(
        request=request, name='/common_pages/legal.html'
    )


@router.get('/feedback/', response_class=HTMLResponse)
@router.post('/feedback/', response_class=HTMLResponse)
async def feedback(
    request: Request,
):
    print(request.method)
    return request.method
