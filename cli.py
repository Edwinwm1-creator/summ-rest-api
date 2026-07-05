import requests
import json

# Local URL targeting our own Flask REST backend application
BASE_URL = "http://127.0.0.1:5000/inventory"


def display_menu():
    """Prints the clear user terminal dashboard choice selector matrix."""
    print("\n" + "="*45)
    print(" INVENTORY MANAGEMENT PORTAL - MENU SYSTEM")
    print("="*45)
    print("1. View Full Inventory Catalogue")
    print("2. Look Up Individual Item Details (By ID)")
    print("3. Register / Import New Product Record")
    print("4. Update Item Specific Valuation & Stock Levels")
    print("5. Purge/Delete Product Entry")
    print("6. Check Live OpenFoodFacts Barcode Directory (v3)")
    print("7. Terminate Dashboard Client Session")
    print("="*45)


def list_all_items():
    """Fetches and displays all items currently inside the database array."""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            items = response.json()
            if not items:
                print(
                    "Notice: Current array inventory workspace contains zero listings.")
                return
            for item in items:
                p = item["product"]
                print(
                    f"[ID: {item['id']}] Barcode: {item['barcode']} | {p['product_name']} ({p['brands']})")
                print(
                    f"      Price: ${item['price']:.2f} | Stock Level: {item['stock']} units")
        else:
            print(
                f"Error encountered. API responded with status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Network Exception: Confirm local server application backend app.py runner context is active.")


def view_single_item():
    """Looks up a specific database item by its unique index sequence ID."""
    item_id = input(
        "Provide target storage sequence verification index ID: ").strip()
    if not item_id:
        return
    try:
        response = requests.get(f"{BASE_URL}/{item_id}")
        if response.status_code == 200:
            item = response.json()
            print("\n--- DETAILED PRODUCT VERIFICATION MATRICES ---")
            print(json.dumps(item, indent=4))
        else:
            print(
                f"Query Notification: {response.json().get('error', 'Operation mapping fault.')}")
    except requests.exceptions.ConnectionError:
        print("Connection Failure: Target service endpoint is unreachable.")


def add_new_item():
    """Registers a new inventory item and checks OpenFoodFacts API v3 to automate data entry."""
    print("\n--- ADD NEW RECORD CONFIGURATOR ---")
    barcode = input("Enter product barcode number: ").strip()
    if not barcode:
        print("Error: Barcode input value cannot be left blank.")
        return
    price_input = input("Enter unit sale price: $").strip()
    stock_input = input("Enter current physical asset count: ").strip()

    try:
        price = float(price_input) if price_input else 0.0
        stock = int(stock_input) if stock_input else 0
    except ValueError:
        print("Formatting Failure: Price must resolve to numeric, stock values to whole numbers.")
        return

    payload = {"barcode": barcode, "price": price, "stock": stock}

    # Pre-check API v3 data directly from the CLI to prompt for manual entries if needed
    v3_check_url = f"https://openfoodfacts.org{barcode}.json"
    headers = {
        "User-Agent": "InventoryAdminPortal/1.0 (Beginner Assignment Application)"}
    print("Scanning global registries via OpenFoodFacts API v3 network connection...")

    try:
        check_resp = requests.get(v3_check_url, headers=headers, timeout=4)
        if check_resp.status_code != 200 or check_resp.json().get("status") != "success":
            print(
                "Notice: Barcode registration footprint absent on OpenFoodFacts API v3 directory.")
            payload["product_name"] = input(
                "Manually enter Product Name: ").strip()
            payload["brands"] = input(
                "Manually enter Brand Designation: ").strip()
            payload["ingredients_text"] = input(
                "Manually enter Product Ingredients Info: ").strip()
    except Exception:
        print("API Lookup Warning: Proceeding with fallback local profile inputs.")

    try:
        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 201:
            print(
                "Success: Record successfully pushed and updated within database registry array.")
            print(json.dumps(response.json(), indent=2))
        else:
            print(
                f"Request Blocked: {response.json().get('error', 'Unknown system data error.')}")
    except requests.exceptions.ConnectionError:
        print("Connection Failure: Check if app.py runtime loop handles requests.")


def update_item():
    """Modifies the price or stock levels of an entry via a PATCH request."""
    item_id = input(
        "Provide target database index entry sequence ID: ").strip()
    if not item_id:
        return
    print("Leave field blank to keep current system setting values.")
    new_price = input("New valuation unit price: $").strip()
    new_stock = input("New operational safety stock count: ").strip()

    payload = {}
    try:
        if new_price:
            payload["price"] = float(new_price)
        if new_stock:
            payload["stock"] = int(new_stock)
    except ValueError:
        print("Invalid Entry: Numerical formatting parse failure.")
        return

    if not payload:
        print("No input data provided. Update cancelled.")
        return

    try:
        response = requests.patch(f"{BASE_URL}/{item_id}", json=payload)
        if response.status_code == 200:
            print("Modification Success: Record updated successfully.")
            print(json.dumps(response.json(), indent=2))
        else:
            print(
                f"Modification Error: {response.json().get('error', 'Execution task failure.')}")
    except requests.exceptions.ConnectionError:
        print("Connection Failure: Backend system not available.")


def delete_item():
    """Removes a product entirely from the server data array list using its database ID."""
    item_id = input(
        "Enter target product item registry ID for complete deletion: ").strip()
    if not item_id:
        return
    confirm = input(
        f"Are you sure you want to permanently delete item index {item_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Deletion process cancelled safely.")
        return

    try:
        response = requests.delete(f"{BASE_URL}/{item_id}")
        if response.status_code == 200:
            print(
                "Purge Operation Confirmed: Product safely removed from operational matrices.")
        else:
            print(
                f"Failure Notice: {response.json().get('error', 'Target element index missing.')}")
    except requests.exceptions.ConnectionError:
        print("Network failure verification error context.")


def check_external_api_v3():
    """Queries OpenFoodFacts API v3 directly to view raw external product attributes."""
    barcode = input(
        "Enter target barcode to scan against OpenFoodFacts v3 database: ").strip()
    if not barcode:
        return
    url = f"https://openfoodfacts.org{barcode}.json"
    headers = {
        "User-Agent": "InventoryAdminPortal/1.0 (Beginner Assignment Application)"}
    print("Querying external OpenFoodFacts API v3 directory...")
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            # API v3 explicitly uses string "success" for active items instead of integer 1
            if data.get("status") == "success" and "product" in data:
                p = data["product"]
                print("\n[MATCH FOUND EXTERNALLY VIA API V3]")
                print(f"Product Name: {p.get('product_name', 'N/A')}")
                print(f"Brand Origin: {p.get('brands', 'N/A')}")
                print(
                    f"Ingredients Profile Summary: {p.get('ingredients_text', 'N/A')}")
            else:
                print(
                    "No product matches this barcode sequence within OpenFoodFacts v3 records.")
        else:
            print(
                f"Query failure returned status code response context: {res.status_code}")
    except Exception as e:
        print(
            f"External API communication loop fault exception tracking block: {e}")


def main():
    """Launches choice evaluation application execution context wrapper."""
    while True:
        display_menu()
        choice = input("Enter menu item option selection (1-7): ").strip()
        if choice == "1":
            list_all_items()
        elif choice == "2":
            view_single_item()
        elif choice == "3":
            add_new_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            check_external_api_v3()
        elif choice == "7":
            print("Closing Admin Portal. Session logged out safely.")
            break
        else:
            print("Selection out of bounds. Pick a valid option (1-7).")


if __name__ == '__main__':
    main()
