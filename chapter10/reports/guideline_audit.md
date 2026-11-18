# Chapter10 요구사항 대응

확인 기준은 공식 가이드·공식 Notebook·답안 템플릿·공통 제출 기준이며, 정확한 원본 커밋과 파일 해시는 `source_manifest.json`에 기록했다.

| 공식 STEP | 구현 및 확인 근거 |
| --- | --- |
| 0 입력 준비 | 공통 Raw 4종 사용, PK/FK·중복·필수값·금액·행 보존 검사 후 Processed 생성 |
| 1 Target Contract | Notebook 1절: completed=0, cancelled=1, refunded/기타 제외, 접수 시점·라벨 기간의 한계 |
| 2 주문 특징 | 3절: line_total 재계산, 상세 행 수·총수량·금액 합, 총합·중복·결측 assert |
| 3 병합·Feature Audit | 2~3절: one_to_one/many_to_one, 행 수 보존·미매칭 0, 허용·금지 목록 |
| 4 클래스·Baseline | 4~5절: 완료184/취소64, Dummy의 Accuracy와 취소 탐지 실패 설명 |
| 5 분할 | 6절: 148/50/50 stratified random split, 두 클래스·주문 중복·누락 검사, 고객 중복 수 공개 |
| 6 Pipeline | 5절: 세 후보별 Train median·scaler mean·fit 표본 수·encoder 범주 확인 |
| 7 모델 선택 | 5~7절: Validation에서 비Dummy F1→Recall→Precision 규칙으로 Logistic Regression 선택 |
| 8 Threshold | 8절: 사전 범위13개 값, Precision/Recall/F1/FP/FN 비교, 0.20 선택 이유·한계 |
| 9 Final Test | 10절: freeze 파일 및 학습 상태 해시 확인 후 한 후보 평가, 선택 이후 재학습 없음 |
| 10 FP/FN | 9절: FP32/FN1 의미, 업무 영향의 가정, 비용·개입 효과·처리 용량 추가 데이터 |
| 11 공개 범위 | 11절: 새 record_id·공개6열 allowlist, 내부 CSV gitignore |
| 12 Evidence | 12절: 필수CSV·요약MD 저장, 자동10항목과 별도 사람 검토, Raw WARN을 구분 |
| 13 재실행 | 마지막 코드 셀: 루트에서 두 필수 명령 새 프로세스 실행, 공개 파일 바이트 비교·Raw 불변 |
| 14 사용 판단 | 13절: 현재 사용 보류, Baseline·지표·Threshold·FP/FN·미래 검증·인과 한계 |
| LLM 보조 검증 | Prompt 및 7개 채택/수정/보류 기록과 코드·Validation 근거 |
| 제출 Evidence | 실행 셀 Output·그림4개, 템플릿15영역+추가2영역 대응표 |

가입일 역전은 원본 품질 WARN이며 원본이 정상이라고 표시하지 않았다. 해당 날짜 Feature의 전체 제외로 현재 모델 입력 위험을 완화한 상태다. 해결되지 않은 필수 FAIL이 있으면 완료로 보지 않는다. GitHub 원격 표시 확인과 LMS 제출은 아직 수행하지 않아 최종 체크에서 미체크로 남겼다.
