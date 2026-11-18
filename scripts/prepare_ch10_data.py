"""Prepare validated Chapter10 classification input from common project raw data.

Run from the project root:

    python scripts/prepare_ch10_data.py

Input:
    data/raw/customers.csv
    data/raw/products.csv
    data/raw/orders.csv
    data/raw/order_items.csv

Output:
    data/processed/customers_clean.csv
    data/processed/products_clean.csv
    data/processed/orders_clean.csv
    data/processed/order_items_clean.csv

Chapter05의 전용 오류 탐지 데이터(`practice/chapter05/data/raw`)는 사용하지 않습니다.
Chapter10은 Chapter08·09와 같은 공통 프로젝트 데이터 흐름을 이어받습니다.
"""

from __future__ import annotations

from pathlib import Path
import sys
import hashlib

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_sales_data  # noqa: E402
from src.preprocessing import (  # noqa: E402
    preprocess_sales_data,
    save_processed_data,
    validate_relationships,
)


RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def prepare_ch10_data(
    raw_dir: str | Path = RAW_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
) -> dict[str, object]:
    """Preprocess common raw data and fail on core relationship errors."""
    raw_data = load_sales_data(raw_dir)
    source_checks = []

    def check(name, value, passed, resolution="검증 통과"):
        source_checks.append({"check": name, "value": value,
                              "status": "PASS" if passed else "FAIL",
                              "resolution": resolution})

    for table, key in [("customers", "customer_id"), ("products", "product_id"),
                       ("orders", "order_id"), ("order_items", "order_item_id")]:
        frame = raw_data[table]
        invalid = int(frame[key].isna().sum() + frame[key].duplicated().sum())
        check(f"{table}_primary_key", invalid, invalid == 0)
        duplicates = int(frame.duplicated().sum())
        check(f"{table}_duplicate_rows", duplicates, duplicates == 0)
    for child, fk, parent, pk in [("orders", "customer_id", "customers", "customer_id"),
                                  ("order_items", "order_id", "orders", "order_id"),
                                  ("order_items", "product_id", "products", "product_id")]:
        invalid = int((raw_data[child][fk].isna() | ~raw_data[child][fk].isin(raw_data[parent][pk])).sum())
        check(f"{child}_{fk}_foreign_key", invalid, invalid == 0)
    missing_detail = int((~raw_data["orders"].order_id.isin(raw_data["order_items"].order_id)).sum())
    check("every_order_has_detail", missing_detail, missing_detail == 0)
    values = raw_data["order_items"][["quantity", "unit_price"]].apply(pd.to_numeric, errors="coerce")
    invalid_amounts = int((~np.isfinite(values) | values.le(0)).any(axis=1).sum())
    check("finite_positive_quantity_price", invalid_amounts, invalid_amounts == 0)
    for table, columns in {
        "orders": ["order_id", "customer_id", "order_date", "order_status", "payment_method"],
        "customers": ["customer_id", "gender", "age", "city", "signup_date"],
        "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
    }.items():
        missing = int(raw_data[table][columns].isna().sum().sum())
        check(f"{table}_required_missing", missing, missing == 0)
    for table, col in [("orders", "order_date"), ("customers", "signup_date")]:
        invalid_dates = int(pd.to_datetime(raw_data[table][col], errors="coerce").isna().sum())
        check(f"{table}_{col}_parse", invalid_dates, invalid_dates == 0)
    if "line_total" in raw_data["order_items"]:
        supplied = pd.to_numeric(raw_data["order_items"].line_total, errors="coerce")
        mismatch = int((~np.isfinite(supplied) | (supplied - values.quantity * values.unit_price).abs().gt(1e-6)).sum())
        check("raw_line_total_mismatch", mismatch, mismatch == 0)
    failures = [r for r in source_checks if r["status"] == "FAIL"]
    if failures:
        raise ValueError(f"Raw validation failed; no rows silently removed: {failures}")

    processed_data = preprocess_sales_data(raw_data)
    for table in raw_data:
        check(f"{table}_row_count_preserved", len(processed_data[table]),
              len(raw_data[table]) == len(processed_data[table]))
    items = processed_data["order_items"]
    mismatch = int((items.line_total - items.quantity * items.unit_price).abs().gt(1e-6).sum())
    check("processed_line_total_mismatch", mismatch, mismatch == 0)
    if any(r["status"] == "FAIL" for r in source_checks):
        raise ValueError(f"Preprocessing quality failure: {source_checks}")

    dates = processed_data["orders"].merge(
        processed_data["customers"][["customer_id", "signup_date"]],
        on="customer_id", validate="many_to_one")
    negative = dates.order_date.lt(dates.signup_date)
    source_checks.append({
        "check": "signup_after_order_all_statuses", "value": int(negative.sum()),
        "status": "WARN" if negative.any() else "PASS",
        "resolution": "가상 데이터 생성기의 날짜 독립 추출. 원본·주문 보존; signup_date/days_since_signup 전체 입력 제외",
    })
    relationship_checks = validate_relationships(processed_data)

    if (
        not relationship_checks.empty
        and not relationship_checks["invalid_count"].eq(0).all()
    ):
        failed = relationship_checks.loc[
            relationship_checks["invalid_count"].ne(0)
        ]
        raise ValueError(
            "Chapter10 입력 관계 검증에 실패했습니다:\n"
            + failed.to_string(index=False)
        )

    saved_paths = save_processed_data(processed_data, processed_dir)
    report_dir = PROJECT_ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    source_checks = pd.DataFrame(source_checks)
    source_checks.to_csv(report_dir / "ch10_source_checks.csv", index=False)
    manifest = []
    for table, frame in raw_data.items():
        path = Path(raw_dir) / f"{table}.csv"
        manifest.append({"file": f"data/raw/{path.name}", "rows": len(frame),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    pd.DataFrame(manifest).to_csv(report_dir / "ch10_input_manifest.csv", index=False)
    return {
        "raw_data": raw_data,
        "processed_data": processed_data,
        "relationship_checks": relationship_checks,
        "saved_paths": saved_paths,
        "source_checks": source_checks,
    }


def main() -> None:
    result = prepare_ch10_data()

    print("Chapter10 모델링 입력 준비 완료")
    print(f"입력 Raw 경로: {RAW_DIR}")
    print("\n[관계 검증]")
    print(result["relationship_checks"].to_string(index=False))
    print("\n[Raw/Processed 품질 검사: 날짜 WARN은 Feature 제외로 완화]")
    print(result["source_checks"].to_string(index=False))
    print("\n[저장된 processed 파일]")
    for path in result["saved_paths"]:
        print(f"- {path}")


if __name__ == "__main__":
    main()
