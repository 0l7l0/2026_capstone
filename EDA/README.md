# EDA — 탐색적 데이터 분석

## 1. 파일 개요 (Overview)

`EDA_final.ipynb`는 지정학적 위기 시 비트코인(BTC)의 안전자산 특성을 검증하기 위한 통합 탐색적 데이터 분석 노트북입니다.  
총 8단계(Step 0–8)로 구성되며, 6개 자산의 가격 추이·수익률 분포·통계 검정·상관관계 변화를 분석하고 이후 분석(이벤트 스터디, 분위 회귀, GARCH)을 위한 기초 근거를 마련합니다.

---

## 2. 분석 목적 (Objective)

- **핵심 질문**: 지정학적 위기 시 비트코인은 "디지털 금(안전자산)"인가?
- 비트코인과 전통 안전자산(금·미국 국채)·위험자산(S&P500·NASDAQ)의 가격 패턴 및 상관관계 구조 비교
- JB·ADF·ARCH 검정을 통해 이후 GARCH 모델 적용 근거 확보

---

## 3. 사용 데이터 (Dataset)

**자산 데이터** — 출처: Yahoo Finance (`yfinance`)

| 자산 | 티커 | 유형 |
|------|------|------|
| Bitcoin | BTC-USD | 암호화폐 |
| Gold Futures | GC=F | 안전자산 |
| 미국 국채 ETF | TLT | 안전자산 |
| 달러 인덱스 | DX-Y.NYB | 통화 |
| S&P 500 | ^GSPC | 주식 |
| NASDAQ | ^IXIC | 주식 |

- **수집 기간**: 2019-07-01 ~ 2026-03-24 (총 1,691 거래일)
- **결측치 처리**: NASDAQ 거래일 기준 정렬 후 금 선물 결측치 전일값(ffill) 적용

**분석 대상 이벤트 (5개)**

| 이벤트 | 분석 기간 | 이벤트 기준일 |
|--------|-----------|--------------|
| US-Iran Conflict (솔레이마니 암살) | 2019-07-01 ~ 2020-07-01 | 2020-01-03 |
| COVID-19 Pandemic | 2019-09-01 ~ 2020-09-01 | 2020-03-11 |
| Russia-Ukraine War | 2021-08-01 ~ 2022-08-01 | 2022-02-24 |
| Israel-Hamas War | 2023-04-01 ~ 2024-04-01 | 2023-10-07 |
| Iran War (2026) | 2025-06-01 ~ 2026-03-24 | 2026-02-28 |

---

## 4. 주요 변수 설명 (Features)

| 변수 | 설명 |
|------|------|
| `df` | 6개 자산 일별 종가 |
| `returns` | 로그 수익률 (`ln(Pₜ / Pₜ₋₁)`) |
| `normalized` | 분석 시작일 = 100 기준 정규화 가격 |
| `WAR_START` | 이란 전쟁 전·후 구분 기준일 (`2026-02-28`) |
| `EVENT_PERIODS` | 이벤트명 → `{start, end, event_date}` 딕셔너리 |
| `EVENTS` | 이란 전쟁 세부 마커 3개 (시위 시작·항모 배치·공습 시작) |

---

## 5. 분석 방법론 (Methodology)

| Step | 내용 | 세부 방법 |
|------|------|-----------|
| 0 | 환경 설정 | 전역 상수(TICKERS·EVENTS·EVENT_PERIODS) 정의 |
| 1 | 데이터 수집·정제 | yfinance 다운로드, ffill, 로그수익률·정규화 산출 |
| 2 | 기술통계 | 연환산 수익률·변동성·왜도·첨도·샤프지수 |
| 3-1 | 전체 가격 추이 | 정규화 가격 + 이벤트 마커 + 전쟁 기간 음영 |
| 3-2 | 이벤트별 정규화 비교 | 5개 이벤트 루프, 이벤트 전후 음영 처리 |
| 3-3 | 이동평균선 | MA20·MA60 (6개 자산 서브플롯) |
| 4-1 | 수익률 분포·변동성 군집 | 히스토그램 + 정규분포 오버레이, 수익률² 시계열 |
| 4-2 | BTC High-Low 변동폭 | 이벤트별 일별 고가-저가 차이 시계열 |
| 5 | 통계 검정 | Jarque-Bera(정규성)·ADF(정상성)·ARCH 효과 검정 |
| 6-1 | 상관관계 히트맵 | 전체·전쟁 전·전쟁 중 3구간 피어슨 상관관계 비교 |
| 6-2 | 이벤트별 ±60일 히트맵 | 이벤트 기준 전후 60 거래일 상관관계 비교 |
| 6-3 | 전후 평균 수익률 비교 | 이벤트 기준 Before/After/Difference 테이블 |
| 7 | 롤링 상관관계 | 30일 윈도우, BTC vs SP500·Gold·TLT |
| 8 | EDA 요약 | 변동성 비교 바차트·상관관계 변화 종합 해석 |

---

## 6. 주요 결과 (Key Findings)

**기술통계 요약**

| 자산 | 변동성(연,%) | 첨도 | 샤프지수 |
|------|-------------|------|---------|
| BTC | 62.6 | 14.6 | 0.389 |
| Gold | 6.9 | 1.8 | -0.532 |
| TLT | 18.1 | 10.5 | 0.730 |
| DXY | 16.7 | 4.2 | -0.619 |
| SP500 | 20.2 | 15.3 | 0.390 |
| NASDAQ | 24.5 | 8.2 | 0.445 |

**통계 검정 결과** — 6개 자산 모두 p < 0.05

| 검정 | 귀무가설 | 결과 | 함의 |
|------|---------|------|------|
| Jarque-Bera | 정규분포를 따른다 | 전원 기각 | 비선형 모델 필요 |
| ADF | 단위근이 있다 | 전원 기각 | 정상 시계열 → 시계열 분석 가능 |
| ARCH | ARCH 효과 없다 | 전원 기각 | 변동성 군집 존재 → GARCH 사용 정당화 |

**이란 전쟁(2026) 전후 BTC 상관관계 변화**

| 비교 쌍 | 전쟁 전 | 전쟁 중 | 변화 | 해석 |
|---------|--------|--------|------|------|
| BTC–SP500 | 0.365 | 0.572 | +0.206 | ❌ 위험자산 신호 |
| BTC–NASDAQ | 0.388 | 0.552 | +0.164 | ❌ 위험자산 신호 |
| BTC–Gold | -0.130 | -0.129 | +0.001 | → 변화 미미 |
| BTC–TLT | 0.106 | 0.297 | +0.191 | ✅ 안전자산 신호 |
| BTC–DXY | -0.024 | -0.065 | -0.041 | → 변화 미미 |

**이벤트별 BTC 평균 수익률 변화**

| 이벤트 | 이전(%) | 이후(%) | 방향 |
|--------|--------|--------|------|
| US-Iran Conflict | -0.325 | +0.223 | ↑ 상승 |
| COVID-19 Pandemic | -0.148 | +0.340 | ↑ 상승 |
| Russia-Ukraine War | -0.087 | -0.431 | ↓ 하락 |
| Israel-Hamas War | -0.015 | +0.762 | ↑ 상승 |
| Iran War | -0.244 | +0.460 | ↑ 상승 |

> **EDA 종합**: BTC는 SP500·NASDAQ과 상관관계가 강화(위험자산 행태)되는 반면, TLT와의 상관관계도 동시에 증가하는 혼재된 신호를 보임. 러-우 전쟁을 제외한 4개 이벤트에서 BTC 이벤트 후 수익률이 상승했으나, 금과의 상관관계 변화는 미미하여 고전적 안전자산 정의에는 부합하지 않음.

---

## 7. 결과 파일 (Output)

| 파일 | 유형 | 내용 |
|------|------|------|
| `result_csv_png/prices.csv` | CSV | 6개 자산 일별 종가 |
| `result_csv_png/returns.csv` | CSV | 로그 수익률 |
| `result_csv_png/normalized.csv` | CSV | 시작일=100 정규화 가격 |
| `result_csv_png/plot1_price_trend.png` | PNG | 전체 기간 자산별 가격 추이 |
| `result_csv_png/plot2_event_price.png` | PNG | 이벤트별 정규화 가격 비교 (5개) |
| `result_csv_png/plot3_moving_average.png` | PNG | 자산별 MA20·MA60 이동평균선 |
| `result_csv_png/plot4_returns_dist.png` | PNG | 수익률 분포 + 변동성 군집 |
| `result_csv_png/plot5_btc_highlow.png` | PNG | BTC 이벤트별 일별 변동폭 (High-Low) |
| `result_csv_png/plot6_corr_heatmap.png` | PNG | 전쟁 전·중·전체 상관관계 히트맵 |
| `result_csv_png/plot7_event_heatmap.png` | PNG | 이벤트별 ±60일 상관관계 히트맵 |
| `result_csv_png/plot8_rolling_corr.png` | PNG | BTC 30일 롤링 상관관계 |

---

## 8. 참고문헌 (References)

- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
- Sharpe, W. F. (1966). Mutual Fund Performance. *The Journal of Business*, 39(1), 119–138.
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation. *Econometrica*, 50(4), 987–1007.
- Yahoo Finance API — `yfinance` Python library
