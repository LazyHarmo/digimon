from fastapi import APIRouter, HTTPException, Depends, Query

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, Session, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("/me")
async def get_wallet(
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],) -> models.Wallet:

    # Query to find the wallet based on the foreign key relationship
    result = await session.execute(
        select(models.DBWallet).where(models.DBWallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()

    if wallet:
        return models.Wallet.from_orm(wallet)

    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/balance/{balance}")
async def add_wallet_balance(
    balance: float,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Wallet:
    # Query to find the wallet based on the foreign key relationship
    result = await session.execute(
        select(models.DBWallet).where(models.DBWallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()

    if wallet:
        wallet.balance += balance

        await session.commit()
        await session.refresh(wallet)

        return models.Wallet.from_orm(wallet)

    raise HTTPException(status_code=404, detail="Wallet not found")



@router.post("")
async def create_wallet(
    wallet: models.CreatedWallet,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Wallet | None:
    dbwallet = models.DBWallet.model_validate(wallet)
    session.add(dbwallet)
    await session.commit()
    await session.refresh(dbwallet)

    return models.Wallet.from_orm(dbwallet)


@router.delete("/me")
async def delete_wallet(
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    
    # Query to find the wallet based on the foreign key relationship
    result = await session.execute(
        select(models.DBWallet).where(models.DBWallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()

    if wallet:
        db_wallet = await session.get(models.DBWallet, models.Wallet.from_orm(wallet).id)
        await session.delete(db_wallet)
        await session.commit()
        return dict(message="delete success")

    raise HTTPException(status_code=404, detail="Wallet not found")

