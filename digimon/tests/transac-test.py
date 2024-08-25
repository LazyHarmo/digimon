import pytest
import pytest_asyncio
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

@pytest_asyncio.fixture(name="item1")
async def example_item(session: models.AsyncSession, user1: models.DBUser, merchant1: models.DBMerchant) -> models.DBItem:
    item = models.DBItem(
        name="Test Item",
        description="A test item",
        price=10.0,
        merchant_id=merchant1.id,
        user_id=user1.id
    )

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

@pytest_asyncio.fixture(name="merchant1")
async def example_merchant(session: models.AsyncSession, user1: models.DBUser) -> models.DBMerchant:
    merchant = models.DBMerchant(
        name="Test Merchant",
        description="A test merchant",
        tax_id="1234567890123",
        user_id=user1.id
    )

    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant

@pytest_asyncio.fixture(name="user1")
async def example_user(session: models.AsyncSession) -> models.DBUser:
    user = models.DBUser(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword"  # You should use a proper hashed password in real scenarios
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest_asyncio.fixture(name="token_user1")
async def example_token(user1: models.DBUser) -> models.Token:
    # Generate a fake token for testing
    return models.Token(
        access_token="test-access-token",
        token_type="Bearer",
        user_id=user1.id
    )

# Test cases

@pytest.mark.asyncio
async def test_create_transaction(
    client: AsyncClient, token_user1: models.Token, item1: models.DBItem
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "amount": 20,
        "item_id": item1.id
    }

    response = await client.post("/transactions", json=payload, headers=headers)
    
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 20
    assert data["item_id"] == item1.id
    assert "id" in data

@pytest.mark.asyncio
async def test_read_transaction(
    client: AsyncClient, transaction1: models.DBTransaction, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.get(f"/transactions/{transaction1.id}", headers=headers)
    
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction1.id
    assert data["amount"] == transaction1.amount
    assert data["item_id"] == transaction1.item_id

@pytest.mark.asyncio
async def test_update_transaction(
    client: AsyncClient, transaction1: models.DBTransaction, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "amount": 100,
        "item_id": transaction1.item_id
    }

    response = await client.put(f"/transactions/{transaction1.id}", json=payload, headers=headers)
    
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100
    assert data["item_id"] == transaction1.item_id

@pytest.mark.asyncio
async def test_delete_transaction(
    client: AsyncClient, transaction1: models.DBTransaction, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(f"/transactions/{transaction1.id}", headers=headers)
    
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    assert response.json() == {"message": "delete success"}