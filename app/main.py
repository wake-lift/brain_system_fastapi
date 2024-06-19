from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.questions import router as questions_router
from app.api.users import router as users_router
from app.core.config import settings
from app.pages.common_pages import router as common_pages_router
from app.pages.brain_system import router as brain_system_router
from app.pages.questions import router as questions_router

app_api = FastAPI(
    title=settings.app_api_title,
    description=settings.app_api_description
)

app_api.include_router(questions_router)
app_api.include_router(users_router)

app_pages = FastAPI(
    title=settings.app_pages_title,
    description=settings.app_pages_description

)

app_pages.mount(
    '/static',
    StaticFiles(directory=settings.static_dir), name='static'
)

app_pages.include_router(common_pages_router)
app_pages.include_router(brain_system_router)
app_pages.include_router(questions_router)
