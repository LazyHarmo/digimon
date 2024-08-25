from typing import Optional
import datetime
import pydantic
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

from . import users
from . import merchants
from . import items

class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    amount: int | None = 1
    merchant_id: int | None
    user_id: int | None = 1
    item_id: int | None = 1

class CreatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int
    transaction_date: datetime.datetime | None = pydantic.Field(
    json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
    
class DBTransaction(BaseTransaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: int = Field(default=None, primary_key=True)
    merchant_id: int = Field(default=None, foreign_key="merchants.id")
    merchant: merchants.DBMerchant = Relationship()

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()

    item_id: int = Field(default=None, foreign_key="items.id")
    item: items.DBItem | None = Relationship()

    transaction_date: datetime.datetime = Field(default_factory=datetime.datetime.now)

class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transactions: list[Transaction]
    page: int
    page_count: int
    size_per_page: int
