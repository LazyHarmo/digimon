from fastapi import APIRouter, HTTPException, Depends, Query

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, Session, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/transactions" , tags=["transactions"])

SIZE_PER_PAGE = 50


@router.get("")
async def read_transactions(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.TransactionList:

    result = await session.exec(
        select(models.DBTransaction).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    transactions = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBTransaction.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    print("page_count", page_count)
    print("transactions", transactions)
    return models.TransactionList.from_orm(
        dict(transactions=transactions, page_count=page_count, page=page, size_per_page=SIZE_PER_PAGE)
    )


@router.post("")
async def create_transaction(
    transaction: models.CreatedTransaction,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Transaction | None:
    # Query to find the wallet based on the foreign key relationship
    wallet = await session.get(models.Wallet, current_user.id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Query to find the item based on the foreign key relationship
    item = await session.get(models.Item, transaction.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if the wallet balance is sufficient
    if wallet.balance < item.price:
        raise HTTPException(status_code=400, detail="Not enough money")

    # Update the wallet balance
    wallet.balance -= item.price
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)

    # Create and add the transaction
    db_transaction = models.DBTransaction(
        amount=transaction.amount,
        item_id=transaction.item_id,
        user_id=current_user.id,
    )
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)
    return models.Transaction.from_orm(db_transaction)

   


@router.get("/{transaction_id}")
async def read_transaction(
    transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Transaction:
    db_transaction = await session.get(models.DBTransaction, transaction_id)
    if db_transaction:
        return models.Transaction.from_orm(db_transaction)

    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_transaction = await session.get(models.DBTransaction, transaction_id)
    await session.delete(db_transaction)
    await session.commit()

    return dict(message="delete success")
