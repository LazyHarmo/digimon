from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship
from . import merchants


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None
    merchant_id: int | None


class CreatedItem(BaseItem):
    pass


class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int
    merchant_id: int
    # merchant: merchants.Merchant


class DBItem(Item, SQLModel, table=True):
    __tablename__ = "items"
    id: int = Field(default=None, primary_key=True)
    merchant_id: int = Field(default=None, foreign_key="merchants.id")
    # merchant: merchants.DBMerchant | None = Relationship(back_populates="items")


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int
