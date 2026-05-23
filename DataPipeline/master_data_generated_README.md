
# master_data_generated

## 1. 파일 개요 (Overview)

`master_data_generated.ipynb`는 Custom GPR 데이터와 금융시장 수익률 데이터를 병합하여 최종 분석용 master dataset을 생성하는 노트북이다.

BTC, Gold, SP500, NASDAQ, TLT, DXY 등의 금융시장 데이터를 수집하고, Custom GPR·VIX·Fear & Greed Index와 결합하여 Event Study, Quantile Regression, GARCH 분석에 사용되는 통합 데이터셋을 구축하였다.

---

## 2. 분석 목적 (Objective)

본 분석의 목적은 지정학 리스크(Custom GPR)와 금융시장 수익률 데이터를 통합하여 BTC의 안전자산(safe-haven asset) 여부를 실증 분석하기 위한 최종 분석 데이터셋을 생성하는 데 있다.

특히 이벤트 기간별 금융시장 반응과 BTC 수익률 변화를 비교할 수 있도록 이벤트 기반 master dataset을 구축하였다.

---

## 3. 사용 데이터 (Dataset)

### 금융시장 데이터

| 자산 | Yahoo Finance Ticker |
|---|---|
| Bitcoin | `BTC-USD` |
| Gold | `GC=F` |
| TLT | `TLT` |
| DXY | `DX-Y.NYB` |
| S&P500 | `^GSPC` |
| NASDAQ | `^IXIC` |

### 추가 데이터

- Custom GPR (`custom_gpr_daily.csv`)
- VIX Index
- CNN Fear & Greed Index

### 데이터 출처

- Yahoo Finance (`yfinance`)
- Custom GPR Pipeline
- CNN Fear & Greed
- CBOE VIX

---

## 4. 주요 변수 설명 (Features)

| 변수 | 설명 |
|---|---|
| `BTC` | Bitcoin 일별 로그수익률 |
| `Gold` | Gold 일별 로그수익률 |
| `TLT` | 미국 장기채 ETF 수익률 |
| `DXY` | 달러 인덱스 수익률 |
| `SP500` | S&P500 수익률 |
| `NASDAQ` | NASDAQ 수익률 |
| `GPR_custom` | F3 기반 Custom GPR |
| `VIX` | 변동성 지수 |
| `fear_greed` | Fear & Greed Index |
| `event_name` | 지정학 이벤트 이름 |
| `event_date` | 이벤트 기준일 |

---

## 5. 분석 방법론 (Methodology)

### Step 1. 금융시장 데이터 수집

- `yfinance` 기반 가격 데이터 수집
- 로그수익률(log return) 계산
- 미국 거래일 기준 데이터 정렬

### Step 2. BTC 거래일 보정

BTC는 24시간 거래되는 반면 전통 금융시장은 휴장일이 존재하므로, 비거래일 BTC 수익률을 다음 거래일에 누적 반영하였다.

### Step 3. Custom GPR 병합

- 이벤트별 Custom GPR 데이터 병합
- 이벤트 기준일(event_date) 연결
- Z-score 기반 GPR 변수 생성

### Step 4. VIX 및 Fear & Greed 병합

- VIX 데이터 병합
- Fear & Greed Index 병합
- 날짜 기준 정렬 및 결측치 처리

### Step 5. 최종 Master Dataset 생성

최종적으로 다음 변수를 포함한 통합 master dataset을 생성하였다.

- 금융시장 수익률
- 지정학 리스크(Custom GPR)
- 시장 불안 심리 지표(VIX, Fear & Greed)
- 이벤트 메타데이터

---

## 6. 주요 결과 (Key Findings)

- 지정학 이벤트 기간 동안 BTC는 Gold와 상이한 수익률 반응을 보이는 경우가 확인되었다.
- F3 기반 Custom GPR이 금융시장 변동성과 가장 높은 연관성을 보였다.
- VIX 상승 구간에서 BTC 변동성이 확대되는 경향이 관찰되었다.
- 생성된 master dataset은 이후 Event Study, Quantile Regression, GARCH 분석의 핵심 입력 데이터로 활용되었다.

---

## 7. 결과 파일 (Output)

| 파일명 | 설명 |
|---|---|
| `market_returns.csv` | 금융시장 일별 로그수익률 데이터 |
| `merged_market_data.csv` | 시장 데이터 + Custom GPR 병합 데이터 |
| `final_master_data.csv` | 최종 통합 master dataset |
| `returns.csv` | 이벤트 분석용 수익률 데이터 |

### 주요 활용 분석

- Event Study
- Quantile Regression
- GARCH Volatility Analysis
- Dashboard Visualization
