# DataPipeline — 데이터 파이프라인

## 1. 파일 개요 (Overview)

본 폴더는 GDELT 기반 지정학 이벤트 데이터와 야후 파이낸스·FRED·CNN의 금융시장 데이터를 통합해 본분석에 사용할 단일 마스터 데이터셋(`master_data.csv`, 1,827 거래일)을 생성하는 데이터 파이프라인 디렉토리입니다.

핵심 노트북은 두 개입니다. `GPR_custom_analysis.ipynb`는 GDELT GKG 원시 데이터로부터 자체 지정학 리스크 지수(GPR_custom)를 생성하고 공식 GPR(Caldara & Iacoviello 2022)과 비교 검증합니다. `master_data_generated.ipynb`는 GPR_custom 결과를 금융 시계열과 병합해 분석용 마스터 데이터를 만듭니다.

---

## 2. 분석 목적 (Objective)

- **GPR_custom 지수 생성**: GDELT GKG의 일별 뉴스 톤·기사 수 데이터로부터 5종 후보 공식(F1~F5)을 비교하고, 공식 GPR과 상관관계가 가장 높은 변형을 선택
- **금융 시계열 통합**: BTC·Gold·SP500·NASDAQ·TLT·DXY 가격, VIX, Fear & Greed 지수를 일별로 병합
- **본분석용 마스터 데이터 산출**: 결측치 처리, 이벤트 라벨링, 표준화 전처리 완료된 단일 CSV 생성

---

## 3. 사용 데이터 (Dataset)

### 원시 데이터 출처

| 데이터 | 출처 | 도구 |
|---|---|---|
| 지정학 뉴스 톤·기사 수 | GDELT GKG (Global Knowledge Graph) | BigQuery SQL |
| 자산 가격 (BTC·Gold·SP500·NASDAQ·TLT·DXY) | Yahoo Finance | `yfinance` |
| 변동성 지수 (VIX) | Yahoo Finance | `yfinance` |
| 시장 심리 (Fear & Greed) | CNN | 웹 스크랩 |
| 공식 GPR | Caldara & Iacoviello (2022) | FRED |

### 분석 기간 및 표본

- 기간: 2019-01-02 ~ 2026-04-30
- 마스터 데이터 표본: 1,827 거래일
- 자산 수익률 표본: 1,843 거래일 (`returns.csv`)

### 디렉토리 구조

```text
DataPipeline/
├── SQL_GKG/                              GDELT GKG 추출 SQL
├── raw_data/                             이벤트별 원시 뉴스 샘플
├── processed_data/                       GPR_custom + 마스터 데이터
├── GPR_custom_analysis.ipynb             GPR 생성 노트북
├── GPR_custom_analysis_README.md
├── master_data_generated.ipynb           마스터 데이터 통합 노트북
└── master_data_generated_README.md
```

---

## 4. 주요 변수 설명 (Features)

### GPR_custom 후보 공식 (F1 ~ F5)

| 변형 | 공식 | 의미 |
|---|---|---|
| F1 | 일별 평균 톤 | 평균 톤 (단순) |
| F2 | 일별 기사 수 | 보도 빈도 |
| F3 | tone × log(N) | **본분석 채택** — 톤과 빈도의 결합 |
| F4 | tone × √N | 톤·빈도 결합 (변형) |
| F5 | tone × N | 톤·빈도 곱 (스케일링 없음) |

→ F3가 공식 GPR(Caldara & Iacoviello 2022)과 최고 상관관계.

### 마스터 데이터 주요 컬럼

| 컬럼 | 설명 |
|---|---|
| `BTC`, `Gold`, `SP500`, `NASDAQ`, `TLT`, `DXY` | 자산별 로그수익률 |
| `VIX` | 시장 변동성 지수 |
| `fear_greed`, `fear_greed_lag1` | CNN Fear & Greed (당일·전일) |
| `GPR_custom` | 자체 지정학 리스크 지수 (F3 Z-score) |
| `GPR_zscore` | 공식 GPR Z-score (Caldara & Iacoviello 2022) |
| `event_name` | 이벤트 라벨 (6개 지정학 위기 + 평상시) |

---

## 5. 분석 방법론 (Methodology)

### Step별 작업 흐름

| Step | 노트북 | 내용 |
|---|---|---|
| 1 | `GPR_custom_analysis.ipynb` | GDELT GKG에서 일별 톤·기사 수 추출 (BigQuery SQL) |
| 2 | 동일 | F1~F5 공식 비교, 공식 GPR과 상관관계 분석, F3 채택 |
| 3 | 동일 | 이벤트 ±26일 윈도우 GPR 변화 검증 |
| 4 | `master_data_generated.ipynb` | yfinance로 자산 가격 다운로드, 로그수익률 계산 |
| 5 | 동일 | VIX·F&G 병합, 결측치 ffill 처리 |
| 6 | 동일 | GPR_custom + GPR_zscore Z-score 표준화 |
| 7 | 동일 | 6개 이벤트 라벨링 (event_name 컬럼) |
| 8 | 동일 | 단일 `master_data.csv` 출력 (1827 × 19) |

### F3 공식 채택 근거

- 공식 GPR과 최고 상관관계 (r ≈ 0.7+)
- 톤(부정적 보도 강도)과 빈도(보도 집중도)를 동시에 반영
- log(N) 스케일링으로 극단적 보도 폭증의 과대평가 회피
- 인용: Caldara & Iacoviello (2022) — 톤·빈도 결합이 GPR의 핵심 구성 원리

---

## 6. 주요 결과 (Key Findings)

### GPR_custom 생성 결과

- F3 (tone × log(N))이 공식 GPR과 최고 상관관계
- 6개 이벤트 모두에서 이벤트 직후 GPR_custom 급등 확인
- 이벤트 윈도우 ±26일 시각화로 GPR 반응 패턴 검증

### 마스터 데이터 통합 결과

- 1,827 거래일 × 19 컬럼 단일 데이터셋 완성
- 결측치 0% (ffill 처리 완료)
- 6개 지정학 이벤트 라벨링 완료 (`hormuz_crisis`, `soleimani_assassination`, `russia_ukraine_war`, `israel_hamas_war`, `israel_iran`, `us_israel_iran`)

> **본분석에 미친 영향**: 본 마스터 데이터는 EventStudy·Quantile·GARCH 3종 분석의 단일 입력원으로 사용됨. 1,827행 표본은 catalog v1.6 학술 표준의 충분 표본 조건을 충족 (단, 호르무즈 위기 추정창 86일은 표준 95일에 미달하여 Wild Bootstrap 보강 적용 — `validation/event_study_car_wild_bh.csv`).

---

## 7. 결과 파일 (Output)

| 파일 | 설명 |
|---|---|
| `processed_data/master_data.csv` | 통합 마스터 데이터 (1,827 거래일 × 19 컬럼) — 본분석 단일 입력원 |
| `processed_data/returns.csv` | 자산 로그수익률 (1,843 거래일) |
| `processed_data/GPR_custom_F3.csv` | F3 공식 기반 자체 GPR (Z-score) |
| `raw_data/` | 이벤트별 원시 GDELT 뉴스 데이터 샘플 |
| `SQL_GKG/` | BigQuery SQL 쿼리 모음 |
| `GPR_custom_analysis_README.md` | GPR 생성 노트북 상세 설명 |
| `master_data_generated_README.md` | 마스터 데이터 통합 노트북 상세 설명 |

---

## 8. 참고문헌 (References)

- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
- Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global data on events, location, and tone, 1979–2012. *ISA Annual Convention*, 2(4), 1–49.
- Yahoo Finance API — `yfinance` Python library
- CNN Fear & Greed Index — money.cnn.com/data/fear-and-greed/
- FRED (Federal Reserve Economic Data) — Caldara & Iacoviello 공식 GPR 시계열
