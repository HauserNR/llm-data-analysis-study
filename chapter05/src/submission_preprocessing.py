"""Chapter 05: 원본 보존, 처리 사유 기록, 재검증을 포함한 제출용 전처리."""
from pathlib import Path
import pandas as pd
from src.data_loader import load_sales_data
from src.preprocessing import STATUS_MAP, save_processed_data, validate_relationships

KEYS = {"customers": "customer_id", "products": "product_id", "orders": "order_id", "order_items": "order_item_id"}
CATEGORY_MAP = {"전자 기기": "전자기기", "생활 용품": "생활용품", "뷰 티": "뷰티"}
ALLOWED_STATUS = {"completed", "cancelled", "refunded"}
REFERENCE_DATE = pd.Timestamp("2026-10-14")


def quality(data):
    return pd.DataFrame([{
        "dataset": name, "rows": len(df), "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "pk_missing": int(df[KEYS[name]].isna().sum()),
        "pk_duplicates": int(df[KEYS[name]].duplicated().sum()),
    } for name, df in data.items()])


def preprocess_with_audit(raw):
    # 완전히 동일한 행만 제외한다. 속성이 다른 PK 중복은 임의로 선택하지 않는다.
    data = {name: df.drop_duplicates().copy() for name, df in raw.items()}
    audit = []
    string_audit = []
    conversion_audit = []
    rejections = []
    candidates = []
    stages = {"raw": quality(raw), "deduplicated": quality(data)}
    for name, df in data.items():
        key = KEYS[name]
        assert df[key].notna().all(), f"{name}: PK missing; review required"
        assert not df[key].duplicated().any(), f"{name}: conflicting PK; review required"
        audit.append({"dataset": name, "operation": "exact duplicate removal", "affected": len(raw[name]) - len(df)})
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col].dtype):
                before = df[col].astype("string")
                stripped = before.str.strip()
                changed = int((before.notna() & before.ne(stripped)).fillna(False).sum())
                empty = int(stripped.eq("").fillna(False).sum())
                df[col] = stripped.replace("", pd.NA)
                string_audit.append({"dataset": name, "column": col, "trimmed": changed, "empty_to_na": empty,
                                     "missing_after": int(df[col].isna().sum())})
    stages["strings"] = quality(data)

    numeric_columns = {"customers": ["age"], "products": ["price"], "order_items": ["quantity", "unit_price"]}
    for name, cols in numeric_columns.items():
        for col in cols:
            before = data[name][col].astype("string")
            converted = pd.to_numeric(before.str.replace(",", "", regex=False), errors="coerce")
            conversion_audit.append({"dataset": name, "column": col, "kind": "numeric", "rows_checked": len(before),
                "missing_before": int(before.isna().sum()),
                "comma_removed": int(before.str.contains(",", regex=False, na=False).sum()),
                "new_failures": int((before.notna() & converted.isna()).sum()),
                "missing_immediately_after": int(converted.isna().sum())})
            data[name][col] = converted.astype("Float64")
    for name, col in [("customers", "signup_date"), ("orders", "order_date")]:
        before = data[name][col].astype("string")
        converted = pd.to_datetime(before, format="mixed", errors="coerce")
        conversion_audit.append({"dataset": name, "column": col, "kind": "date", "rows_checked": len(before),
            "missing_before": int(before.isna().sum()), "comma_removed": 0,
            "new_failures": int((before.notna() & converted.isna()).sum()),
            "missing_immediately_after": int(converted.isna().sum())})
        data[name][col] = converted
    stages["converted"] = quality(data)

    age_median = float(data["customers"]["age"].median())
    age_missing = int(data["customers"]["age"].isna().sum())
    assert pd.notna(age_median), "No usable age; do not fabricate a median"
    data["customers"]["age"] = data["customers"]["age"].fillna(age_median)
    city_missing = int(data["customers"]["city"].isna().sum())
    data["customers"]["city"] = data["customers"]["city"].fillna("Unknown")
    audit.extend([
        {"dataset": "customers", "operation": f"age median imputation ({age_median})", "affected": age_missing},
        {"dataset": "customers", "operation": "city Unknown", "affected": city_missing},
    ])
    status_before = data["orders"]["order_status"].copy()
    data["orders"]["order_status"] = status_before.replace(STATUS_MAP)
    audit.append({"dataset": "orders", "operation": "status normalization", "affected": int(status_before.ne(data["orders"]["order_status"]).sum())})
    category_before = data["products"]["category"].copy()
    data["products"]["category"] = category_before.replace(CATEGORY_MAP)
    audit.append({"dataset": "products", "operation": "category alias normalization", "affected": int(category_before.ne(data["products"]["category"]).sum())})
    stages["imputed_normalized"] = quality(data)

    # 변환 실패와 비양수를 별도로 기록한 뒤 실습의 양수 분석 범위에서 제외한다.
    for name, cols in [("products", ["price"]), ("order_items", ["quantity", "unit_price"])]:
        df = data[name]
        reasons = pd.Series("", index=df.index, dtype="string")
        for col in cols:
            for mask, reason in [(df[col].isna(), f"{col}:conversion_failed_or_missing"),
                                 (df[col].le(0).fillna(False), f"{col}:nonpositive")]:
                reasons.loc[mask] += reason + ";"
        excluded = reasons.ne("")
        for idx in df.index[excluded]:
            rejections.append({"dataset": name, "primary_key": int(df.at[idx, KEYS[name]]), "reason": reasons.at[idx]})
        audit.append({"dataset": name, "operation": "numeric eligibility exclusion (unique rows)", "affected": int(excluded.sum())})
        data[name] = df.loc[~excluded].copy()
    stages["filtered"] = quality(data)
    date = data["orders"]["order_date"]
    data["orders"]["order_month"] = date.dt.to_period("M").astype("string").where(date.notna(), pd.NA)
    data["orders"]["order_dayofweek"] = date.dt.day_name().astype("string")
    data["order_items"]["line_total"] = data["order_items"]["quantity"] * data["order_items"]["unit_price"]
    stages["final"] = quality(data)

    # 아래 임계값은 검토 대상을 고르는 기준이며 자동 삭제 기준이 아니다.
    candidate_rules = [
        ("customers", "age", data["customers"]["age"].lt(0) | data["customers"]["age"].gt(120), "outside 0..120"),
        ("products", "price", data["products"]["price"].gt(1_000_000), "above review threshold 1,000,000"),
        ("order_items", "quantity", data["order_items"]["quantity"].gt(20), "above review threshold 20"),
        ("orders", "order_date", data["orders"]["order_date"].gt(REFERENCE_DATE), "after assignment date 2026-10-14"),
    ]
    for name, col, mask, reason in candidate_rules:
        for _, row in data[name].loc[mask.fillna(False)].iterrows():
            candidates.append({"dataset": name, "primary_key": int(row[KEYS[name]]), "column": col,
                "value": str(row[col]), "reason": reason, "decision": "retain; review business meaning"})
    return data, {
        "operations": pd.DataFrame(audit), "strings": pd.DataFrame(string_audit),
        "conversions": pd.DataFrame(conversion_audit), "rejected": pd.DataFrame(rejections),
        "candidates": pd.DataFrame(candidates), "stages": stages, "age_median": age_median,
        "relationships": validate_relationships(data),
        "unexpected_status": data["orders"].loc[~data["orders"]["order_status"].isin(ALLOWED_STATUS), ["order_id", "order_status"]],
    }


def report_text(raw, clean, evidence):
    def table(df):
        return df.to_markdown(index=False)
    return "\n\n".join([
        "# Chapter 05 데이터 전처리 요약",
        "## 입력과 결과 파일\n입력: data/raw/ (공식 전용 Raw, 원본 보존)\n"
        "결과: data/processed/customers_clean.csv, products_clean.csv, orders_clean.csv, order_items_clean.csv",
        "## 전처리 전 상태\n" + table(quality(raw)),
        "## 전처리 후 상태\n" + table(quality(clean)),
        "## 문자열·빈 문자열\n" + table(evidence["strings"]),
        "## 숫자·날짜 변환 실패\n" + table(evidence["conversions"]),
        "## 처리 기준과 영향 건수\n" + table(evidence["operations"]),
        "## 제외 사유 (원본 삭제 아님)\n" + table(evidence["rejected"]),
        "## 검토 후 보류한 이상값 후보\n" + table(evidence["candidates"]),
        "## PK/FK 재검증\n" + table(evidence["relationships"]),
        "## 파생 컬럼\norder_month, order_dayofweek, line_total = quantity × unit_price. "
        "날짜 실패는 NaT로 유지하고 월/요일도 결측으로 유지한다.",
        "## 업무 적용 한계\n완전 중복만 제거한다. PK 충돌은 자동 삭제하지 않는다. "
        "age의 기존 결측과 숫자 변환 실패는 구분해 기록한 뒤 실습 기준으로 중앙값을 대체한다. "
        "city는 Unknown으로 남긴다. ID·날짜·금액을 임의로 복구하지 않는다. "
        "비양수 금액·수량과 숫자 변환 실패 행은 정상 양수 분석 범위에서만 제외하고 사유를 보존한다. "
        "없는 FK는 자동 제거하지 않는다. FK 불일치와 날짜 실패, 미래 날짜, 극단값이 남아 있으므로 "
        "clean이라는 이름만으로 완전한 데이터 또는 확정 매출로 해석할 수 없다. "
        "매출 분석에서는 completed 상태, 연결 가능한 키, 유효 날짜, 분석 기간을 명시해야 한다.",
    ]) + "\n"


def run_pipeline(project_root):
    root = Path(project_root)
    raw = load_sales_data(root / "data/raw")
    clean, evidence = preprocess_with_audit(raw)
    paths = save_processed_data(clean, root / "data/processed")
    report = root / "reports/ch05_preprocessing_summary.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text(report_text(raw, clean, evidence), encoding="utf-8")
    print("전처리 완료 (품질 오류는 아래 결과로 별도 확인)")
    print(quality(clean).to_string(index=False))
    print(evidence["relationships"].to_string(index=False))
    print("숫자/날짜 신규 실패:", int(evidence["conversions"]["new_failures"].sum()))
    print("제외:", len(evidence["rejected"]), "보류 후보:", len(evidence["candidates"]))
    for path in paths:
        print(path.relative_to(root).as_posix(), path.stat().st_size, "bytes")
    print(report.relative_to(root).as_posix())
    return clean, evidence
