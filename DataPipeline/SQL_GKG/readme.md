# Overview - Event Selection Criteria

본 프로젝트에서는 공식 GPR(Geopolitical Risk) 지수의 평균 대비 급등 구간을 기준으로 주요 지정학 이벤트를 선정하였다.

선정된 이벤트는 다음과 같다.

- Hormuz Crisis
- Soleimani Assassination
- Russia-Ukraine War
- Israel-Hamas War
- Israel-Iran Conflict
- US-Israel-Iran Conflict

각 이벤트는 GDELT GKG 데이터셋에서 SQL 기반 키워드 필터링을 통해 추출하였다.  

---
## Objective

- GKG 데이터셋 내 지정학 관련 키워드 검색 수행
- GDELT theme taxonomy 기반 군사·분쟁 관련 테마 필터링 적용
- Persons, Organizations, Locations, Themes 필드를 활용한 이벤트별 조건 구성
- 공통 지정학 테마(Common Geopolitical Themes)를 OR 조건으로 묶어 군사·전쟁·안보 관련 뉴스 우선 추출
- 이벤트별 인물·조직·지역 키워드를 OR 조건으로 구성하여 특정 지정학 이벤트 관련 기사 식별
- 이벤트 특수 테마(예: MARITIME, SANCTIONS, DRONES 등)를 OR 조건으로 추가 적용
- 각 조건 그룹(Common Themes / Event Keywords / Additional Themes)은 AND 조건으로 연결하여 이벤트 관련성 강화
- 중복 뉴스 제거 수행
- 이벤트 기간 기준 뉴스 데이터 추출
- 일별 뉴스 빈도 집계 수행
- 
---
## Dataset

| 데이터셋 | 설명 |
|---|---|
| GDELT GKG | 글로벌 뉴스 및 이벤트 데이터 |
| Event Period | 2019 ~ 2026 주요 지정학 이벤트 |
| Source Type | 뉴스 기사 및 이벤트 메타데이터 |

---
## Data Collection Scope

본 프로젝트는 GDELT GKG(Global Knowledge Graph) 데이터셋을 기반으로
2019-01-01 ~ 2026-04-30 기간의 글로벌 뉴스 데이터를 수집하였다.

각 지정학 이벤트는 이벤트 발생일(event date)을 기준으로
이전 이벤트와 이후 이벤트 구간이 겹치지 않도록 분할하여 수집하였다.

### Event Windows

| Event | Event Date | Collection Period |
|---|---|---|
| Hormuz Crisis | 2019-06-13 | 2019-01-01 ~ 2019-09-23 |
| Soleimani Assassination | 2020-01-03 | 2019-09-24 ~ 2021-01-28 |
| Russia-Ukraine War | 2022-02-24 | 2021-01-29 ~ 2022-12-15 |
| Israel-Hamas War | 2023-10-07 | 2022-12-16 ~ 2024-01-03 |
| Israel-Iran Conflict | 2024-04-01 | 2024-01-04 ~ 2025-03-16 |
| US-Israel-Iran Conflict | 2026-02-28 | 2025-03-17 ~ 2026-04-30 |

---
## Keywords

각 이벤트별 지정학 관련 인물(Persons), 조직(Organizations),
지역(Locations), 테마(Themes) 키워드를 기반으로 SQL 필터링을 수행하였다.

### Common Geopolitical Themes

| Common Themes |
|---|
| TAX_FNCACT_MILITARY |
| WB_635_PEACE_AND_SECURITY |
| CRISISLEX_T03_ARMED-CONFLICT |
| SANCTIONS |
| ARMEDCONFLICT |
| WB_2432_FRAGILITY_CONFLICT_AND_VIOLENCE |
| EPU_CATS_NATIONAL_SECURITY |
| KILL |
| DRONES |

###  Event-specific Keywords

| Event | Persons / Organizations / Locations | Additional Themes |
|---|---|---|
| Hormuz Crisis | irgc, gevolutionary guard, iran, hormuz, persian gulf | MARITIME, ENV_OIL, SEIZE, tanker |
| Soleimani Assassination | soleimani, irgc, quds, baghdad, iraq | assassination |
| Russia-Ukraine War | putin, zelensky, ukraine, kyiv, conbas, russia | - |
| Israel-Hamas War | hamas, netanyahu, israel, gaza, palestine | - |
| Israel-Iran Conflict | netanyahu, khamenei, iran, israel, irgc | - |
| US-Israel-Iran Conflict | biden, netanyahu, khamenei, pentagon, irgc, iran, israel | MARITIME |

---
## SQL Logic / Filtering Rule

- GKG 데이터셋 내 지정학 관련 키워드 검색
- GDELT theme taxonomy 기반 군사·분쟁 테마 필터링
- 중복 뉴스 제거
- 이벤트 기간 기준 뉴스 데이터 추출
- 일별 뉴스 빈도 집계 수행

----

## Output

| 파일명 | 설명 |
|---|---|
| hormuz_raw.csv | 호르무즈 위기 뉴스 데이터 |
| soleimani_raw.csv | 솔레이마니 사건 뉴스 데이터 |
| ukraine_raw.csv | 러시아-우크라이나 전쟁 뉴스 데이터 |
| israel_hamas_raw.csv | 이스라엘-하마스 전쟁 뉴스 데이터 |
| israel_iran_raw.csv | 이스라엘-이란 충돌 뉴스 데이터 |
| us_israel_iran_raw.csv | 미국-이스라엘-이란 갈등 뉴스 데이터 |

---
## Related Analysis

본 SQL 기반 데이터 추출 결과는 다음 분석 과정에 활용된다.

- Custom_GPR/
- Quantile/
- EventStudy/
- GARCH/
- Dashboard/

---
## References

### GDELT / GKG References
- GDELT Global Knowledge Graph (GKG) Codebook
- GDELT Theme Taxonomy Documentation
- GDELT Project Documentation

### Geopolitical Risk References
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk.
- Geopolitical Risk (GPR) Index Methodology

### Custom Filtering Note
본 프로젝트에서는 GDELT GKG의 테마 체계(theme taxonomy)와
지정학 이벤트 관련 주요 인물·조직·지역 키워드를 기반으로
커스텀 SQL 필터링을 수행하였다.
