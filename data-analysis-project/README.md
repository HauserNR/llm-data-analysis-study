# KBO의 ‘운 없던 타자’는 다음 시즌 반등할까?

개인별 과거 BABIP에 리그 환경을 반영한 기준선을 만들고, 기준보다 낮은 BABIP가 다음 시즌 타율 회복과 관련되는지 검증하는 학기 데이터분석 프로젝트입니다.

- [1차 프로젝트 계획서](01_proposal/01_proposal.md)
- [데이터 출처·라이선스·다운로드 방법](data/raw/README.md)
- [확보 자료의 구조 점검](data/data_audit.json)
- [구조 점검 재현 코드](scripts/inspect_data.py)

2026-10-09 기준으로 KBO 타자 공개 CSV Version 5를 확보했습니다. 원본은 9,703행·34개 컬럼이며, 계획서의 표본 조건으로 다음 시즌까지 평가 가능한 기록은 597건·142명입니다. 본 분석과 모형 성능 검증은 이후 진행합니다.

원본 CSV는 로컬에 보관하고 Git 추적에서 제외합니다. 데이터 배포자는 netsong이며, [Kaggle 데이터셋](https://www.kaggle.com/datasets/netsong/kbo-player-stats-19822025)에 표시된 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ko) 조건을 따릅니다. KBO 공식 데이터 배포물 또는 공식 승인 프로젝트로 표시하지 않습니다.

GitHub 업로드 후 LMS에 제출할 [계획서 파일 URL](https://github.com/HauserNR/llm-data-analysis-study/blob/main/data-analysis-project/01_proposal/01_proposal.md)입니다. 로컬 파일 작성만으로 원격 저장소에 반영되는 것은 아닙니다.
