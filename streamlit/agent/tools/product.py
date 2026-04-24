from dotenv import load_dotenv
load_dotenv()
import json
import os

PRODUCTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/products.json")

def lookup_product(product_id: str) -> dict:
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
    print(lookup_product("PROD_1000"))