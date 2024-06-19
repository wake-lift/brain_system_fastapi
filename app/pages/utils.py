import io

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.brain_system import get_bought_in_products


async def create_bom_file(session: AsyncSession) -> io.BytesIO:
    products = await get_bought_in_products(session)
    products_list = []
    for product in products:
        product_dict = {
            'Название': product.name,
            'Входит в состав': product.unit.name,
            'Кол-во': product.quantity,
            'Тип': product.product_type,
            'Ссылки': '\n'.join(_.link for _ in product.links_for_product),
            'Комментарий': product.comment
        }
        products_list.append(product_dict)
    df = pd.DataFrame(products_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='odf') as doc:
        df.to_excel(doc, sheet_name='Bought-in poducts')
    return output
