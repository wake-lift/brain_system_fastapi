from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.pages.forms import FeedbackForm


async def add_feedback_to_db(
    form: FeedbackForm,
    session: AsyncSession,
) -> Feedback:
    """Создает новую запись в Базе."""
    feedback_obj = Feedback(
        name=form.name.data,
        email=form.email.data,
        feedback_text=form.feedback_text.data
    )
    session.add(feedback_obj)
    await session.commit()
    await session.refresh(feedback_obj)
    return feedback_obj
