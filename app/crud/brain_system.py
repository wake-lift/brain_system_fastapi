from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.brain_system import BoughtInProduct


async def get_bought_in_products(
    session: AsyncSession,
) -> Sequence[BoughtInProduct]:
    """Получает из БД набор данных по покупным деталям."""
    query = (
        select(BoughtInProduct)
        .options(
            joinedload(BoughtInProduct.unit),
            selectinload(BoughtInProduct.links_for_product)
        )
    )
    product_list = await session.scalars(query)
    return product_list
