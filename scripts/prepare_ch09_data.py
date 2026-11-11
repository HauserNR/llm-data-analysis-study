"""Prepare validated Chapter09 regression input from the common project raw data.

Run from the project root or any working directory:

    python scripts/prepare_ch09_data.py

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
Chapter09는 Chapter08에서 검증한 공통 프로젝트 데이터 흐름을 이어받습니다.
"""

from __future__ import annotations

from pathlib import Path
import sys


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


def prepare_ch09_data(
    raw_dir: str | Path = RAW_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
) -> dict[str, object]:
    """Preprocess common raw data and fail if core FK relationships are broken."""
    raw_data = load_sales_data(raw_dir)
    import numpy as np
    import pandas as pd
    checks = []
    for table, key in [("customers", "customer_id"), ("products", "product_id"),
                       ("orders", "order_id"), ("order_items", "order_item_id")]:
        frame = raw_data[table]
        checks.append((f"{table}_pk", frame[key].notna().all() and frame[key].is_unique))
    for child, fk, parent, pk in [("orders", "customer_id", "customers", "customer_id"),
                                  ("order_items", "order_id", "orders", "order_id"),
                                  ("order_items", "product_id", "products", "product_id")]:
        checks.append((f"{child}_{fk}_fk", raw_data[child][fk].notna().all() and raw_data[child][fk].isin(raw_data[parent][pk]).all()))
    checks.append(("every_order_has_detail", raw_data["orders"].order_id.isin(raw_data["order_items"].order_id).all()))
    amounts = raw_data["order_items"][["quantity", "unit_price"]].apply(pd.to_numeric, errors="coerce")
    checks.append(("amounts_finite_positive", np.isfinite(amounts).all().all() and amounts.gt(0).all().all()))
    checks.append(("dates_valid", pd.to_datetime(raw_data["orders"].order_date, errors="coerce").notna().all()))
    if not all(ok for _, ok in checks):
        raise ValueError(f"Raw validation failed: {checks}")
    processed_data = preprocess_sales_data(raw_data)
    if any(len(raw_data[k]) != len(processed_data[k]) for k in raw_data):
        raise ValueError("Preprocessing changed row counts; investigate before modeling")
    report_dir = PROJECT_ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    pd.DataFrame([{"check": name, "status": "PASS" if ok else "FAIL"} for name, ok in checks]).to_csv(report_dir / "ch09_source_checks.csv", index=False)
    relationship_checks = validate_relationships(processed_data)

    if (
        not relationship_checks.empty
        and not relationship_checks["invalid_count"].eq(0).all()
    ):
        failed = relationship_checks.loc[
            relationship_checks["invalid_count"].ne(0)
        ]
        raise ValueError(
            "Chapter09 입력 관계 검증에 실패했습니다:\n"
            + failed.to_string(index=False)
        )

    saved_paths = save_processed_data(processed_data, processed_dir)
    return {
        "raw_data": raw_data,
        "processed_data": processed_data,
        "relationship_checks": relationship_checks,
        "saved_paths": saved_paths,
    }


def main() -> None:
    result = prepare_ch09_data()

    print("Chapter09 모델링 입력 준비 완료")
    print(f"입력 Raw 경로: {RAW_DIR}")
    print("\n[관계 검증]")
    print(result["relationship_checks"].to_string(index=False))
    print("\n[저장된 processed 파일]")
    for path in result["saved_paths"]:
        print(f"- {path}")


if __name__ == "__main__":
    main()
