from dotenv import load_dotenv
load_dotenv()

import json
import os

# Go up 4 levels from product.py to reach repo root, then into data/
_here = os.path.abspath(__file__)
PRODUCTS_PATH = os.path.join(
    os.path.dirname(  # agent/
    os.path.dirname(  # streamlit/
    os.path.dirname(  # project_2/
    os.path.dirname(_here)))),  # repo root
    "data", "products.json"
)

def lookup_product(product_id: str) -> dict:
    product_id = product_id.strip().strip('`').strip()
    try:
        with open(PRODUCTS_PATH) as f:
            products = json.load(f)
        result = next((p for p in products if p['product_id'] == product_id), None)
        if not result:
            return {"error": f"Product {product_id} not found"}
        return result
    except Exception as e:
        return {"error": f"Product lookup failed: {str(e)}"}

if __name__ == "__main__":
    print("Path:", PRODUCTS_PATH)
    print("Exists:", os.path.exists(PRODUCTS_PATH))
    print(lookup_product("PROD_1000"))