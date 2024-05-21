from fastapi import FastAPI

from app.api.questions import router as questions_router
from app.api.users import router as users_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description
)

app.include_router(questions_router)
app.include_router(users_router)
