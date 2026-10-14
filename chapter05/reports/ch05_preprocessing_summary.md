# Chapter 05 데이터 전처리 요약

## 입력과 결과 파일
입력: data/raw/ (공식 전용 Raw, 원본 보존)
결과: data/processed/customers_clean.csv, products_clean.csv, orders_clean.csv, order_items_clean.csv

## 전처리 전 상태
| dataset     |   rows |   columns |   missing_cells |   duplicate_rows |   pk_missing |   pk_duplicates |
|:------------|-------:|----------:|----------------:|-----------------:|-------------:|----------------:|
| customers   |    152 |         6 |               6 |                2 |            0 |               2 |
| products    |    102 |         4 |               0 |                2 |            0 |               2 |
| orders      |    302 |         5 |               0 |                2 |            0 |               2 |
| order_items |    765 |         5 |               0 |                2 |            0 |               2 |

## 전처리 후 상태
| dataset     |   rows |   columns |   missing_cells |   duplicate_rows |   pk_missing |   pk_duplicates |
|:------------|-------:|----------:|----------------:|-----------------:|-------------:|----------------:|
| customers   |    150 |         6 |               2 |                0 |            0 |               0 |
| products    |     96 |         4 |               0 |                0 |            0 |               0 |
| orders      |    300 |         7 |               9 |                0 |            0 |               0 |
| order_items |    752 |         6 |               0 |                0 |            0 |               0 |

## 문자열·빈 문자열
| dataset     | column         |   trimmed |   empty_to_na |   missing_after |
|:------------|:---------------|----------:|--------------:|----------------:|
| customers   | name           |         0 |             0 |               0 |
| customers   | gender         |         0 |             0 |               0 |
| customers   | age            |         0 |             0 |               4 |
| customers   | city           |         5 |             0 |               2 |
| customers   | signup_date    |         0 |             0 |               0 |
| products    | product_name   |         0 |             0 |               0 |
| products    | category       |         3 |             0 |               0 |
| products    | price          |         0 |             0 |               0 |
| orders      | order_date     |         0 |             0 |               0 |
| orders      | payment_method |         5 |             0 |               0 |
| orders      | order_status   |         0 |             0 |               0 |
| order_items | quantity       |         0 |             0 |               0 |
| order_items | unit_price     |         0 |             0 |               0 |

## 숫자·날짜 변환 실패
| dataset     | column      | kind    |   rows_checked |   missing_before |   comma_removed |   new_failures |   missing_immediately_after |
|:------------|:------------|:--------|---------------:|-----------------:|----------------:|---------------:|----------------------------:|
| customers   | age         | numeric |            150 |                4 |               0 |              2 |                           6 |
| products    | price       | numeric |            100 |                0 |               4 |              2 |                           2 |
| order_items | quantity    | numeric |            763 |                0 |               0 |              5 |                           5 |
| order_items | unit_price  | numeric |            763 |                0 |               5 |              2 |                           2 |
| customers   | signup_date | date    |            150 |                0 |               0 |              2 |                           2 |
| orders      | order_date  | date    |            300 |                0 |               0 |              3 |                           3 |

## 처리 기준과 영향 건수
| dataset     | operation                                   |   affected |
|:------------|:--------------------------------------------|-----------:|
| customers   | exact duplicate removal                     |          2 |
| products    | exact duplicate removal                     |          2 |
| orders      | exact duplicate removal                     |          2 |
| order_items | exact duplicate removal                     |          2 |
| customers   | age median imputation (41.0)                |          6 |
| customers   | city Unknown                                |          2 |
| orders      | status normalization                        |         15 |
| products    | category alias normalization                |          3 |
| products    | numeric eligibility exclusion (unique rows) |          4 |
| order_items | numeric eligibility exclusion (unique rows) |         11 |

## 제외 사유 (원본 삭제 아님)
| dataset     |   primary_key | reason                                   |
|:------------|--------------:|:-----------------------------------------|
| products    |            18 | price:conversion_failed_or_missing;      |
| products    |            48 | price:nonpositive;                       |
| products    |            73 | price:conversion_failed_or_missing;      |
| products    |            95 | price:nonpositive;                       |
| order_items |            17 | quantity:conversion_failed_or_missing;   |
| order_items |            91 | quantity:conversion_failed_or_missing;   |
| order_items |           205 | quantity:conversion_failed_or_missing;   |
| order_items |           277 | unit_price:conversion_failed_or_missing; |
| order_items |           319 | quantity:conversion_failed_or_missing;   |
| order_items |           433 | unit_price:conversion_failed_or_missing; |
| order_items |           447 | quantity:conversion_failed_or_missing;   |
| order_items |           511 | quantity:nonpositive;                    |
| order_items |           579 | unit_price:nonpositive;                  |
| order_items |           612 | quantity:nonpositive;                    |
| order_items |           703 | quantity:nonpositive;                    |

## 검토 후 보류한 이상값 후보
| dataset     |   primary_key | column     | value               | reason                           | decision                        |
|:------------|--------------:|:-----------|:--------------------|:---------------------------------|:--------------------------------|
| customers   |            33 | age        | 150.0               | outside 0..120                   | retain; review business meaning |
| products    |            99 | price      | 9999999.0           | above review threshold 1,000,000 | retain; review business meaning |
| order_items |           738 | quantity   | 50.0                | above review threshold 20        | retain; review business meaning |
| order_items |           751 | quantity   | 100.0               | above review threshold 20        | retain; review business meaning |
| orders      |           256 | order_date | 2027-01-15 00:00:00 | after assignment date 2026-10-14 | retain; review business meaning |
| orders      |           287 | order_date | 2028-12-31 00:00:00 | after assignment date 2026-10-14 | retain; review business meaning |

## PK/FK 재검증
| check                                                |   invalid_count |
|:-----------------------------------------------------|----------------:|
| orders.customer_id exists in customers.customer_id   |               2 |
| order_items.order_id exists in orders.order_id       |               2 |
| order_items.product_id exists in products.product_id |              26 |

## 파생 컬럼
order_month, order_dayofweek, line_total = quantity × unit_price. 날짜 실패는 NaT로 유지하고 월/요일도 결측으로 유지한다.

## 업무 적용 한계
완전 중복만 제거한다. PK 충돌은 자동 삭제하지 않는다. age의 기존 결측과 숫자 변환 실패는 구분해 기록한 뒤 실습 기준으로 중앙값을 대체한다. city는 Unknown으로 남긴다. ID·날짜·금액을 임의로 복구하지 않는다. 비양수 금액·수량과 숫자 변환 실패 행은 정상 양수 분석 범위에서만 제외하고 사유를 보존한다. 없는 FK는 자동 제거하지 않는다. FK 불일치와 날짜 실패, 미래 날짜, 극단값이 남아 있으므로 clean이라는 이름만으로 완전한 데이터 또는 확정 매출로 해석할 수 없다. 매출 분석에서는 completed 상태, 연결 가능한 키, 유효 날짜, 분석 기간을 명시해야 한다.
