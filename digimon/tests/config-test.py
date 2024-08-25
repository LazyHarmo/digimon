import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from typing import Any, Dict, Optional
from pydantic_settings import SettingsConfigDict
from digimon import models, config, main, security
import pytest
import pytest_asyncio
import pathlib
import datetime
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.recreate_table())

    yield app


@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:

    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username,
        password=password,
        email="test@test.com",
        first_name="Firstname",
        last_name="lastname",
        last_login_date=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    await user.set_password(password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> dict:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user1
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user.last_login_date,
        user_id=user.id,
    )


@pytest_asyncio.fixture(name="merchant_user1")
async def example_merchant_user1(
    session: models.AsyncSession, user1: models.DBUser
) -> models.DBMerchant:
    name = "merchant1"

    query = await session.exec(
        models.select(models.DBMerchant)
        .where(models.DBMerchant.name == name, models.DBMerchant.user_id == user1.id)
        .limit(1)
    )
    merchant = query.one_or_none()
    if merchant:
        return merchant

    merchant = models.DBMerchant(
        name=name, user=user1, decription="Merchant Description", tax_id="0000000000000"
    )

    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant

@pytest_asyncio.fixture(name="wallet_user1")
async def fixture_wallet_user1(
    session: models.AsyncSession, user1: models.DBUser
) -> models.DBWallet:
    # Define a unique balance and user ID for the wallet
    balance = 1000.0

    # Query to check if the wallet already exists for the user
    query = await session.exec(
        models.select(models.DBWallet)
        .where(models.DBWallet.user_id == user1.id)
        .limit(1)
    )
    wallet = query.one_or_none()
    
    # If wallet exists, return it
    if wallet:
        return wallet

    # If not, create a new wallet
    wallet = models.DBWallet(
        balance=balance, user=user1
    )

    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
    return wallet


@pytest_asyncio.fixture(name="item_user1")
async def example_item_user1(
    session: models.AsyncSession, merchant1: models.DBMerchant, user1: models.DBUser
) -> models.DBItem:
    name = "item1"

    query = await session.exec(
        models.select(models.DBItem)
        .where(models.DBItem.name == name, models.DBItem.merchant_id == merchant1.id)
        .limit(1)
    )
    item = query.one_or_none()
    if item:
        return item

    item = models.DBItem(
        name=name,
        description="Item description",
        price=10.0,
        merchant_id=merchant1.id,
        user_id=user1.id
    )

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

@pytest_asyncio.fixture(name="merchant1")
async def example_merchant1(
    session: models.AsyncSession, user1: models.DBUser
) -> models.DBMerchant:
    name = "merchant1"
    
    query = await session.exec(
        models.select(models.DBMerchant)
        .where(models.DBMerchant.name == name, models.DBMerchant.user_id == user1.id)
        .limit(1)
    )
    merchant = query.one_or_none()
    
    if merchant:
        return merchant

    merchant = models.DBMerchant(
        name=name, 
        description="Merchant Description", 
        tax_id="0000000000000",
        user_id=user1.id
    )
    
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant

import pytest
from httpx import AsyncClient
from datetime import datetime
from digimon import models

@pytest_asyncio.fixture(name="transaction1")
async def example_transaction(
    session: models.AsyncSession, user1: models.DBUser, item1: models.DBItem
) -> models.DBTransaction:
    transaction = models.DBTransaction(
        amount=100,
        item_id=item1.id,
        user_id=user1.id,
        transaction_date=datetime.utcnow()
    )

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction
