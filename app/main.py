from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import CSRFProtectMiddleware

from app.api.common_endpoints import router as common_endpints_router
from app.api.questions import router as api_questions_router
from app.api.users import router as users_router
from app.core.config import settings, lifespan, limiter
from app.pages.common_pages import router as common_pages_router
from app.pages.brain_system import router as brain_system_router
from app.pages.error_handlers import custom_error_handlers
from app.pages.questions import router as pages_questions_router


app_api = FastAPI(
    title=settings.app_api_title,
    description=settings.app_api_description,
    lifespan=lifespan
)
app_api.state.limiter = limiter
app_api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app_api.include_router(api_questions_router)
app_api.include_router(users_router)
app_api.include_router(common_endpints_router)


app_pages = FastAPI(
    title=settings.app_pages_title,
    description=settings.app_pages_description,
    middleware=[
        Middleware(SessionMiddleware,
                   secret_key=settings.session_middleware_secret_key),
        Middleware(CSRFProtectMiddleware,
                   csrf_secret=settings.csrf_middleware_secret_key),
    ],
    exception_handlers=custom_error_handlers,
    docs_url=None,
    redoc_url=None,
)
app_pages.state.limiter = limiter

app_pages.mount(
    '/static',
    StaticFiles(directory=settings.static_dir), name='static'
)

app_pages.include_router(common_pages_router)
app_pages.include_router(brain_system_router)
app_pages.include_router(pages_questions_router)
