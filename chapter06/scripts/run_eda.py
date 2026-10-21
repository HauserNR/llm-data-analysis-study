"""저장소 루트에서 python chapter06/scripts/run_eda.py 실행."""
from pathlib import Path
import sys
import pandas as pd

chapter = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(chapter))
from src.eda import load_processed_sales_data, run_basic_eda

frames = load_processed_sales_data(chapter.parent / 'data/processed')
results = run_basic_eda(frames)
out = chapter / 'reports' / 'script'
out.mkdir(exist_ok=True)
for name, frame in results.items():
    frame.to_csv(out / f'ch06_{name}.csv', index=False, encoding='utf-8-sig')
for name, key in [('category_sales','category'),('monthly_sales','order_month'),('customer_sales','customer_id')]:
    notebook = pd.read_csv(chapter/'reports'/f'ch06_{name}.csv')
    result = pd.read_csv(out/f'ch06_{name}.csv')
    pd.testing.assert_frame_equal(notebook.sort_values(key).reset_index(drop=True),
                                  result.sort_values(key).reset_index(drop=True))
print('독립 스크립트 ↔ Notebook 3개 집계 전체 표 일치')
print('completed 원본·카테고리·월별 합계:',results['category_sales'].total_sales.sum(),results['monthly_sales'].total_sales.sum())
