from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Annotated
from sqlmodel import Field, SQLModel, Session, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/items", tags=["items"])

SIZE_PER_PAGE = 50

@router.get("")
async def read_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.ItemList:
    query = select(models.DBItem).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    result = await session.exec(query)
    items = result.all()

    total_items_query = select(func.count(models.DBItem.id))
    total_result = await session.exec(total_items_query)
    total_items = total_result.one()

    page_count = math.ceil(total_items / SIZE_PER_PAGE)

    return models.ItemList.model_validate(
        dict(items=items, page_count=page_count, page=page, size_per_page=SIZE_PER_PAGE)
    )

@router.post("")
async def create_item(
    item: models.CreatedItem,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Item | None:
    dbitem = models.DBItem.model_validate(item)  # Use model_validate
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)
    return models.Item.model_validate(dbitem)  # Use model_validate

@router.get("/{item_id}")
async def read_item(
    item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Item:
    db_item = await session.get(models.DBItem, item_id)
    if db_item:
        return models.Item.model_validate(db_item)  # Use model_validate
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item: models.UpdatedItem,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Item:
    data = item.model_dump()  # Use model_dump
    db_item = await session.get(models.DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return models.Item.model_validate(db_item)  # Use model_validate

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_item = await session.get(models.DBItem, item_id)
    await session.delete(db_item)
    await session.commit()

    return dict(message="delete success")
