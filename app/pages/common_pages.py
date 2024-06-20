from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_wtf import csrf_protect

from app.core.config import templates
from app.core.db import get_async_session
from app.crud.feedback import add_feedback_to_db
from app.pages.forms import FeedbackForm


router = APIRouter(
    prefix='',
    tags=['Базовые страницы сайта',]
)


@router.get('/')
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name='/common_pages/main.html'
    )


@router.get('/legal/')
async def legal(request: Request):
    return templates.TemplateResponse(
        request=request, name='/common_pages/legal.html'
    )


@csrf_protect
@router.get('/feedback/')
@router.post('/feedback/')
async def feedback(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    form = await FeedbackForm.from_formdata(request)
    context = {'form': form}
    if request.method == 'POST':
        if await form.validate_on_submit():
            await add_feedback_to_db(form, session)
            context['form_saved'] = True
    else:
        context['form_saved'] = False
    return templates.TemplateResponse(
        request=request, name='/common_pages/feedback.html', context=context
    )
