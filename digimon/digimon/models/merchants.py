from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

from . import items


class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    tax_id: str | None = None


class CreatedMerchant(BaseMerchant):
    pass


class UpdatedMerchant(BaseMerchant):
    pass


class Merchant(BaseMerchant):
    id: int
    # items: items.Item


class DBMerchant(Merchant, SQLModel, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)
    # items: list["DBItem"] = Relationship(back_populates="merchant")


class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Merchant]
    page: int
    page_size: int
    size_per_page: int
