# Chapter 09 가이드·템플릿 점검 결과

점검일: 2026-11-12 (한국 시간)

판정 범위는 현재 제출본의 코드 실행 순서, 저장된 결과, 답안과 지정 산출물이다. PASS는 실제 운영 성능이나 한 번도 열람하지 않은 미래 Test의 독립성을 보증하지 않는다.

## 공식 가이드 전 항목

| 기준 | 확인 근거 | 현재 제출본 판정 |
|---|---|---|
| STEP 0 입력 준비 | 공통 raw 4종 → 전처리 → PK/FK 검증 → processed 생성, 원본 행 수 보존 | PASS |
| STEP 1 예측 문제·시점 | 답안 1: 단위·Target·시점·가용/불가 정보와 가정 | PASS |
| STEP 2 Leakage Audit | 허용 6열, 금지 11열 사유 표, 교집합 0 | PASS |
| STEP 3 Target·관계 | line_total 불일치 0, 두 합계 255,610,000원, one_to_one/many_to_one, 손상 데이터 3종 중단 확인 | PASS |
| STEP 4 시간 분할 | 237건: 2025-09-15~2026-06-25 / 63건: 2026-06-30~2026-09-15, 날짜 교집합 0 | PASS |
| STEP 5 Train 전처리 | Pipeline 내부 imputer/scaler/encoder, 최종 학습 median과 Train median 일치 | PASS |
| STEP 6 Baseline·후보 | Dummy Mean, Linear Regression, Random Forest | PASS |
| STEP 7 Train CV | TimeSeriesSplit 5 fold, CV MAE mean/std 및 R² mean 3모델 | PASS |
| STEP 8 모델 고정 | 비베이스라인 CV MAE 최소 Random Forest 선택 후 최종 평가 함수 호출 | PASS (현재 코드 순서) |
| STEP 9 Final Test | Baseline과 Frozen Random Forest 2개만 평가, Train MAE·Test MAE/RMSE/R²·개선율 | PASS |
| STEP 10 지표 해석 | 답안 6: 오차 단위·큰 오차·음수 R²·0.72% 개선 및 RMSE 악화 | PASS |
| STEP 11 오차 진단 | 사례 3건에 실제/예측/residual/abs_error·관찰·가설·추가 확인·한계 | PASS |
| STEP 12 Validation | 지정 CSV 6행 모두 PASS | PASS |
| STEP 13 새 실행 | 빈 임시 processed/report 폴더에서 재현, 기존 지표 일치 확인 | PASS |
| STEP 14 사용 판단 | 사용 보류 선택, CV 안정성·Test 지표·누수·시간·오차·한계와 개선 우선순위 | PASS |
| STEP 15 산출물 | Evidence 6종, Internal 2종(로컬), 공개 보고서 1종·그래프 2종 생성 | PASS |

## 공통 제출 기준과 템플릿

- 제출 정보 및 답안 1~11, 표·하위 질문·사례·최종 체크 존재. 원문 항목별 위치는 `template_audit.csv`에 기록했다.
- Notebook 코드 셀 15개 실행 완료, 오류·stderr 경고 출력 없음. Markdown 해석 및 지표·결과표가 실제 산출물과 일치한다.
- 템플릿 이미지 3개와 진단 그래프 2개를 포함한다. GitHub Preview에서 Markdown·표 및 이미지 5개의 로드 완료와 실제 크기(0보다 큼)를 확인했다.
- 공개 Notebook·보고서에는 식별자를 가진 실제 행을 표시하지 않는다. Feature Audit의 ID 열 이름과 Internal 파일 경로는 검토 설명을 위한 것이다.
- 실제 자격증명·비공개 업무자료·실제 고객 개인정보를 추가하지 않았다. 데이터는 공통 실습 가상 표본이다.
- 템플릿의 29개 체크박스: 완료 27개, 최종 판단 미선택 2개. LMS 제출은 2026-11-12 사용자 완료 확인을 반영했다. 미선택 판단 2개는 실패가 아닌 대안 선택지다.
- 모델링 사람 검토 체크리스트 12행은 현재 제출본 실행 절차 기준 PASS이며 `review_note`에 근거와 시점 가정을 기록했다. 자동 Validation 6행의 PASS와 구별한다.

## 남아 있는 제한과 사용자 작업

1. 이전 버전에서 Test 일부의 결과를 열람했다. 현재 모델은 Train CV로 고정했으나 이 이력 때문에 엄격한 독립 미래 평가를 완전히 만족했다고 주장하지 않는다. 별도의 새 미래 데이터가 필요하다. 점수를 높이려고 모델·데이터를 바꾸지 않았다.
2. 예측 시점에 고객 속성·결제수단을 알 수 있다는 것은 교육용 문제의 가정이다. 당시 기록 시각은 데이터에 없어 운영 가용성을 검증하지 못했다.
3. LMS 제출은 2026-11-12 사용자로부터 완료 확인을 받았으며 제출 체크를 반영했다.

빈 폴더 재현 및 거부 검사는 `reproduction_checks.json`의 16개 항목이 모두 true다. 현재의 코드·답안 항목 충족과 위 평가 한계는 별개로 해석해야 한다.

## 기준 문서

- https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/SUBMISSION_GUIDE.md
- https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/CHAPTER_SUBMISSION_MATRIX.md
- https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/chapter09/chapter09.md
- https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/chapter09/templates/chapter09_assignment.md
- https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/notebooks/ch09_regression_analysis.ipynb
