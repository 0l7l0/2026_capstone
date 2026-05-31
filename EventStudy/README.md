# Event Study — CAR 분석

## 1. 파일 개요 (Overview)

`event_study.ipynb`는 6개 지정학적 이벤트에 대해 비트코인(BTC)과 전통 자산의 누적 비정상 수익률(CAR)을 산출하고, Baur & Lucey (2010) 기준으로 안전자산 여부를 판별하는 이벤트 스터디 분석 노트북입니다.  
정상 수익률 모델(CMRM / Market Model), BMP 검정, 블록 부트스트랩, 다중검정 보정(BH), 플라시보 검정까지 단계적으로 수행합니다.

---

## 2. 분석 목적 (Objective)

- **핵심 질문**: 지정학적 위기 시 BTC의 CAR이 통계적으로 유의하게 양(+)인가? → 안전자산인가?
- 자산별 정상 수익률(Normal Return)을 추정하여 이벤트 기간의 비정상 수익률(AR) 분리
- t-test·BMP 검정·블록 부트스트랩으로 CAR 유의성 검증
- Baur & Lucey (2010) 기준으로 각 자산을 Safe Haven / Diversifier / Risky Asset으로 분류

---

## 3. 사용 데이터 (Dataset)

| 파일 | 용도 | 기간 |
|------|------|------|
| `master_data.csv` | 이벤트 창(±17일) 수익률·GPR·VIX·Fear&Greed | 이벤트 구간 |
| `returns.csv` | 추정 기간 수익률 슬라이싱 | 2019-07-01~ |

**분석 자산**: BTC, Gold, TLT, DXY, NASDAQ (SP500은 Market Model 벤치마크로 사용)

**분석 대상 이벤트 (6개)**

| 이벤트 | 기준일 | 이벤트 창 | 추정 기간 |
|--------|--------|-----------|-----------|
| Hormuz Crisis | 2019-06-13 | ±17 거래일 | [-120, -26] 거래일 |
| Soleimani Assassination | 2020-01-03 | ±17 거래일 | [-120, -26] 거래일 |
| Russia-Ukraine War | 2022-02-24 | ±17 거래일 | [-120, -26] 거래일 |
| Israel-Hamas War | 2023-10-07 | ±17 거래일 | [-120, -26] 거래일 |
| Israel-Iran | 2024-04-14 | ±17 거래일 | [-120, -26] 거래일 |
| US-Israel-Iran War | 2026-02-28 | ±17 거래일 | [-120, -26] 거래일 |

> 이벤트 창을 `±25`일에서 **`±17`일**로 수정 — 모든 이벤트에서 확보 가능한 최소 공통 거래일 기준

---

## 4. 주요 변수 설명 (Features)

| 변수 | 설명 |
|------|------|
| `AR(t)` | 비정상 수익률 = 실제 수익률 − 정상 수익률 |
| `SAR(t)` | 표준화 비정상 수익률 = AR(t) / σ_est (BMP 검정용) |
| `CAR` | 누적 비정상 수익률 = Σ AR(t), 이벤트 창 전체 합산 |
| `CSAR` | 누적 표준화 비정상 수익률 = Σ SAR(t) |
| `t_stat` | CAR 유의성 t통계량 |
| `p_norm` | 정규분포 기반 p-value |
| `p_boot` | 블록 부트스트랩(5,000회) p-value |
| `p_norm_bh` | Benjamini-Hochberg 다중검정 보정 p-value |
| `sig` | 유의 여부 (p_norm < 0.05) |

---

## 5. 분석 방법론 (Methodology)

**정상 수익률 모델**

| 자산 | 모델 | 설명 |
|------|------|------|
| BTC, Gold, DXY | CMRM | 추정 기간 평균 수익률 μ를 정상 수익률로 사용 |
| NASDAQ, TLT | Market Model | SP500을 독립변수로 한 OLS 회귀 |

> BTC에 Market Model (NASDAQ 기반) 적용 시 이벤트마다 β 극심 변동(0.03~1.06), R² 불안정(0.00~0.22) → CMRM 채택

**검정 방법**

| Step | 내용 |
|------|------|
| Step 0 | 라이브러리 설정 |
| Step 1 | 데이터 로드 (master_data.csv, returns.csv) |
| Step 2 | 추정 기간 슬라이싱 (returns.csv → [-120, -26]) |
| Step 3 | 정상 수익률 추정 (CMRM / Market Model OLS) |
| Step 4 | AR·SAR·CAR·CSAR 산출 (이벤트 창 ±17일 슬라이싱) |
| Step 5 | 유의성 검정: t-test + BMP + 블록 부트스트랩(5,000회) + BH 보정 |
| Step 6 | 시각화 (CAR 시계열·막대그래프) |
| Step 7 | Baur & Lucey (2010) 최종 분류 |
| Step 8 | 결과 저장 |

**Baur & Lucey (2010) 분류 기준**

| 조건 | 분류 |
|------|------|
| CAR > 0 & p < 0.05 | **Safe Haven** ✅ |
| CAR > 0 & p ≥ 0.05 | **Diversifier** |
| CAR < 0 & p < 0.05 | **Risky Asset** ❌ |
| CAR < 0 & p ≥ 0.05 | 비유의 |

---

## 6. 주요 결과 (Key Findings)

**CAR 및 유의성 요약** (유의 기준: p_norm < 0.05)

| 이벤트 | 자산 | CAR | t-stat | p_norm | p_boot | 판정 |
|--------|------|-----|--------|--------|--------|------|
| Hormuz Crisis | BTC | +0.081 | 0.835 | 0.436 | 0.236 | ⚪ 비유의 |
| Hormuz Crisis | Gold | +0.004 | 0.223 | 0.831 | 0.792 | ⚪ 비유의 |
| Soleimani | BTC | +0.142 | 1.516 | 0.180 | 0.227 | ⚪ 비유의 |
| Soleimani | Gold | +0.026 | 1.232 | 0.264 | 0.182 | ⚪ 비유의 |
| Russia-Ukraine | BTC | +0.113 | 1.042 | 0.337 | 0.239 | ⚪ 비유의 |
| Israel-Hamas | BTC | -0.029 | -0.871 | 0.417 | 0.534 | ⚪ 비유의 |
| **Israel-Iran** | **Gold** | **+0.043** | **2.611** | **0.040** | **0.035** | **🟢 Safe Haven** |
| Israel-Iran | BTC | -0.063 | -0.751 | 0.481 | 0.416 | ⚪ 비유의 |
| US-Israel-Iran | BTC | +0.132 | 1.898 | 0.107 | 0.010 | ⚪ 비유의 |

**BH 다중검정 보정 후**: 30개 검정 전체 비유의 (Gold Israel-Iran: p_bh = 0.849)

**플라시보 검정** (200회 무작위 창 시뮬레이션)

| 이벤트 | 실제 BTC CAR | 플라시보 평균 | 백분위 | p-value |
|----------|----------:|----------:|----------:|----------:|
| Hormuz Crisis | +0.365 | +0.014 | 86.0% | 0.28 |
| Soleimani Assassination | +0.404 | -0.022 | 95.0% | 0.10 |
| Russia–Ukraine War | +0.132 | +0.000 | 63.5% | 0.73 |
| Israel–Hamas War | +0.405 | -0.019 | 95.5% | 0.09 |
| Israel–Iran | -0.219 | -0.004 | 20.5% | 0.41 |
| US–Israel–Iran | +0.168 | -0.040 | 72.5% | 0.55 |


> **핵심 결론**
>
> * **BTC**: 6개 이벤트 중 4개에서 양(+) CAR를 기록하였으나, BH-FDR 보정 후 모든 이벤트가 비유의(pBH=0.849)로 나타남
> * **Gold**: Israel-Iran 이벤트에서 유일하게 Safe Haven 판정(p=0.040)을 받았으나, BH 보정 후 비유의(pBH=0.849)로 전환
> * **BH 다중검정 보정 후**: 30개 검정 전체 비유의 (Gold Israel-Iran: pBH = 0.849)
> * **플라시보 검정(200회 무작위 창 시뮬레이션)**에서도 모든 이벤트가 유의수준 5%를 충족하지 못함
> * 따라서 이벤트 스터디(C1)만으로 BTC를 Strong Safe Haven으로 분류할 통계적 근거는 확인되지 않음
> * 이후 분위수 회귀(C2)와 GARCH(C3)를 통해 극단 하락 구간 동조화 및 변동성 반응을 추가 검증

 ---

## 7. 결과 파일 (Output)

### CSV 파일

| 파일                                             | 내용                             |
| ---------------------------------------------- | ------------------------------ |
| `result_csv_png/event_study_results.csv`       | 이벤트별·자산별 CAR·t-stat·p-value·판정 |
| `result_csv_png/event_study_car_bh.csv`        | BH 다중검정 보정 적용 결과               |
| `result_csv_png/event_study_AR_timeseries.csv` | 일별 AR·SAR·CAR·CSAR 시계열         |
| `result_csv_png/event_study_placebo.csv`       | 플라시보 검정 결과 (200회)              |

### PNG 파일

| 파일                                              | 내용                      |
| ----------------------------------------------- | ----------------------- |
| `result_csv_png/event_study_CAR_timeseries.png` | 이벤트별·자산별 CAR 시계열        |
| `result_csv_png/event_study_CAR_bar_final.png`  | 이벤트별 CAR 막대그래프 (유의성 표시) |


---

## 8. 참고문헌 (References)

- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? An Analysis of Stocks, Bonds and Gold. *Financial Review*, 45(2), 217–229.
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39.
- Brown, S. J., & Warner, J. B. (1985). Using Daily Stock Returns: The Case of Event Studies. *Journal of Financial Economics*, 14(1), 3–31.
- Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-Study Methodology under Conditions of Event-Induced Variance. *Journal of Financial Economics*, 30(2), 253–272.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
