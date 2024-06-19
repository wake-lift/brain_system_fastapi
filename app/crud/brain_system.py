from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brain_system import BoughtInProduct, ProductLink, Unit


async def get_bought_in_products(
    session: AsyncSession,
) -> Sequence[BoughtInProduct]:
    """Получает из БД набор данных по покупным деталям."""
    query = (
        select(BoughtInProduct).
        join(Unit).
        join(ProductLink)
    )
    product_list = await session.execute(query)
    return product_list.scalars().unique().all()
