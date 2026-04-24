from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../ecommerce_purchases.csv")

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_HTTP_PATH = os.environ.get("DATABRICKS_HTTP_PATH", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")


def lookup_from_databricks(order_id: str) -> dict:
    """Look up a live UUID order from Databricks Gold view."""
    try:
        from databricks import sql
        conn = sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM delta.`/Volumes/project_2/datalake/gold/v_order_features`
            WHERE order_id = '{order_id}'
        """)
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        if row is None:
            return {"error": f"Order {order_id} not found in live data"}

        return dict(zip(columns, row))

    except Exception as e:
        return {"error": f"Databricks lookup failed: {str(e)}"}


def lookup_from_csv(order_id: str) -> dict:
    """Look up a training CSV order by ORD- prefixed ID."""
    try:
        df = pd.read_csv(CSV_PATH)
        row = df[df['order_id'] == order_id]
        if row.empty:
            return {"error": f"Order {order_id} not found"}
        return row.iloc[0].to_dict()
    except Exception as e:
        return {"error": f"CSV lookup failed: {str(e)}"}


def lookup_order(order_id: str) -> dict:
    """
    Route lookup based on order ID format:
    - ORD-XXXXXXXX format → CSV (training data, used for demo scoring)
    - UUID format → Databricks Gold view (live Kafka data)
    """
    # Clean the input
    order_id = order_id.strip().strip('`').strip()

    if order_id.startswith("ORD-"):
        return lookup_from_csv(order_id)
    else:
        return lookup_from_databricks(order_id)


if __name__ == "__main__":
    # Test CSV lookup
    print("Testing CSV lookup (ORD- format):")
    result = lookup_order("ORD-17633387")
    print(result)
    print()

    # Test Databricks lookup with a real UUID
    print("Testing Databricks lookup (UUID format):")
    result = lookup_order("531d6be0-d4b5-4903-a9ef-904687c0b71e")
    print(result)