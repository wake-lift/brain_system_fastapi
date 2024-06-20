from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import templates
from app.core.db import get_async_session
from app.crud.brain_system import get_bought_in_products
from app.pages.utils import create_bom_file


router = APIRouter(
    prefix='/brain_system',
    tags=['Базовые страницы сайта',]
)


@router.get('/operating-principle/')
async def operating(request: Request):
    return templates.TemplateResponse(
        request=request, name='/brain_system/operating_principle.html'
    )


@router.get('/electric-schematics/')
async def circuit(request: Request):
    return templates.TemplateResponse(
        request=request, name='/brain_system/circuit.html'
    )


@router.get('/pcb/')
async def pcb(request: Request):
    return templates.TemplateResponse(
        request=request, name='/brain_system/pcb.html'
    )


@router.get('/printed-parts/')
async def printed(request: Request):
    return templates.TemplateResponse(
        request=request, name='/brain_system/printed_parts.html'
    )


@router.get('/bought-in-products/')
async def bought(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    context = {'product_list': await get_bought_in_products(session)}
    return templates.TemplateResponse(
        request=request,
        name='/brain_system/bought_in_products.html',
        context=context
    )


@router.get('/export_model_to_ods/')
async def export_model_to_ods(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    output = await create_bom_file(session)
    output.seek(0)
    headers = {
        'Content-Disposition': 'attachment; filename=brain_system_BOM.ods'
    }
    return StreamingResponse(output, headers=headers)


@router.get('/firmware/')
async def firmware(request: Request):
    return templates.TemplateResponse(
        request=request, name='/brain_system/firmware.html'
    )
