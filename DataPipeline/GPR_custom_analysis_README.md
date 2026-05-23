# GPR_custom_analysis

## 1. 파일 개요 (Overview)

`GPR_custom_analysis.ipynb`는 GDELT GKG 기반 지정학 이벤트 뉴스 데이터를 활용하여 Custom GPR(Geopolitical Risk) 지수를 생성하고, 공식 GPR 지수와의 상관관계를 비교·검증하는 분석 파일이다.

뉴스 tone, polarity, 보도량 정보를 활용하여 F1~F5 형태의 대체 GPR 공식을 구축하고, 이벤트별 시계열 및 상관관계 분석을 수행하였다.

---

## 2. 분석 목적 (Objective)

본 분석의 목적은 지정학 이벤트 발생 시 뉴스 기반 Custom GPR 지수를 구축하고, 이를 통해 BTC의 안전자산(safe-haven asset) 여부를 검증하기 위한 지정학 리스크 변수를 생성하는 데 있다.

특히 기존 Caldara & Iacoviello GPR 구조를 참고하여 다양한 대체 GPR 공식을 설계하고, 공식 GPR과의 상관관계를 비교하여 가장 설명력이 높은 공식을 선정하였다.

---

## 3. 사용 데이터 (Dataset)

### 사용 이벤트

- Hormuz Crisis
- Soleimani Assassination
- Russia–Ukraine War
- Israel–Hamas War
- Israel–Iran Conflict
- US–Israel–Iran Conflict

### 데이터 출처

- GDELT GKG 2.1
- Google BigQuery
- Google Cloud Storage (GCS)

### 주요 데이터 컬럼

| 컬럼 | 설명 | 비고 |
|---|---|---|
| `event_timestamp` | 기사 수집 시각 (UTC) | GDELT 15분 단위 |
| `date` | YYYYMMDD 날짜 | 일별 집계 키 |
| `url` | 기사 URL | 중복 제거 기준 |
| `tone_score` | 전체 어조 | 음수=부정, 양수=긍정 |
| `positive_score` | 긍정 단어 비율 | V2Tone[1] |
| `negative_score` | 부정 단어 비율 | V2Tone[2] |
| `polarity` | 감정 강도 | V2Tone[3] |
| `themes` | GDELT 자동 분류 태그 | `;` 구분 |

---

## 4. 주요 변수 설명 (Features)

| 변수 | 설명 |
|---|---|
| `F1_raw` | 단순 평균 tone 기반 GPR |
| `F2_raw` | polarity 가중 tone 기반 GPR |
| `F3_raw` | 보도량 × tone 복합 GPR |
| `F4_raw` | 부정 비율 기반 GPR |
| `F5_raw` | F2 기반 28일 EWMA GPR |
| `GPR_zscore` | 공식 GPR Z-score |

### 최종 생성 변수

- `F1_z`
- `F2_z`
- `F3_z`
- `F4_z`
- `F5_z`

(Z-score 표준화 적용)

---

## 5. 분석 방법론 (Methodology)

### Step 1. 데이터 로드 및 이벤트 분리

- 이벤트별 원시 CSV 로드
- 날짜 형식 통일
- 이벤트 단위 데이터 구성

### Step 2. 데이터 전처리

1. URL 기준 중복 제거
2. tone 관련 결측치 제거
3. `|tone_score| > 20` 이상값 제거
4. GEO_THEMES 기반 지정학 기사 필터링
5. `_date` datetime 파생 변수 생성
6. 하루 기사 수 5건 미만 날짜 제거

### Step 3. Custom GPR 지수 생성

다음 5가지 대체 GPR 공식을 구축하였다.

| 공식 | 설명 |
|---|---|
| F1 | 단순 일평균 tone 역전 |
| F2 | polarity 가중 tone |
| F3 | 보도량 × tone 복합 |
| F4 | 부정 비율 기반 |
| F5 | 28일 EWMA 기반 |

### Step 4. 공식 GPR 상관관계 분석

- Pearson Correlation
- Spearman Correlation
- 이벤트별 최고 상관 공식 비교
- Correlation Heatmap 및 Scatter Matrix 시각화

### Step 5. 최적 GPR 공식 선정

공식 GPR과의 상관관계 비교 결과, 대부분 이벤트에서 F3(보도량 × tone 복합 지수)가 가장 높은 Pearson 상관계수를 보였다.

이에 따라 이후 BTC 안전자산 검증 분석에서는 F3 기반 Custom GPR을 핵심 지정학 리스크 변수로 활용하였다.

---

## 6. 주요 결과 (Key Findings)

- F3(보도량 × tone 복합 지수)가 대부분 이벤트에서 공식 GPR과 가장 높은 상관관계를 기록하였다.
- 단순 tone 평균보다 보도량을 함께 반영한 지수가 공식 GPR 구조를 더 잘 설명하는 것으로 나타났다.
- 지정학 이벤트 발생 시 기사량 급증과 tone 악화가 동시에 나타나는 경향을 확인하였다.
- F3 기반 Custom GPR은 이후 Event Study 및 회귀 분석의 핵심 지정학 리스크 변수로 활용되었다.

---

## 7. 결과 파일 (Output)

| 파일명 | 설명 |
|---|---|
| `custom_gpr_daily.csv` | 전체 이벤트 통합 Custom GPR 데이터 |
| `gpr_combined.csv` | 이벤트별 통합 GPR 결과 |
| `gpr_correlation_summary.csv` | 공식 GPR 상관관계 요약 |
| `01_*.png` ~ `07_*.png` | 분석 시각화 결과 |

### 주요 시각화 결과

- Raw Article Distribution
- Preprocessed Tone Distribution
- Correlation Heatmap
- Scatter Matrix
- GPR Time Series
- Official vs Custom GPR Comparison
- Event Window Analysis

---

## 8. 참고문헌 (References)

1. Caldara, D., & Iacoviello, M. (2022). *Measuring Geopolitical Risk*. American Economic Review.
2. BBVA Research (2025). *Geopolitical Risk Monitoring Framework*.
3. BNP Paribas Asset Management (2022). *Geopolitical Risk and Market Dynamics*.
4. GDELT Project Documentation — https://www.gdeltproject.org/
5. Yahoo Finance API (`yfinance`)
