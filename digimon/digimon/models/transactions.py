from typing import Annotated
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

from . import users
from . import merchants
from . import wallets

class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sender: str
    receiver: str
    amount: float


class CreatedTransaction(BaseTransaction):
    pass


class Transaction(BaseTransaction):
    id: int
    merchant_id: int
    wallet_id: int
    item_id: int

class DBTransaction(Transaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: int = Field(default=None, foreign_key="merchants.id")
    wallet_id: int = Field(default=None, foreign_key="wallets.id")
    item_id: int = Field(default=None, foreign_key="items.id")


class Transaction_list(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int
