"""Chapter 07: processed 입력, 범위별 집계, 실제 matplotlib 객체 검증.

공식 src/visualization.py의 질문·검증·6종 그래프 흐름을 참고했다.
이 제출 데이터에 남은 FK 불일치와 날짜 문제는 별도 표에 보존한다.
"""
from pathlib import Path
import hashlib
import json

import matplotlib.pyplot as plt
from matplotlib import font_manager, dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np
import pandas as pd

AS_OF = pd.Timestamp("2026-10-28")
FILENAMES = {
    "category": "graph01_category.png", "monthly": "graph02_monthly.png",
    "price": "graph03_price.png", "scatter": "graph04_scatter.png",
    "customers": "graph05_customers.png", "status": "graph06_status.png",
}
FORMAT = FuncFormatter(lambda value, _: f"{value:,.0f}")


def setup_korean_font():
    installed = {f.name for f in font_manager.fontManager.ttflist}
    candidates = ["Apple SD Gothic Neo", "AppleGothic", "Malgun Gothic",
                  "NanumGothic", "Noto Sans CJK KR", "Noto Sans KR"]
    selected = next((f for f in candidates if f in installed), None)
    if selected is None:
        raise RuntimeError("한글 폰트를 설치한 뒤 다시 실행하세요: Noto Sans CJK KR 등")
    plt.rcParams.update({"font.family": selected, "axes.unicode_minus": False,
                         "font.size": 11, "axes.titlesize": 14,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.dpi": 110, "savefig.dpi": 150})
    return selected


def validation_row(label, actual, expected):
    passed = bool(np.allclose(actual, expected, rtol=0, atol=1e-6, equal_nan=True))
    if not passed:
        raise AssertionError(f"검증 실패: {label}")
    return {"check": label, "actual": float(np.nansum(actual)),
            "expected": float(np.nansum(expected)), "passed": passed}


def prepare_visualization_data(project_root):
    root = Path(project_root)
    data, manifest = {}, []
    keys = {"customers": "customer_id", "products": "product_id",
            "orders": "order_id", "order_items": "order_item_id"}
    required = {
        "customers": {"customer_id"},
        "products": {"product_id", "category", "price"},
        "orders": {"order_id", "customer_id", "order_date", "order_status"},
        "order_items": {"order_item_id", "order_id", "product_id", "quantity",
                        "unit_price", "line_total"},
    }
    for name, key in keys.items():
        filename = name + "_clean.csv"
        path = root / "data/processed" / filename
        original = root / "chapter05/data/processed" / filename
        if path.read_bytes() != original.read_bytes():
            raise AssertionError(f"Chapter 05 입력과 다름: {filename}")
        # 이름·주소 등 불필요한 개인정보는 읽지 않는다.
        frame = pd.read_csv(path, usecols=lambda c: c in required[name])
        if not required[name].issubset(frame.columns):
            raise ValueError(f"필수 컬럼 누락: {name}")
        if frame[key].isna().any() or not frame[key].is_unique:
            raise ValueError(f"PK 결측/중복: {name}.{key}")
        data[name] = frame
        manifest.append({"file": filename, "rows": len(frame),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "same_as_ch05": True})
    customers, products, orders, items = (data[k] for k in keys)
    for frame, columns in [(products, ["price"]),
                            (items, ["quantity", "unit_price", "line_total"])]:
        for col in columns:
            frame[col] = pd.to_numeric(frame[col], errors="raise")
            if not np.isfinite(frame[col]).all() or (frame[col] <= 0).any():
                raise ValueError(f"숫자 품질 점검 실패: {col}")
    if products.category.isna().any() or orders.order_status.isna().any():
        raise ValueError("카테고리 또는 주문 상태 결측")
    checks = [validation_row("상세별 line_total = quantity × unit_price",
                             items.line_total, items.quantity * items.unit_price)]
    orders["order_date"] = pd.to_datetime(orders.order_date, errors="coerce")
    # CSV에 저장된 파생 월 대신 실제 변환한 날짜에서 다시 계산한다.
    orders["month"] = orders.order_date.dt.to_period("M")
    joined = items.merge(orders, on="order_id", how="left",
                         validate="many_to_one", indicator=True)
    orphan = joined.loc[joined._merge.eq("left_only")]
    completed = joined.loc[joined.order_status.eq("completed")].drop(columns="_merge")
    if completed.empty:
        raise ValueError("완료 주문 상세가 없음")
    enriched = completed.merge(products, on="product_id", how="left",
                                validate="many_to_one", indicator="product_match")
    enriched["category"] = enriched.category.fillna("상품 미연결")
    total = completed.line_total.sum()
    category = enriched.groupby("category", as_index=False).agg(
        total_quantity=("quantity", "sum"), completed_amount=("line_total", "sum"))
    category = category.sort_values("completed_amount", ascending=False).reset_index(drop=True)
    category["amount_ratio_pct"] = category.completed_amount / total * 100
    category["weighted_unit_price"] = category.completed_amount / category.total_quantity

    invalid = completed.loc[completed.order_date.isna()]
    future = completed.loc[completed.order_date.gt(AS_OF)]
    dated = completed.loc[completed.order_date.le(AS_OF)]
    observed_orders = orders.loc[orders.order_date.le(AS_OF)]
    calendar = pd.period_range(observed_orders.month.min(), observed_orders.month.max(), freq="M")
    monthly = dated.groupby("month").agg(
        completed_amount=("line_total", "sum"), completed_order_count=("order_id", "nunique"))
    monthly = monthly.reindex(calendar).rename_axis("month")
    monthly["all_order_rows"] = observed_orders.groupby("month").size().reindex(calendar, fill_value=0)
    # 해당 월 orders가 전혀 없으면 수집 여부 불명: NaN을 유지해 선을 끊는다.
    file_zero = monthly.completed_amount.isna() & monthly.all_order_rows.gt(0)
    monthly.loc[file_zero, ["completed_amount", "completed_order_count"]] = 0
    monthly["coverage"] = np.where(monthly.all_order_rows.eq(0), "관측 없음/NaN",
                                    np.where(file_zero, "파일 내 완료 상세 0", "완료 상세 관측"))
    monthly["average_completed_order_amount"] = (
        monthly.completed_amount / monthly.completed_order_count.replace(0, np.nan))
    monthly = monthly.reset_index()
    monthly["month_start"] = monthly.month.dt.to_timestamp()

    matched = enriched.loc[enriched.product_match.eq("both")]
    product_sales = matched.groupby(["product_id", "price"], as_index=False).agg(
        completed_quantity=("quantity", "sum"), completed_amount=("line_total", "sum"))
    # 공개 표에는 상품 키도 필요 없어 가격·수량·금액만 남긴다.
    scatter = product_sales[["price", "completed_quantity", "completed_amount"]].copy()
    known_customers = completed.customer_id.isin(customers.customer_id)
    customer_sales = completed.loc[known_customers].groupby("customer_id", as_index=False).agg(
        completed_order_count=("order_id", "nunique"), completed_amount=("line_total", "sum"))
    customer_sales = customer_sales.sort_values(
        ["completed_amount", "customer_id"], ascending=[False, True]).reset_index(drop=True)
    customer_sales["anonymous_rank"] = [f"구매금액 순위 {i:02d}" for i in range(1, len(customer_sales) + 1)]
    customer_sales["average_completed_order_amount"] = (
        customer_sales.completed_amount / customer_sales.completed_order_count)
    customer_sales = customer_sales.drop(columns="customer_id")
    status = orders.order_status.value_counts().rename_axis("order_status").reset_index(name="order_count")
    status["order_ratio_pct"] = status.order_count / len(orders) * 100

    quality = pd.DataFrame([
        ("주문 미연결 상세: 상태 불명으로 completed 범위 밖", len(orphan), orphan.line_total.sum()),
        ("completed 상품 미연결: 카테고리 별도/산점도 제외", int(enriched.product_match.eq("left_only").sum()),
         enriched.loc[enriched.product_match.eq("left_only"), "line_total"].sum()),
        ("completed 날짜 결측: 월별만 제외", len(invalid), invalid.line_total.sum()),
        ("completed 기준일 이후: 월별만 제외", len(future), future.line_total.sum()),
        ("completed 고객 미연결: 고객 순위 제외", int((~known_customers).sum()),
         completed.loc[~known_customers, "line_total"].sum()),
    ], columns=["issue_and_policy", "detail_rows", "amount_krw"])
    scope = pd.DataFrame([
        ("전체 주문 헤더", len(orders), np.nan),
        ("completed 주문 헤더", int(orders.order_status.eq("completed").sum()), np.nan),
        ("상세가 남은 completed 주문", completed.order_id.nunique(), total),
        ("카테고리 전체(미연결 포함)", len(enriched), category.completed_amount.sum()),
        ("월별(유효 날짜·기준일 이전)", len(dated), dated.line_total.sum()),
        ("산점도(상품 연결 completed 상세)", len(matched), matched.line_total.sum()),
        ("고객 순위(고객 연결 completed 상세)", int(known_customers.sum()),
         completed.loc[known_customers, "line_total"].sum()),
    ], columns=["scope", "count_in_scope", "amount_krw"])
    scope.insert(2, "count_unit", ["주문", "주문", "주문", "상세 행", "상세 행", "상세 행", "상세 행"])
    checks += [
        validation_row("병합 후 상세 행 수 보존", len(joined), len(items)),
        validation_row("상품 병합 후 completed 상세 보존", len(enriched), len(completed)),
        validation_row("completed 독립 isin 필터 총합", items.loc[items.order_id.isin(
            orders.loc[orders.order_status.eq("completed"), "order_id"]), "line_total"].sum(), total),
        validation_row("카테고리 총합(상품 미연결 포함)", category.completed_amount.sum(), total),
        validation_row("월별 + 날짜 결측 + 미래 = completed", monthly.completed_amount.sum()
                       + invalid.line_total.sum() + future.line_total.sum(), total),
        validation_row("상품별 + 상품 미연결 = completed", scatter.completed_amount.sum()
                       + enriched.loc[enriched.product_match.eq("left_only"), "line_total"].sum(), total),
        validation_row("익명 고객별 + 고객 미연결 = completed", customer_sales.completed_amount.sum()
                       + completed.loc[~known_customers, "line_total"].sum(), total),
        validation_row("상태별 주문 수 총합", status.order_count.sum(), len(orders)),
    ]
    # Chapter 06과 같은 입력·정의의 두 주요 결과를 독립 대조한다.
    old_category = root / "chapter06/reports/ch06_category_sales.csv"
    if old_category.exists():
        old = pd.read_csv(old_category)
        checks.append(validation_row("Chapter 06 completed 총합 대조", total, old.total_sales.sum()))
    return {"products": products, "orders": orders, "completed": completed,
            "category": category, "monthly": monthly, "scatter": scatter,
            "customers": customer_sales, "status": status, "quality": quality,
            "scope": scope, "input_manifest": pd.DataFrame(manifest),
            "validation": pd.DataFrame(checks), "total": float(total)}


def format_axis(ax, direction="y"):
    axis = ax.yaxis if direction == "y" else ax.xaxis
    axis.set_major_formatter(FORMAT)
    ax.grid(axis=direction, alpha=0.18)
    ax.set_axisbelow(True)


def plot_category(d):
    t = d["category"]
    fig, ax = plt.subplots(figsize=(11, 5.7))
    bars = ax.bar(t.category, t.completed_amount,
                  color=["#9199a2" if c == "상품 미연결" else "#35658a" for c in t.category])
    ax.bar_label(bars, labels=[f"{v:,.0f}" for v in t.completed_amount], padding=4, fontsize=10)
    bars[-1].set_hatch("//")
    ax.set(title="카테고리별 completed 상세 금액 | 날짜 제한 없음",
           xlabel="카테고리 (금액 내림차순, 미연결 별도)", ylabel="완료 주문 상세 금액 (원)",
           ylim=(0, t.completed_amount.max() * 1.18))
    format_axis(ax)
    fig.tight_layout()
    checks = [validation_row("그래프1 막대 높이 = 집계표 전체", [b.get_height() for b in bars], t.completed_amount),
              validation_row("그래프1 범주 순서", [x.get_text() for x in ax.get_xticklabels()] == t.category.tolist(), True),
              validation_row("그래프1 금액 축 시작 0", ax.get_ylim()[0], 0)]
    return fig, checks


def plot_monthly(d):
    t = d["monthly"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    line, = axes[0].plot(t.month_start, t.completed_amount, marker="o", color="#35658a")
    for x, value in zip(t.month_start, t.completed_amount):
        if pd.notna(value):
            axes[0].annotate(f"{value / 10000:,.1f}", (x, value), xytext=(0, 8),
                             textcoords="offset points", ha="center", fontsize=9)
    axes[0].set(title="월별 completed 상세 금액 | 유효 날짜·2026-10-28까지",
                ylabel="금액 (원) · 점 위 숫자는 만원", ylim=(0, t.completed_amount.max() * 1.22))
    count_line, = axes[1].plot(t.month_start, t.completed_order_count, marker="s",
                              linestyle="--", color="#98653a", label="상세가 남은 완료 주문 수")
    axes[1].set(ylabel="완료 주문 수 (건)", xlabel="주문 월 (시간순)", ylim=(0, t.completed_order_count.max() * 1.35))
    axes[1].legend(loc="upper left", fontsize=9)
    axes[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].set_xticks(t.month_start)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(axes[1].get_xticklabels(), rotation=45, ha="right")
    for ax in axes:
        format_axis(ax)
    fig.text(0.08, 0.01, "관측 월만 표시 · 9~10월을 0으로 추가하지 않음 · 첫/마지막 달 수집 완전성 미확인", fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    checks = [validation_row("그래프2 선 금액 = 월별 집계 전체", line.get_ydata(), t.completed_amount),
              validation_row("그래프2 주문 수 = 월별 집계 전체", count_line.get_ydata(), t.completed_order_count),
              validation_row("그래프2 실제 x 좌표 = 월 시작일", mdates.date2num(line.get_xdata()), mdates.date2num(t.month_start)),
              validation_row("그래프2 월 오름차순", t.month.is_monotonic_increasing, True)]
    return fig, checks


def plot_price(d):
    prices = d["products"].price.to_numpy()
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey="row")
    checks = []
    regular = prices[prices <= 1_000_000]
    for column, bins in enumerate([10, 20, 30]):
        for row, values in enumerate([prices, regular]):
            ax = axes[row, column]
            counts, edges, patches = ax.hist(values, bins=bins, color="#35658a", edgecolor="white")
            expected, expected_edges = np.histogram(values, bins=bins)
            checks += [validation_row(f"그래프3 행{row + 1} bins={bins} 구간별 빈도", counts, expected),
                       validation_row(f"그래프3 행{row + 1} bins={bins} 실제 막대 높이", [p.get_height() for p in patches], expected),
                       validation_row(f"그래프3 행{row + 1} bins={bins} 구간 경계", edges, expected_edges)]
            ax.set(title=f"{'전체' if row == 0 else '보조: 100만원 이하'} {len(values)}개 · bins={bins}",
                   xlabel="상품 마스터 가격 (원)", ylabel="상품 수 (개)", ylim=(0, None))
            ax.xaxis.set_major_locator(MaxNLocator(3))
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.xaxis.set_major_formatter(FORMAT)
            ax.grid(axis="y", alpha=0.18)
    fig.suptitle("전체 상품 마스터 가격 분포 | 위: 극단값 포함, 아래: 범위 제한 보조 비교", y=1.01)
    fig.text(0.06, 0.01, f"전체 {len(prices)}개는 삭제 없이 유지 · 보조 패널에서만 {len(prices) - len(regular)}개 제외 · 구간 수에 따라 세부 모양은 달라짐", fontsize=10)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    return fig, checks


def plot_scatter(d):
    t = d["scatter"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    collections = []
    for ax in axes:
        points = ax.scatter(t.price, t.completed_quantity, s=40, alpha=0.65, color="#35658a", edgecolors="white", linewidths=0.4)
        collections.append(points)
        ax.set(xlabel="상품 마스터 가격 (원)", ylabel="completed 판매 수량 (개)", ylim=(0, t.completed_quantity.max() * 1.15))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(alpha=0.18)
    axes[0].set(title="선형 축 · 전체 극단값 유지", xlim=(0, t.price.max() * 1.06))
    axes[0].xaxis.set_major_formatter(FORMAT)
    axes[0].xaxis.set_major_locator(MaxNLocator(4))
    axes[1].set_xscale("log")
    axes[1].set_title("보조: x 로그 축 · 같은 모든 상품")
    fig.suptitle(f"가격과 완료 판매 수량 | 한 점 = 상품 1개, {len(t)}개 · 관계 ≠ 원인", y=1.01)
    fig.text(0.07, 0.01, "가격은 마스터 현재값, 거래단가와 다를 수 있음 · 상품 미연결은 제외 · 미판매 상품을 포함한 수요 분석이 아님", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    checks = [validation_row(f"그래프4 패널{i + 1} 점 좌표 = 상품별 가격·수량", p.get_offsets(), t[["price", "completed_quantity"]])
              for i, p in enumerate(collections)]
    checks.append(validation_row("그래프4 로그 축 명시", axes[1].get_xscale() == "log", True))
    return fig, checks


def plot_customers(d):
    t = d["customers"].head(10)
    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.barh(t.anonymous_rank, t.completed_amount, color="#35658a")
    ax.bar_label(bars, labels=[f"{v:,.0f}원 · {n}건" for v, n in zip(t.completed_amount, t.completed_order_count)], padding=5, fontsize=10)
    ax.invert_yaxis()
    ax.set(title="고객 연결 completed 상세 금액 상위 10명 | 날짜 제한 없음",
           xlabel="완료 주문 상세 금액 (원)", ylabel="금액순 익명 순위 (원본 ID 아님)",
           xlim=(0, t.completed_amount.max() * 1.32))
    format_axis(ax, "x")
    fig.tight_layout()
    checks = [validation_row("그래프5 막대 너비 = Top10 집계 전체", [b.get_width() for b in bars], t.completed_amount),
              validation_row("그래프5 순위 라벨만 표시", [x.get_text() for x in ax.get_yticklabels()] == t.anonymous_rank.tolist(), True),
              validation_row("그래프5 금액 축 시작 0", ax.get_xlim()[0], 0)]
    return fig, checks


def plot_status(d):
    t = d["status"]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.bar(t.order_status, t.order_count, color="#35658a")
    ax.bar_label(bars, labels=[f"{n}건 ({pct:.1f}%)" for n, pct in zip(t.order_count, t.order_ratio_pct)], padding=4)
    ax.set(title="전체 주문 상태 분포 | 주문 헤더 300건, 날짜 제한 없음",
           xlabel="주문 상태 (건수 내림차순)", ylabel="주문 수 (건)", ylim=(0, t.order_count.max() * 1.22))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    format_axis(ax)
    fig.tight_layout()
    return fig, [validation_row("그래프6 막대 높이 = 상태별 주문 수", [b.get_height() for b in bars], t.order_count),
                 validation_row("그래프6 전체 주문 헤더 분모", t.order_count.sum(), len(d["orders"]))]


PLOTTERS = {"category": plot_category, "monthly": plot_monthly, "price": plot_price,
            "scatter": plot_scatter, "customers": plot_customers, "status": plot_status}


def save_tables(d, report_dir, chart_checks):
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    for name in ["category", "monthly", "scatter", "customers", "status", "scope", "quality", "input_manifest", "validation"]:
        d[name].to_csv(report_dir / f"{name}.csv", index=False)
    pd.DataFrame(chart_checks).to_csv(report_dir / "chart_validation.csv", index=False)
    result = {"as_of": str(AS_OF.date()), "completed_amount": d["total"],
              "aggregate_checks": len(d["validation"]), "chart_checks": len(chart_checks),
              "all_passed": bool(d["validation"].passed.all() and all(c["passed"] for c in chart_checks)),
              "figures": list(FILENAMES.values())}
    (report_dir / "execution_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def create_all_figures(d, image_dir, report_dir):
    image_dir = Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    checks = []
    for name, plotter in PLOTTERS.items():
        fig, validations = plotter(d)
        fig.savefig(image_dir / FILENAMES[name], bbox_inches="tight", facecolor="white")
        plt.close(fig)
        checks.extend(validations)
    return save_tables(d, report_dir, checks)
