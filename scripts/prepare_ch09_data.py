"""Validate source relationships and prepare one row per order for Chapter 09."""
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "chapter09" / "data"


def prepare():
    orders = pd.read_csv(RAW / "orders.csv", encoding="utf-8-sig")
    items = pd.read_csv(RAW / "order_items.csv", encoding="utf-8-sig")
    customers = pd.read_csv(RAW / "customers.csv", encoding="utf-8-sig")
    checks = {
        "orders_pk_unique": orders.order_id.is_unique,
        "items_pk_unique": items.order_item_id.is_unique,
        "customers_pk_unique": customers.customer_id.is_unique,
        "orders_keys_present": orders[["order_id", "customer_id"]].notna().all().all(),
        "items_keys_present": items[["order_item_id", "order_id", "product_id"]].notna().all().all(),
        "customers_key_present": customers.customer_id.notna().all(),
        "all_orders_have_details": orders.order_id.isin(items.order_id).all(),
        "items_fk_valid": items.order_id.isin(orders.order_id).all(),
        "customers_fk_valid": orders.customer_id.isin(customers.customer_id).all(),
        "line_inputs_present": items[["quantity", "unit_price"]].notna().all().all(),
        "line_inputs_nonnegative": (items[["quantity", "unit_price"]] >= 0).all().all(),
        "order_dates_valid": pd.to_datetime(orders.order_date, errors="coerce").notna().all(),
    }
    if not all(checks.values()):
        raise ValueError(f"Source data validation failed: {checks}")

    items["line_total"] = items.quantity * items.unit_price
    checks["line_total_formula"] = bool(np.allclose(items.line_total, items.quantity * items.unit_price))
    totals = items.groupby("order_id", as_index=False).line_total.sum().rename(columns={"line_total": "order_total"})
    checks["order_total_formula"] = bool(np.allclose(totals.order_total, items.groupby("order_id").line_total.sum().to_numpy()))
    checks["orders_totals_one_to_one"] = totals.order_id.is_unique and orders.order_id.is_unique
    checks["orders_customers_many_to_one"] = customers.customer_id.is_unique
    if not all(checks.values()):
        raise ValueError(f"Target validation failed: {checks}")

    data = orders.merge(totals, on="order_id", how="left", validate="one_to_one", indicator=True)
    if not data._merge.eq("both").all() or data.order_total.isna().any():
        raise ValueError("Every order must have a detail-derived target")
    data = data.drop(columns="_merge").merge(
        customers[["customer_id", "gender", "age", "city"]],
        on="customer_id", how="left", validate="many_to_one", indicator=True,
    )
    if not data._merge.eq("both").all():
        raise ValueError("Every order must match exactly one customer")
    data = data.drop(columns="_merge")
    data["order_date"] = pd.to_datetime(data.order_date)
    data["order_month"] = data.order_date.dt.month
    data["order_dayofweek"] = data.order_date.dt.dayofweek
    OUT.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUT / "ch09_order_level.csv", index=False)
    pd.DataFrame({"check": list(checks), "result": ["PASS" if x else "FAIL" for x in checks.values()]}).to_csv(
        OUT / "ch09_source_checks.csv", index=False
    )
    return data, checks


if __name__ == "__main__":
    data, checks = prepare()
    print(f"Prepared {len(data)} orders; {len(checks)} source checks PASS")
