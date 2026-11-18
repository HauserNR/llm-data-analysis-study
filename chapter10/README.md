# Chapter 10 제출물

주 제출 파일은 [chapter10.ipynb](chapter10.ipynb)다. 공식 Notebook을 복사하여 답안 템플릿의 13개 절, 실제 실행 결과, 그래프, LLM 검토, 자동 Validation, 재실행 비교를 추가했다.

저장소 루트의 Python 환경에서 실행한다.

```bash
python -m pip install -r requirements.txt
python scripts/prepare_ch10_data.py
python scripts/run_classification_analysis.py
```

Notebook은 루트와 `chapter10/` 양쪽에서 실행할 수 있다. 마지막 실행 셀은 두 명령을 새 프로세스로 재실행하고 공개 산출물을 바이트 단위로 비교한다. 첫 실행부터 Test를 보고 Feature·후보·분할·선택 규칙을 변경하지 않았다. 반복 실행은 재현성 확인이며 새로운 독립 평가가 아니다.

입력은 기존 `data/raw/`의 공통 가상 데이터 4종이다. Raw를 재생성하지 않는다. 기존 `data/processed/`는 현재 공통 Raw와 달라 준비 스크립트로 다시 생성한다. Chapter05 전용 오류 탐지 데이터를 혼용하지 않는다. 고객 150명·상품 100개·주문 300건·상세 764행이며, 환불 52건을 제외한 완료 184건·취소 64건으로 분석한다.

원본에서 가입일이 주문일보다 늦은 주문 48건(분류 범위 34건)을 발견했다. 날짜를 추정해 바꾸거나 해당 주문을 제거하지 않고, 학습 전에 `signup_date`와 `days_since_signup`을 전체 모델 입력에서 제외했다. Raw 품질 표에는 WARN이 남으며, 그 Feature 제외를 포함한 모델 입력 계약을 별도로 검증한다.

숫자/범주 전처리와 세 고정 후보는 공식 구현을 따른다. Stratified 60/20/20 분할, seed 42, Validation F1 우선으로 Logistic Regression을 선택하고 0.20~0.80 범위에서 Threshold 0.20을 선택했다. Final Test 전에 `reports/ch10_selection_frozen.json`을 저장하고 학습 상태 불변을 확인한다.

Test는 Accuracy 0.34, Precision 0.2727, Recall 0.9231, F1 0.4211, TN5/FP32/FN1/TP12다. 취소 탐지 수치가 높아도 대부분 주문을 경고하여 선별 효용이 확인되지 않았으므로 최종 판단은 **현재 사용 보류**다. 실제 비용·미래 검증·시점 이력·공정성은 추가 확인이 필요하다.

`reports/ch10_*_internal.csv`는 식별자 추적용 로컬 산출물로 gitignore 처리했다. 공개 Prediction은 `record_id`, `actual_is_cancelled`, `predicted_is_cancelled`, `cancel_probability`, `model`, `threshold` 여섯 열만 사용한다. 그림 4개는 Notebook Output에 포함되며 `images/`에도 저장한다.

공식 자료의 커밋·파일 해시는 [source_manifest.json](reports/source_manifest.json)에, 템플릿 대응은 [template_audit.csv](reports/template_audit.csv)에 기록한다. 자동 분류 계약 검사와 사람 검토를 구분한다. 공식 사람 검토 양식의 빈 체크는 자동 PASS로 바꾸지 않고 별도 [ch10_human_review.csv](reports/ch10_human_review.csv)에 근거 절을 기록했다.

2026-11-18 Notebook·이미지·코드·공개 산출물을 GitHub `main`에 커밋·푸시했다. 로그인하지 않은 공개 GitHub Preview에서 답안·표 39개·그래프 4개의 실제 로드와 크기를 확인했고, 원격 Notebook·이미지 4개의 바이트가 로컬 파일과 일치함도 확인했다. 근거는 [github_rendering_checks.json](reports/github_rendering_checks.json)에 기록한다. GitHub Notebook에서 체크 상태가 보이도록 ☑/☐ 기호를 사용한다. LMS 제출은 아직 수행하지 않았으며 사용자가 아래 최종 파일 URL을 제출하면 된다.

최종 제출 대상 URL: https://github.com/HauserNR/llm-data-analysis-study/blob/main/chapter10/chapter10.ipynb
