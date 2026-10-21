# Chapter 06 — 데이터를 보며 질문을 만드는 EDA

주 제출물은 [chapter06.ipynb](chapter06.ipynb)입니다. 작성자 송누리(HauserNR), 2026-10-21.

Chapter 05에서 저장한 processed 4개를 저장소 루트 data/processed에 그대로 복사했습니다. Notebook에서 SHA-256과 원본 바이트를 대조합니다. 기존 장의 파일은 변경하지 않았습니다.

루트에서 `.venv/bin/python chapter06/scripts/run_eda.py`를 실행하면 completed 범위의 카테고리·월별·고객별 결과를 다시 계산하여 Notebook CSV와 전체 표를 비교합니다. `src/eda.py`는 공식 모듈에서 completed 필터, Unknown 카테고리, NaT 월, 고객 결측 그룹 보존을 보완했습니다. 내려받은 공식 원본과 가이드는 references에 있습니다.

금액은 전처리 후 남은 completed 상세의 합계입니다. 주 집계는 미래·날짜 미상·상품 미연결을 별도 그룹에 포함하며 141,340,000원입니다. 날짜 유효·기준일 이전 비교 범위는 138,528,000원입니다. 주문 180건 중 상세가 남은 179건만 객단가 분모에 사용합니다. 원천 전체 매출, 수익성, 광고 효과를 뜻하지 않습니다.
