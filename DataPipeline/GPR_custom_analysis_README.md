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

### Custom GPR 지수 (F1~F5)

| 변수 | 수식 | 설명 |
|---|---|---|
| `F1_raw` | $-\overline{\text{tone}}$ | GDELT GKG tone의 일평균을 역방향으로 변환한 단순 감성 지표 |
| `F2_raw` | $-\dfrac{\sum(\text{tone}_i \times \text{polarity}_i)}{\sum \text{polarity}_i}$ | polarity를 감성 밀도 가중치로 사용한 톤 가중평균 |
| `F3_raw` | $-\overline{\text{tone}} \times \log\!\left(1 + \dfrac{N}{\overline{N}}\right)$ | 평균 tone에 상대 보도량 충격을 결합한 복합 지표 |
| `F4_raw` | $\dfrac{\overline{\text{neg}}}{\overline{\text{pos}} + \overline{\text{neg}}}$ | 부정 비중이 차지하는 비율 |
| `F5_raw` | $\text{EWMA}_{28}(F2,\ r=0.1)$ | F2의 단기 변동을 완화한 28일 지수가중 이동평균 |
| `GPR_zscore` | — | 공식 Caldara & Iacoviello GPR Z-score |


### 최종 생성 변수 (Z-score 표준화)

| 변수 | 설명 |
|---|---|
| `F1_z` | F1_raw Z-score 표준화 |
| `F2_z` | F2_raw Z-score 표준화 |
| `F3_z` | F3_raw Z-score 표준화 |
| `F4_z` | F4_raw Z-score 표준화 |
| `F5_z` | F5_raw Z-score 표준화 |

> **하이퍼파라미터**
> - 이상값 제거 기준: `|tone_score| > 20`
> - 최소 일별 기사 수: `MIN_DAILY_COUNT = 5`
> - EWMA 윈도우: `WND = 28`일, 감쇠율: `r = 0.1`

---

## 5. 분석 방법론 (Methodology)

### Step 1. 데이터 로드 및 이벤트 분리

이벤트를 아래 4개 그룹으로 나눠 순차 처리한 후 전체 통합한다.

| 그룹 | 이벤트 | 중간 저장 파일 |
|---|---|---|
| (1) | hormuz_crisis, soleimani_assassination | `gpr_hormuz_soleimani.csv` |
| (2) | russia_ukraine_war | `gpr_russia_ukraine.csv` |
| (3) | israel_hamas_war, israel_iran, us_israel_iran | `gpr_israel_hamas_iran.csv` |
| (4) | 전체 통합 | `custom_gpr_daily.csv` |

- GCS(Google Cloud Storage) 기반 원시 CSV 로드 (`gcsfs`)

### Step 2. 데이터 전처리

1. URL 기준 중복 제거
2. tone 관련 결측치 제거
3. `|tone_score| > 20` 이상값 제거
4. GEO_THEMES 기반 지정학 기사 필터링
5. `_date` datetime 파생 변수 생성
6. 하루 기사 수 5건 미만 날짜 제거

### Step 3. Custom GPR 지수 생성

다음 5가지 대체 GPR 공식을 구축하였다.

| 공식 | 수식 | 설계 의도 |
|---|---|---|
| F1 | $-\overline{\text{tone}}$ | 뉴스 부정도의 단순 측정 |
| F2 | $-\sum(\text{tone} \times \text{polarity}) / \sum\text{polarity}$ | 감정 강도로 가중한 tone |
| F3 | $-\overline{\text{tone}} \times \log(1 + N/\overline{N})$ | 보도 집중도 반영 복합 지수 (공식 GPR 구조 모방) |
| F4 | $\overline{\text{neg}} / (\overline{\text{pos}} + \overline{\text{neg}})$ | 순수 부정 비율 측정 |
| F5 | $\text{EWMA}_{28}(F2,\ r=0.1)$ | F2의 단기 노이즈 평활화 |

**Z-score 표준화**

각 공식별로 이벤트 내 전체 기간 기준 Z-score 변환 적용

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

### 중간 저장 파일 (그룹별)

| 파일명 | 포함 이벤트 | 
|---|---|
| `gpr_hormuz_soleimani.csv` | hormuz_crisis, soleimani_assassination | 
| `gpr_russia_ukraine.csv` | russia_ukraine_war | 
| `gpr_israel_hamas_iran.csv` | israel_hamas_war, israel_iran | 
| `gpr_us_israel_iran.csv` | us_israel_iran | 

### 최종 산출 파일

| 파일명 | 설명 | 
|---|---|
| `custom_gpr_daily.csv` | 위 4개 그룹 통합 전체 이벤트 Custom GPR | 
| `gpr_custom_{event}.csv` | 이벤트별 개별 Custom GPR (6개 파일) | 
| `gpr_combined.csv` | 전체 이벤트 통합 GPR 결과 | 
| `gpr_correlation_summary.csv` | 공식 GPR 상관관계 요약 | 
| `01_*.png` ~ `07_*.png` | 분석 시각화 결과 |

### 주요 시각화 결과  

관련 시각화 결과는 `FIGURES/` 디렉토리에 저장하였다.

- Raw Article Distribution
- Preprocessed Tone Distribution
- Correlation Heatmap
- Scatter Matrix
- GPR Time Series
- Official vs Custom GPR Comparison
- Event Window Analysis

---

## 8. 참고문헌 (References)

1. Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. American Economic Review, 112(4), 1194–1225.
2. Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global Data on Events, Location and Tone, 1979–2012. ISA Annual Convention, April 2013.
3. Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139–1168.
4. Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring Economic Policy Uncertainty. Quarterly Journal of Economics, 131(4), 1593–1636.
5. Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35–65.
6. GDELT Project Documentation. GDELT Global Knowledge Graph (GKG) Codebook and Documentation. https://www.gdeltproject.org/
7. Yahoo Finance API via yfinance. Python package documentation. https://pypi.org/project/yfinance/
