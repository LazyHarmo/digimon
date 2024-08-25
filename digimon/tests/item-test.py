from httpx import AsyncClient
from digimon import models
import pytest

@pytest.mark.asyncio
async def test_no_permission_create_item(
    client: AsyncClient, user1: models.DBUser, merchant1: models.DBMerchant
):
    payload = {"name": "item1", "description": "Item description", "price": 10.0, "merchant_id": merchant1.id}
    response = await client.post("/items", json=payload)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, token_user1: models.Token, merchant1: models.DBMerchant):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "name": "item1",
        "description": "Item description",
        "price": 10.0,
        "merchant_id": merchant1.id
    }
    
    # Print payload and headers for debugging
    print("Headers:", headers)
    print("Payload:", payload)
    
    response = await client.post("/items", json=payload, headers=headers)
    
    # Print response status and content for debugging
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json())
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["price"] == payload["price"]
    assert data["merchant_id"] == payload["merchant_id"]
    assert data["id"] > 0


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient, item_user1: models.DBItem, token_user1: models.Token):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.get(f"/items/{item_user1.id}", headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == item_user1.id
    assert data["name"] == item_user1.name

@pytest.mark.asyncio
async def test_update_item(client: AsyncClient, token_user1: models.Token):
    item_id = 1
    update_response = await client.put(
        f"/items/{item_id}",
        json={
            "name": "Updated Item Name",
            "description": "Updated description.",
            "price": 150.0,
            "tax": 15.0,
            "merchant_id": 1,
            "user_id": token_user1.user_id
        },
        headers={"Authorization": f"Bearer {token_user1.access_token}"}
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == item_id
    assert data["name"] == "Updated Item Name"
    assert data["description"] == "Updated description."
    assert data["price"] == 150.0
    assert data["tax"] == 15.0


@pytest.mark.asyncio
async def test_delete_item(
    client: AsyncClient, item_user1: models.DBItem, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(f"/items/{item_user1.id}", headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "delete success"

    # Verify item is deleted
    response = await client.get(f"/items/{item_user1.id}", headers=headers)
    assert response.status_code == 404
