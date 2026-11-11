# Chapter 09 재현 및 출처

최종 제출: [chapter09.ipynb](chapter09.ipynb).

저장소 루트에서 환경 의존성을 설치한 뒤 실행:

```bash
python scripts/prepare_ch09_data.py
python scripts/run_regression_analysis.py
```

Notebook도 첫 코드 셀에서 입력 준비를 수행한다. 루트 및 chapter09 디렉터리에서 실행할 수 있다. 원본 CSV는 다시 생성하지 않는다. 공통 전처리로 data/processed의 4개 파일을 갱신하므로 다른 장의 이전 processed와 구별한다.

## 공식 자료 사용

2026-11-11에 GilbertMoon/llm-data-analysis-course의 아래 파일을 읽고 공식 Notebook 및 함수를 기반으로 작성했다.

- [공식 Notebook](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/notebooks/ch09_regression_analysis.ipynb)
- [가이드](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/chapter09/chapter09.md)
- [답안 양식](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/chapter09/templates/chapter09_assignment.md)
- [회귀 함수](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/src/regression.py)
- [공통 전처리](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/src/preprocessing.py)

src/regression.py, src/preprocessing.py, src/data_loader.py 및 실행 스크립트는 공식 구현을 바탕으로 한다. 추가한 부분은 Raw PK/FK·금액·날짜·행 손실 검사, Feature Audit의 시점·계산재료·ID 구분, Notebook 경로 보정과 답안·재현 비교다. 전체 데이터의 age 중앙값 대치와 city 대치를 제거해 결측 대체를 Pipeline 안에서만 수행하도록 했다. 현재 원본에는 해당 결측이 없어 공식 계산값은 바뀌지 않는다. 사람 검토 체크리스트는 Notebook 검토 내용을 반영했다. 스크립트에서 창 없는 환경에서도 그림을 저장하도록 Matplotlib Agg backend를 사용했다.

## 공개 범위

reports/ch09_regression_*_internal.csv는 식별자가 있어 로컬에만 생성하고 gitignore로 제외한다. 공개 Notebook·보고서·그래프에는 원본 주문 ID를 표시하지 않는다. 이전 버전의 중복된 주문 단위 CSV와 오차 CSV는 현재 제출 트리에서 제거했다. 기존 Git 이력에는 가상 데이터의 과거 산출물이 남아 있다.

## 평가 절차 수정

초기 제출물은 원문 접근 실패로 메시지에 제공된 요구사항만 반영하여 Baseline 자체를 선택 모델로 허용했다. 공식 가이드 확인 후 비베이스라인 선택, 공식 날짜 분할, CV R²·Train MAE, 지정 Evidence·공개 산출물을 반영했다. 이전 결과를 본 이력이 있으므로 완전히 독립적인 미래 성능 검증이 아니며, 새로운 미래 기간 검증이 필요하다는 제한을 Notebook에 명시했다.
