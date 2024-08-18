from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

from . import users


class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    balance: float = 100.0
    user_id: int | None = 1

class CreatedWallet(BaseWallet):
    pass


class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int

class DBWallet(BaseWallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()
