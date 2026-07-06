# Inventory Management API and CLI

This project is a small inventory system built with Flask and a command-line client. It was designed to show how a simple REST API can be paired with a terminal dashboard, and it includes basic tests so you can verify the backend works as expected.

## What’s in this repository

- `app.py` — Flask application serving inventory data from an in-memory list.
- `cli.py` — command-line dashboard that talks to the API.
- `test_app.py` — `pytest` tests for the main Flask endpoints.
- `env/` — local Python virtual environment already set up for the project.

## How the app works

### `app.py`

The server keeps inventory items in a list called `inventory_db`. That means the data is temporary: when the server restarts, the inventory resets.

Each item includes:

- `id` — unique string identifier
- `barcode` — product barcode
- `status` — `1` when OpenFoodFacts returned a match, otherwise `0`
- `product` — nested product details like name, brand, and ingredients
- `price` — item price
- `stock` — quantity available

The app exposes these routes:

- `GET /` — quick health check with a status message and version
- `GET /inventory` — return the full inventory list
- `GET /inventory/<item_id>` — return one item by ID
- `POST /inventory` — add a new inventory item
- `PATCH /inventory/<item_id>` — update price and/or stock
- `DELETE /inventory/<item_id>` — delete an item

When you create a new item, the app tries to look it up on OpenFoodFacts API v3 first. If the barcode exists there, it uses the returned product information. If not, it accepts manually supplied product data.

### `cli.py`

The CLI is a menu-driven interface that talks to the Flask backend at `http://127.0.0.1:5000/inventory`.

It offers a few simple actions:

- list all inventory items
- view one item by ID
- add a new item
- update item price or stock
- delete an item
- check a barcode directly against OpenFoodFacts

It also does basic input validation and prints clear messages when something fails.

### `test_app.py`

These tests use `pytest` to make sure the Flask routes behave the way we expect.

The suite covers:

- fetching the full inventory
- fetching a single item by ID
- returning a 404 for missing items
- creating a fallback item when the external lookup fails
- updating an item with `PATCH`
- deleting an item and verifying it is gone

## Getting started

1. Activate the virtual environment:

```bash
source env/bin/activate
```

2. Install dependencies if needed:

```bash
pip install flask requests pytest
```

3. Start the Flask server:

```bash
python app.py
```

4. In another terminal, start the CLI:

```bash
python cli.py
```

## Example API calls

Fetch the full inventory:

```bash
curl http://127.0.0.1:5000/inventory
```

Fetch one item:

```bash
curl http://127.0.0.1:5000/inventory/1
```

Add a new item:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"barcode": "999999999", "price": 1.50, "stock": 10, "product_name": "Test Soda", "brands": "Test Brand", "ingredients_text": "Carbonated water, corn syrup"}'
```

Update an item:

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 4.50, "stock": 50}'
```

Delete an item:

```bash
curl -X DELETE http://127.0.0.1:5000/inventory/1
```

## Running tests

Run this from the project root:

```bash
pytest
```

## Notes

- This is an in-memory demo app, so inventory data is not persisted.
- `cli.py` expects the Flask app to be running locally on port `5000`.
- OpenFoodFacts lookup is attempted automatically when adding new products; if it fails, the app falls back to manual data.
