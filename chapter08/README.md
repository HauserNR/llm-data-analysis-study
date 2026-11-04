# Chapter 08 제출물

주 제출물은 [chapter08.ipynb](chapter08.ipynb)이다. 공식 Notebook의 38개 셀 흐름을 유지하고 분석 질문 3개, 수치·표·그래프 3개, 해석·한계, 개인정보 점검, LLM 활용 기록과 최종 Validation을 같은 Notebook에 작성했다.

## 재현

저장소 루트에서 기존 `.venv` Python으로 실행한다.

```bash
.venv/bin/python scripts/run_midterm_project.py
```

또는 Notebook 커널을 재시작하고 전체 실행한다. 입력은 **루트 `data/raw/*.csv` 4개**이며, Chapter 06·07의 별도 processed 입력과 다르다. 원본과 기존 processed 파일을 덮어쓰지 않고 SHA-256으로 보존 여부를 확인한다. 고객 이름·원본 고객 ID가 포함된 전처리 결과는 메모리에만 두고, 공개 고객 CSV는 순위 라벨과 허용된 5개 컬럼만 저장한다.

필요 라이브러리는 pandas, numpy, matplotlib, IPython이다. Notebook 전체 실행에는 Jupyter·ipykernel, 실행 검증에는 nbformat·nbclient가 필요하다. 네트워크·API 키는 필요 없다. 한글 폰트는 Apple SD Gothic Neo, Malgun Gothic, NanumGothic, Noto Sans CJK KR 중 설치된 것을 사용한다. 실행 버전은 Notebook 첫 코드 출력에 기록한다.

- `reports/`: 공식 검증표·집계표·보고서, 추가 검증·그래프 검증·입력 해시·재실행 로그
- `images/`: 실제 집계에서 만든 PNG 3개 (Notebook에도 출력으로 포함)
- `src/`: 공식 코드를 바탕으로 이 장에 한정한 공통 모듈
- `references/`: 2026-11-04 내려받은 공식 가이드·템플릿·Notebook·공통 제출 기준·코드 원본

공식 코드 대비 변경: 출력 경로를 chapter08 아래로 분리하고 행 단위 processed 파일 저장을 생략했다. 그래프는 실제 matplotlib 객체의 값을 집계와 비교하고 월 금액·주문 수를 두 패널로 그린다. 추가 검증은 원본 ID 집합 기반의 독립 금액 계산, 원 단위 정확 총합 일치, 날짜·범위·주문 커버리지 등을 검사한다. 공식 8개 Validation 조건은 유지했다. 최종 재실행은 별도 Python 프로세스에서 수행한다.

LLM 보조로 작성했으며 자동 검증을 작성자의 직접 검토로 기록하지 않았다. 제출자는 Notebook의 수치·그래프·해석과 LLM 기록을 직접 확인해야 한다.

LMS 제출 주소는 [최종 Notebook 파일 URL](https://github.com/HauserNR/llm-data-analysis-study/blob/main/chapter08/chapter08.ipynb)이다. GitHub 업로드와 원격 렌더링 확인, LMS 제출은 로컬 파일 생성과 별개다.
