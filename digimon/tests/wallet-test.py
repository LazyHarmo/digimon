from httpx import AsyncClient
from digimon import models
import pytest

@pytest.mark.asyncio
async def test_no_permission_create_wallet(
    client: AsyncClient, user1: models.DBUser
):
    payload = {"balance": 1000, "user_id": user1.id}
    response = await client.post("/wallets", json=payload)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_wallet(client: AsyncClient, token_user1: models.Token):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {"balance": 1000}
    response = await client.post("/wallets", json=payload, headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["balance"] == payload["balance"]
    assert data["user_id"] == token_user1.user_id
    assert data["id"] > 0

@pytest.mark.asyncio
async def test_get_wallet(client: AsyncClient, wallet_user1: models.DBWallet, token_user1: models.Token):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.get("/wallets/me", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == wallet_user1.id
    assert data["balance"] == wallet_user1.balance

@pytest.mark.asyncio
async def test_add_wallet_balance(
    client: AsyncClient, wallet_user1: models.DBWallet, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = 500
    response = await client.put(f"/wallets/balance/{payload}", headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["balance"] == wallet_user1.balance + payload

@pytest.mark.asyncio
async def test_delete_wallet(
    client: AsyncClient, wallet_user1: models.DBWallet, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete("/wallets/me", headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert "delete success" in data["message"]

@pytest.mark.asyncio
async def test_create_wallet_without_auth(client: AsyncClient):
    payload = {"balance": 1000}
    response = await client.post("/wallets", json=payload)

    assert response.status_code == 401

