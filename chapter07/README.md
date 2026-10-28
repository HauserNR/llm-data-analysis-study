# Chapter 07 제출물

주 제출물: [실행된 chapter07.ipynb](chapter07.ipynb)

질문 6개, 그래프 6종, 그래프 전 집계표, 실제 matplotlib 객체와 집계의 교차 검증,
그래프별 관찰·판단·업무 의미·한계를 Notebook에 담았다.
`images/`에는 PNG, `reports/`에는 개인 키 없는 집계표와 검증 결과를 저장한다.

## 재현

저장소 루트 또는 `chapter07/`에서 Python 커널로 Notebook 전체를 실행한다.
전체 그래프·검증 보고서만 재생성하려면 저장소 루트에서 실행한다.

```bash
.venv/bin/python chapter07/scripts/run_visualization.py
```

입력은 루트 `data/processed/*_clean.csv` 4개이며 `chapter05/data/processed/` 사본과
바이트 일치를 검사한다. 입력을 다시 전처리하거나 덮어쓰지 않는다.
금액은 completed 상세의 `quantity × unit_price` 합계로, 회계상 순매출이 아니다.
월별만 날짜 유효·2026-10-28 이하로 제한한다. 상세 범위·문제 금액은 Notebook에 명시했다.

필요 환경: pandas, numpy, matplotlib, scipy(탐색적 Spearman 상관), IPython,
Jupyter 및 한글 폰트(Apple SD Gothic Neo/맑은 고딕/NanumGothic/Noto Sans CJK KR 등).
실행 환경의 버전은 Notebook 첫 출력에 기록한다. API 키와 네트워크는 필요 없다.

## 참고 자료와 보완

2026-10-28에 확인한 공식 자료의 사본을 `references/`에 보관했다.

- [공식 skeleton](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/notebooks/ch07_visualization.ipynb)
- [단계별 실습](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/chapter07/chapter07.md)
- [답안 템플릿](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/practice/chapter07/templates/chapter07_assignment.md)
- [공식 시각화 모듈](https://github.com/GilbertMoon/llm-data-analysis-course/blob/main/src/visualization.py)
- [학생용 블로그 가이드](https://blog.naver.com/dev-dog/224414845375)

공식 순서와 질문 구성을 따르되, 개인 데이터의 FK 미연결·날짜 문제를 숨기지 않도록
집계 정책을 명시하고 보존·제외 금액 대조, 결측 월 처리, 실제 그래프 객체 검증,
극단값 보조 비교, 고객 순위 익명화를 추가했다. 답안 템플릿은 별도 제출 문서 대신
Notebook Markdown에 작성했다. 반복 실행 코드는 이 장의 `src/`로 분리했다.

LMS 제출 URL:
[chapter07/chapter07.ipynb](https://github.com/HauserNR/llm-data-analysis-study/blob/main/chapter07/chapter07.ipynb)

GitHub 표시를 확인한 뒤 이 파일 URL을 제출한다. LMS 제출은 별도 절차다.
