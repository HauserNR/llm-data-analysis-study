"""Leakage-aware chronological regression evaluation for Chapter 09."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from prepare_ch09_data import ROOT, prepare


REPORTS = ROOT / "reports"
FEATURES = ["order_month", "order_dayofweek", "age", "payment_method", "gender", "city"]
FORBIDDEN = {
    "order_total", "line_total", "quantity", "unit_price", "item_count", "total_quantity",
    "avg_unit_price", "order_status", "order_id", "customer_id", "product_id",
}
NUMERIC = ["order_month", "order_dayofweek", "age"]
CATEGORICAL = ["payment_method", "gender", "city"]


def model(estimator):
    preprocess = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                           ("encode", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL),
    ])
    return Pipeline([("preprocess", preprocess), ("regressor", estimator)])


def scores(y, pred):
    return {"MAE": mean_absolute_error(y, pred),
            "RMSE": np.sqrt(mean_squared_error(y, pred)), "R2": r2_score(y, pred)}


def run():
    data, source_checks = prepare()
    overlap = sorted(set(FEATURES) & FORBIDDEN)
    if overlap or len(FEATURES) != len(set(FEATURES)) or not set(FEATURES).issubset(data):
        raise ValueError(f"Feature audit failed: {overlap}")
    # Hold out entire last two calendar months. Same-date orders never cross the boundary.
    data = data.sort_values(["order_date", "order_id"]).reset_index(drop=True)
    cutoff = data.order_date.dt.to_period("M").drop_duplicates().iloc[-2].to_timestamp()
    train = data[data.order_date < cutoff].copy()
    test = data[data.order_date >= cutoff].copy()
    if len(train) < 30 or len(test) < 2 or not train.order_date.max() < test.order_date.min():
        raise ValueError("Invalid chronological split")

    candidates = {
        "Baseline Mean": lambda: DummyRegressor(strategy="mean"),
        "Linear Regression": lambda: model(LinearRegression()),
        "Random Forest": lambda: model(RandomForestRegressor(n_estimators=200, min_samples_leaf=5,
                                                              random_state=42, n_jobs=1)),
    }
    # Split by dates, rather than rows, to ensure equal-date orders stay in one fold.
    unique_dates = np.array(sorted(train.order_date.unique()))
    cv_rows = []
    for fold, (train_dates, valid_dates) in enumerate(TimeSeriesSplit(n_splits=5).split(unique_dates), 1):
        tr = train[train.order_date.isin(unique_dates[train_dates])]
        va = train[train.order_date.isin(unique_dates[valid_dates])]
        assert tr.order_date.max() < va.order_date.min()
        for name, factory in candidates.items():
            fitted = factory().fit(tr[FEATURES], tr.order_total)
            cv_rows.append({"model": name, "fold": fold, "train_rows": len(tr), "valid_rows": len(va),
                            "train_max_date": tr.order_date.max().date(), "valid_min_date": va.order_date.min().date(),
                            "MAE": mean_absolute_error(va.order_total, fitted.predict(va[FEATURES]))})
    cv = pd.DataFrame(cv_rows)
    summary = cv.groupby("model").MAE.agg(["mean", "std", "min", "max"]).reset_index().sort_values(["mean", "model"])
    # Selection rule is fixed before fitting or inspecting final-test predictions.
    selected = str(summary.iloc[0]["model"])
    baseline = candidates["Baseline Mean"]().fit(train[FEATURES], train.order_total)
    frozen = candidates[selected]().fit(train[FEATURES], train.order_total)
    final_rows = []
    for name, fitted in [("Baseline Mean", baseline), ("Frozen Selected Model", frozen)]:
        final_rows.append({"model": name, "selected_model": selected, "test_rows": len(test),
                           **scores(test.order_total, fitted.predict(test[FEATURES]))})
    final = pd.DataFrame(final_rows)
    improvement = 100 * (final.iloc[0].MAE - final.iloc[1].MAE) / final.iloc[0].MAE
    final["baseline_mae_improvement_pct"] = [0.0, improvement]
    pred = frozen.predict(test[FEATURES])
    errors = test[["order_id", "order_date", *FEATURES]].copy()
    errors["actual_order_total"] = test.order_total.to_numpy()
    errors["predicted_order_total"] = pred
    errors["residual"] = errors.actual_order_total - errors.predicted_order_total
    errors["abs_error"] = errors.residual.abs()
    errors = errors.sort_values("abs_error", ascending=False)

    validation = {
        "forbidden_feature_overlap": len(overlap),
        "strict_train_before_test": "PASS" if train.order_date.max() < test.order_date.min() else "FAIL",
        "selected_model_exists_in_train_cv": "PASS" if selected in set(cv.model) else "FAIL",
        "final_test_contains_baseline": "PASS" if "Baseline Mean" in set(final.model) else "FAIL",
        "final_test_contains_frozen_selected_model": "PASS" if "Frozen Selected Model" in set(final.model) else "FAIL",
        "test_rows_for_r2": "PASS" if len(test) >= 2 else "FAIL",
        "source_checks": "PASS" if all(source_checks.values()) else "FAIL",
    }
    if any(v != "PASS" for k, v in validation.items() if k != "forbidden_feature_overlap") or overlap:
        raise ValueError(f"Validation failed: {validation}")
    REPORTS.mkdir(exist_ok=True)
    cv.to_csv(REPORTS / "ch09_train_cv_folds.csv", index=False)
    summary.to_csv(REPORTS / "ch09_train_cv_summary.csv", index=False)
    final.to_csv(REPORTS / "ch09_final_test_metrics.csv", index=False)
    errors.to_csv(REPORTS / "ch09_final_test_predictions.csv", index=False)
    pd.DataFrame([validation]).to_csv(REPORTS / "ch09_regression_validation.csv", index=False)
    return {"train": train, "test": test, "cv": cv, "summary": summary,
            "selected": selected, "final": final, "errors": errors, "validation": validation,
            "cutoff": cutoff, "features": FEATURES}


if __name__ == "__main__":
    result = run()
    print(result["summary"].to_string(index=False))
    print(f"Selected (CV only): {result['selected']}")
    print(result["final"].to_string(index=False))
    print(result["validation"])
