import pytest 
from app import app, inventory_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        inventory_db.clear()
        inventory_db.append({
            "id": "1",
            "barcode": "3017624010701",
            "status": 1,
            "product": {
                "product_name": "Organic Almond Milk",
                "brands": "Silk",
                "ingredients_text": "Filtered water, almonds, cane sugar"
            },
            "price": 3.99,
            "stock": 45
        })
        yield client

def test_get_all_inventory(client):
    response = client.get('/inventory')
    assert response.status_code == 200
    assert len(response.get_json()) == 1

def test_get_single_item_success(client):
    response = client.get('/inventory/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data["barcode"] == "3017624010701"

def test_get_single_item_not_found(client):
    response = client.get('/inventory/999')
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_add_inventory_item_fallback(client):
    new_item_payload = {
        "barcode": "999999999",
        "price": 1.50,
        "stock": 10,
        "product_name": "Test Soda",
        "brands": "Test Brand",
        "ingredients_text": "Carbonated water, corn syrup"
    }
    response = client.post('/inventory', json=new_item_payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == "2"
    assert data["product"]["product_name"] == "Test Soda"

def test_patch_inventory_item(client):
    update_payload = {"price": 4.50, "stock": 50}
    response = client.patch('/inventory/1', json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 4.50
    assert data["stock"] == 50

def test_delete_inventory_item(client):
    response = client.delete('/inventory/1')
    assert response.status_code == 200
    check_response = client.get('/inventory/1')
    assert check_response.status_code == 404
