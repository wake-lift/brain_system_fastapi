from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.config import templates

router = APIRouter(
    prefix='/brain_system',
    tags=['Базовые страницы сайта',]
)


@router.get('/operating-principle/', response_class=HTMLResponse)
async def operating(request: Request):
    return 'operating'


@router.get('/electric-schematics/', response_class=HTMLResponse)
async def circuit(request: Request):
    return 'circuit'


@router.get('/pcb/', response_class=HTMLResponse)
async def pcb(request: Request):
    return 'pcb'


@router.get('/printed-parts/', response_class=HTMLResponse)
async def printed(request: Request):
    return 'printed'


@router.get('/bought-in-products/', response_class=HTMLResponse)
async def bought(request: Request):
    return 'bought'


@router.get('/export_model_to_ods/', response_class=HTMLResponse)
async def export_model_to_ods(request: Request):
    return 'export_model_to_ods'


@router.get('/firmware//', response_class=HTMLResponse)
async def firmware(request: Request):
    return 'firmware'
