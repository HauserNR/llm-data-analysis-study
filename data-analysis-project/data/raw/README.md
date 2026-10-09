# KBO 타자 데이터 확보 기록

- 데이터명: **KBO Player Stats 1982–2025**
- 배포자: **netsong**
- 출처: [Kaggle 상세 페이지](https://www.kaggle.com/datasets/netsong/kbo-player-stats-19822025)
- 메타데이터: [Kaggle 공식 API](https://www.kaggle.com/api/v1/datasets/view/netsong/kbo-player-stats-19822025)
- 고정 버전 다운로드: [Version 5 ZIP](https://www.kaggle.com/api/v1/datasets/download/netsong/kbo-player-stats-19822025?datasetVersionNumber=5)
- 배포자가 표시한 라이선스: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ko)
- 원자료 출처: 배포 설명에 따르면 KBO 공식 공개 기록. 본 프로젝트는 KBO 웹사이트를 직접 크롤링하지 않았습니다.
- 확보일: **2026-10-09**
- 데이터 버전: **5** / 배포 페이지 최종 갱신일: **2026-08-03**
- 사용할 파일: `kbo_batting_stats_season_1982-2025.csv`
- 원본 규모: **9,703행·34개 컬럼·1,867명**, 1982~2025년, **2,524,350바이트**
- SHA-256: `0c6278049dc62132bad73ecf7f4b925c81e999715c6d847ccd508389b563e3ad`
- 변경 사항: ZIP에서 타자 CSV를 바이트 변경 없이 추출했습니다. 아직 파생 데이터나 분석 결과를 만들지 않았습니다.

CSV를 이 폴더에 보관하되 원본은 Git 추적에서 제외합니다. 저장소에는 확보 방법과 행 수 등 구조 점검 요약을 제공합니다. 이 파일은 배포자가 작성한 비공식 데이터이며, 표시 라이선스를 KBO의 승인으로 해석하지 않습니다. 비상업적 과제에 사용하고 출처·라이선스·가공 내용을 명시하며, 공유하는 데이터 가공물에는 동일한 라이선스 조건을 적용합니다.

배포 설명에서 SF·SH는 복원 추정치임을 확인했습니다. SF를 실제 공식 관측값이라고 표현하지 않습니다. 포지션·투타 일부도 추정 정보이므로 주 분석에 사용하지 않습니다. 기본 통계의 결측·중복이 없더라도 전체 기록의 정확성이 보증되는 것은 아닙니다.

## 다시 확보하고 점검하기

1. 위 데이터 페이지 또는 버전 고정 ZIP 링크에서 다운로드합니다. 서비스 상태에 따라 Kaggle 로그인이 필요할 수 있습니다.
2. ZIP에서 `kbo_batting_stats_season_1982-2025.csv`를 이 폴더로 추출합니다.
3. 프로젝트 폴더에서 다음 명령을 실행합니다. Python 표준 라이브러리만 사용하며 웹 요청은 하지 않습니다.

```bash
python3 scripts/inspect_data.py
```

이 코드는 헤더·연도·행 수·필수 결측·ID–시즌 중복과 계획서의 표본 조건에 해당하는 규모를 출력합니다. 본 분석이나 예측은 실행하지 않습니다. 저장된 결과는 [data_audit.json](../data_audit.json)에서 확인할 수 있습니다.

pandas로 읽는 예시는 다음과 같습니다.

```python
import pandas as pd

df = pd.read_csv("data/raw/kbo_batting_stats_season_1982-2025.csv",
                 encoding="utf-8-sig", dtype={"Id": "string"})
```

분석 테이블을 만들 때에는 생년월일·신체정보·학력 등 불필요한 원본 컬럼을 제거합니다. 다음 시즌 기록은 결과 비교에만 쓰며 현재 시즌의 입력에 포함하지 않습니다.
