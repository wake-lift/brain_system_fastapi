from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_wtf import csrf_protect

from app.core.config import limiter, templates
import app.core.constants as const
from app.core.db import get_async_session
from app.crud.feedback import add_feedback_to_db
from app.pages.forms import FeedbackForm


router = APIRouter(
    prefix='',
    tags=['Базовые страницы сайта',]
)


@router.api_route('/', methods=['GET', 'HEAD'])
@limiter.limit(const.BASE_THROTTLING_RATE)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name='/common_pages/main.html'
    )


@router.api_route('/legal/', methods=['GET', 'HEAD'])
@limiter.limit(const.BASE_THROTTLING_RATE)
async def legal(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='/common_pages/legal.html',
    )


@csrf_protect
@router.api_route('/feedback/', methods=['GET', 'HEAD', 'POST'])
@limiter.limit(const.FEEDBACK_THROTTLING_RATE)
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
