import random

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_wtf import csrf_protect

from app.core.config import limiter, templates
import app.core.constants as const
from app.core.db import get_async_session
from app.crud.questions_api import get_questions_by_list_order
from app.crud.questions_pages import (get_base_query,
                                      get_initial_random_question_set,
                                      get_random_package)
from app.elasticsearch.logic import ElasticSearchQuestion
from app.models.questions import Question
from app.pages.forms import RandomPackageForm, RandomQuestionForm

router = APIRouter(
    prefix='/questions',
    tags=['Базовые страницы сайта',]
)


@csrf_protect
@router.get('/random-qustions/')
@router.post('/random-qustions/')
@limiter.limit(const.GENERATE_QUESTIONS_THROTTLING_RATE)
async def random_questions(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    form = await RandomQuestionForm.from_formdata(request)
    context = {'form': form, 'form_is_valid': False}
    if request.method == 'POST':
        """Обработка запроса при отправке пользователем заполненной формы."""
        if await form.validate_on_submit():
            context['form_is_valid'] = True
            if form.full_text_search_pattern.data:
                es = ElasticSearchQuestion()
                search_result = es.search_questions(
                    form.full_text_search_pattern.data,
                    form.questions_quantity.data,
                    dict(
                        form.question_type.choices
                    ).get(form.question_type.data)
                )
                question_pk_list = es.get_questions_pk_list(search_result)
                questions = await get_questions_by_list_order(
                    question_pk_list, session
                )
            else:
                if form.search_pattern.data:
                    query = get_base_query(form.question_type.data).filter(
                        Question.question.contains(form.search_pattern.data)
                    )
                    questions = await session.execute(query)
                    questions = questions.all()
                else:
                    questions = await get_initial_random_question_set(
                        form.question_type.data, session
                    )
                questions_quantity = min(
                    form.questions_quantity.data,
                    len(questions)
                )
                questions = random.choices(questions, k=questions_quantity)
            context['questions'] = questions
    return templates.TemplateResponse(
        request=request,
        name='/questions/random_questions.html',
        context=context
    )


@csrf_protect
@router.get('/random-package/')
@router.post('/random-package/')
@limiter.limit(const.GENERATE_QUESTIONS_THROTTLING_RATE)
async def random_package(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    form = await RandomPackageForm.from_formdata(request)
    context = {'form': form, 'form_is_valid': False}
    if request.method == 'POST':
        if await form.validate_on_submit():
            context['form_is_valid'] = True
            random_package, random_package_name = await get_random_package(
                form.question_type.data, session
            )
            context['random_package'] = random_package
            context['random_package_name'] = random_package_name
    return templates.TemplateResponse(
        request=request,
        name='/questions/random_package.html',
        context=context
    )


@router.api_route('/telegram-bot/', methods=['GET', 'HEAD'])
@limiter.limit(const.BASE_THROTTLING_RATE)
async def tg_bot(request: Request):
    return templates.TemplateResponse(
        request=request, name='/questions/tg_bot.html'
    )


@router.api_route('/api/', methods=['GET', 'HEAD'])
@limiter.limit(const.BASE_THROTTLING_RATE)
async def api_info(request: Request):
    return templates.TemplateResponse(
        request=request, name='/questions/api_info.html'
    )
