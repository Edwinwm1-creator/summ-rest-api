from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Simulated Database Storage (Global Array)
inventory_db = [
    {
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
    },
    {
        "id": "2",
        "barcode": "3017624010702",
        "status": 1,
        "product": {
            "product_name": "Organic Soy Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, soybeans, cane sugar"
        },
        "price": 3.99,
        "stock": 30
    },
    {
        "id": "3",
        "barcode": "3017624010703",
        "status": 1,
        "product": {
            "product_name": "Organic Oat Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, oats, cane sugar"
        },
        "price": 4.49,
        "stock": 25
    },
    {
        "id": "4",
        "barcode": "3017624010704",
        "status": 1,
        "product": {
            "product_name": "Organic Hemp Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, hemp seeds, cane sugar"
        },
        "price": 4.99,
        "stock": 20
    },
    {
        "id": "5",
        "barcode": "3017624010705",
        "status": 1,
        "product": {
            "product_name": "Organic Cashew Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, cashews, cane sugar"
        },
        "price": 4.79,
        "stock": 15
    },
    {
        "id": "6",
        "barcode": "3017624010706",
        "status": 1,
        "product": {
            "product_name": "Organic Rice Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, rice, cane sugar"
        },
        "price": 3.49,
        "stock": 10
    },
    {
        "id": "7",
        "barcode": "3017624010707",
        "status": 1,
        "product": {
            "product_name": "Organic Coconut Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, coconut, cane sugar"
        },
        "price": 4.29,
        "stock": 5
    }
]

# Helper Function: Queries real OpenFoodFacts data using the new API v3 endpoint


def fetch_from_openfoodfacts_v3(barcode):
    # Upgraded target endpoint to API v3 layout structure
    url = f"https://openfoodfacts.org{barcode}.json"
    headers = {
        "User-Agent": "InventoryAdminPortal - DeskApp - Version 2.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # In API v3, if the product is found, it returns "product_found" or a valid product block
            if "product" in data and data.get("product"):
                return data
    except requests.exceptions.RequestException:
        pass
    return None

# Root route


@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Inventory Management API is running", "version": "1.0"}), 200

# Route 1: Fetch all items


@app.route('/inventory', methods=['GET'])
def get_all_inventory():
    return jsonify(inventory_db), 200

# Route 2: Fetch a single item by ID


@app.route('/inventory/<string:item_id>', methods=['GET'])
def get_single_item(item_id):
    for item in inventory_db:
        if item["id"] == item_id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found in system database"}), 404

# Route 3: Create a new inventory record


@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    body = request.get_json()

    if not body or "barcode" not in body:
        return jsonify({"error": "Barcode field required to register product"}), 400

    barcode = body.get("barcode")
    price = body.get("price", 0.0)
    stock = body.get("stock", 0)

    for item in inventory_db:
        if item.get("barcode") == barcode:
            return jsonify({"error": "A product with this barcode already exists"}), 400

    # Using the upgraded API v3 function
    api_data = fetch_from_openfoodfacts_v3(barcode)

    if api_data and "product" in api_data:
        product_details = {
            "product_name": api_data["product"].get("product_name", "Unknown Item"),
            "brands": api_data["product"].get("brands", "Generic"),
            "ingredients_text": api_data["product"].get("ingredients_text", "No detailed ingredient data available")
        }
        status_flag = 1
    else:
        product_details = {
            "product_name": body.get("product_name", "Custom Product Entry"),
            "brands": body.get("brands", "Local Brand"),
            "ingredients_text": body.get("ingredients_text", "Manually specified record")
        }
        status_flag = 0

    new_id = str(len(inventory_db) + 1)
    new_entry = {
        "id": new_id,
        "barcode": barcode,
        "status": status_flag,
        "product": product_details,
        "price": float(price),
        "stock": int(stock)
    }

    inventory_db.append(new_entry)
    return jsonify(new_entry), 201

# Route 4: Update price/stock numbers (PATCH)


@app.route('/inventory/<string:item_id>', methods=['PATCH'])
def patch_inventory_item(item_id):
    body = request.get_json()
    if not body:
        return jsonify({"error": "Missing modification body contents"}), 400

    for item in inventory_db:
        if item["id"] == item_id:
            if "price" in body:
                item["price"] = float(body["price"])
            if "stock" in body:
                item["stock"] = int(body["stock"])
            return jsonify(item), 200

    return jsonify({"error": "Target item not matching current database indices"}), 404

# Route 5: Remove inventory entry (DELETE)


@app.route('/inventory/<string:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    global inventory_db
    for index, item in enumerate(inventory_db):
        if item["id"] == item_id:
            removed_element = inventory_db.pop(index)
            return jsonify({"message": f"Successfully deleted item {item_id}", "deleted": removed_element}), 200

    return jsonify({"error": "Requested removal profile match failed"}), 404


if __name__ == '__main__':
    app.run(port=5000, debug=True)
