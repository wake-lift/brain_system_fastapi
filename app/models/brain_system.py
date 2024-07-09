from typing import List, Optional
from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class BoughtInProduct(Base):
    """Основная таблица покупных деталей."""
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    unit_id: Mapped[int | None] = mapped_column(ForeignKey('unit.id'))
    quantity: Mapped[int | None] = mapped_column(SmallInteger())
    product_type: Mapped[str | None] = mapped_column(String(128))
    comment: Mapped[str | None] = mapped_column(String(512))

    unit: Mapped[Optional['Unit']] = relationship(
        back_populates='bought_in_products', lazy='joined'
    )
    links_for_product: Mapped[List['ProductLink']] = relationship(
        back_populates='bought_in_product', lazy='joined'
    )

    def __str__(self):
        return self.name


class Unit(Base):
    """Таблица узлов, в которые входят покупные детали."""
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))

    bought_in_products: Mapped[List['BoughtInProduct'] | None] = relationship(
        back_populates='unit'
    )

    def __str__(self):
        return self.name


class ProductLink(Base):
    """Таблица ссылок на покупные детали в интернет-магазинах."""
    id: Mapped[int] = mapped_column(primary_key=True)
    bought_in_product_id: Mapped[int | None] = mapped_column(
        ForeignKey('boughtinproduct.id')
    )
    link: Mapped[str | None] = mapped_column(String(300))
    link_short_name: Mapped[str | None] = mapped_column(String(128))

    bought_in_product: Mapped[Optional['BoughtInProduct']] = relationship(
        back_populates='links_for_product'
    )

    def __str__(self):
        return self.link_short_name
