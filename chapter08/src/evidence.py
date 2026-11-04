"""Extra evidence: independent source calculation, column summaries and input hashes."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
from .midterm_project import build_key_duplicate_checks
from .preprocessing import validate_relationships

TABLES = ['customers', 'products', 'orders', 'order_items']
def input_manifest(root):
    rows=[]
    for folder in ['data/raw', 'data/processed']:
        for p in sorted((Path(root)/folder).glob('*.csv')):
            rows.append({'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    return pd.DataFrame(rows)

def extra_evidence(raw, processed, tables, report_dir):
    out = Path(report_dir)
    rows=[]
    for stage,data in [('raw',raw),('processed',processed)]:
        for name,df in data.items():
            for col in df:
                rows.append({'stage':stage,'dataset':name,'column':col,'dtype':str(df[col].dtype),'missing_count':int(df[col].isna().sum())})
    pd.DataFrame(rows).to_csv(out/'ch08_column_checks.csv',index=False)
    pk=build_key_duplicate_checks(raw)
    fk=validate_relationships(raw)
    pk.to_csv(out/'ch08_raw_pk_checks.csv',index=False)
    fk.to_csv(out/'ch08_raw_fk_checks.csv',index=False)
    # 독립 경로: merge 없이 원본 completed 주문 ID 집합으로 상세를 선택한다.
    ids=set(raw['orders'].loc[raw['orders']['order_status'].eq('completed'),'order_id'])
    ri=raw['order_items']; source=ri.loc[ri['order_id'].isin(ids)]
    raw_total=(source['quantity']*source['unit_price']).sum()
    completed=tables['completed_order_sales']
    orders=processed['orders']; items=processed['order_items']
    checks=[]
    def check(name, value, expected, ok):
        checks.append({'check':name,'value':str(value),'expected':str(expected),'status':'PASS' if bool(ok) else 'FAIL'})
    check('raw_pk_integrity',pk.status.eq('PASS').all(),True,pk.status.eq('PASS').all())
    check('raw_fk_integrity',fk.invalid_count.sum(),0,fk.invalid_count.eq(0).all())
    check('independent_raw_completed_amount',raw_total,completed.line_total.sum(),np.isclose(raw_total,completed.line_total.sum(),rtol=0,atol=1e-6))
    check('completed_scope',completed.order_status.eq('completed').all(),True,completed.order_status.eq('completed').all())
    check('completed_order_coverage',completed.order_id.nunique(),len(ids),set(completed.order_id)==ids)
    check('all_order_coverage',items.order_id.nunique(),len(orders),set(items.order_id)==set(orders.order_id))
    check('all_order_dates_valid',orders.order_date.isna().sum(),0,orders.order_date.notna().all())
    future=(orders.order_date>pd.Timestamp('2026-11-04')).sum()
    check('future_order_dates_asof_2026_11_04',future,0,future==0)
    check('category_not_missing',tables['completed_sales_items'].category.isna().sum(),0,tables['completed_sales_items'].category.notna().all())
    numeric=items[['quantity','unit_price','line_total']].to_numpy(dtype=float)
    check('positive_finite_amount_inputs',np.isfinite(numeric).all() and (numeric>0).all(),True,np.isfinite(numeric).all() and (numeric>0).all())
    check('integer_quantities',items.quantity.mod(1).eq(0).all(),True,items.quantity.mod(1).eq(0).all())
    for name in ['customers','products','orders','order_items']:
        check(name+'_rows_preserved',len(processed[name]),len(raw[name]),len(raw[name])==len(processed[name]))
    check('monthly_order_count_sum',tables['monthly_sales'].order_count.sum(),len(ids),tables['monthly_sales'].order_count.sum()==len(ids))
    check('customer_order_count_sum',tables['customer_sales_public'].order_count.sum(),len(ids),tables['customer_sales_public'].order_count.sum()==len(ids))
    month=tables['monthly_sales'].order_month.astype(str)
    expected=pd.period_range(orders.order_date.min(),orders.order_date.max(),freq='M').astype(str)
    check('calendar_months_complete',len(month),len(expected),list(month)==list(expected))
    for name in ['category_sales','monthly_sales','customer_sales']:
        amount=tables[name].total_sales.sum()
        check(name+'_exact_total',amount,raw_total,amount==raw_total)
    saved=pd.read_csv(out/'ch08_customer_sales.csv')
    safe=['customer_label','city','order_count','total_sales','avg_order_value']
    check('saved_customer_schema',list(saved),safe,list(saved)==safe)
    check('anonymous_rank_labels',saved.customer_label.is_unique,True,saved.customer_label.is_unique and saved.customer_label.str.fullmatch(r'Customer \d{2,}').all())
    result=pd.DataFrame(checks)
    result.to_csv(out/'ch08_additional_validation.csv',index=False)
    if not result.status.eq('PASS').all():
        raise ValueError(result.loc[result.status.eq('FAIL')].to_string(index=False))
    return result
