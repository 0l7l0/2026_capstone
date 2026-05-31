# BTC 안전자산 가설 검증 (2026 캡스톤디자인)

> **핵심 질문**: 지정학적 위기 시 비트코인은 디지털 금(안전자산)인가?

---

## 1. 프로젝트 소개

본 연구는 Baur & Lucey (2010)의 Safe-Haven 판정 기준을 6개 지정학적 이벤트에 적용하여 **BTC가 안전자산으로 기능하는지** 통계적으로 검증합니다.

| 항목 | 내용 |
|------|------|
| 분석 기간 | 2019-01-02 ~ 2026-04-30 (1,827 거래일) |
| 분석 이벤트 | 6개 지정학 위기 (이벤트 창 ±17 거래일) |
| 분석 자산 | BTC, Gold, SP500, NASDAQ, TLT, DXY |
| 판정 기준 | Baur & Lucey (2010) 3조건 통합 판정 (부호 기준 엄격 적용) |

**분석 대상 이벤트**

| # | 이벤트 | 기준일 |
|---|--------|--------|
| 1 | 호르무즈 위기 | 2019-06-13 |
| 2 | 솔레이마니 암살 | 2020-01-03 |
| 3 | 러시아-우크라이나 전쟁 | 2022-02-24 |
| 4 | 이스라엘-하마스 전쟁 | 2023-10-07 |
| 5 | 이스라엘-이란 충돌 | 2024-04-14 |
| 6 | 미-이스라엘-이란 전쟁 | 2026-02-28 |

---

## 2. 시스템 구조도

```
GDELT GKG (BigQuery)          야후 파이낸스 / FRED / CNN
        │                               │
        ▼                               ▼
  GPR_custom 생성                 금융 시계열 수집
  (F3 = tone × log(N))          BTC · Gold · SP500 · VIX 등
        │                               │
        └──────────┬────────────────────┘
                   ▼
            master_data.csv
            (1,827 거래일 × 19 컬럼)
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
  Event Study  Quantile    GARCH-X
  (CAR/CSAR)   Regression  (변동성)
       │           │           │
       └───────────┴───────────┘
                   ▼
          최종 통합 판정 (3조건)
                   ▼
           Streamlit 대시보드
```

---

## 3. 분석 방법론

### 3조건 통합 판정 (Baur & Lucey 2010 부호 기준)

| 조건 | 방법 | Safe-Haven 판정 기준 |
|------|------|----------------------|
| C1 이벤트 스터디 | MacKinlay (1997) CAR, BH-FDR, Placebo | **CAR ≥ 0 부호 기준** (음수 미달) |
| C2 분위수 회귀 | Koenker & Bassett (1978), HAC SE | **β ≤ 0 부호 기준** at τ ≤ 0.10 (양수 미달) |
| C3 GARCH | GARCH-X Student-t MLE, EGARCH 강건성 | GPR γ ≤ 0 또는 비유의 (변동성 비연동) |

> ⚠ **2026-05-29 정정**: 이전 채점 로직이 "음수 CAR도 비유의면 C1 통과"로 처리하던 분기 제거. Baur & Lucey (2010) 원래 정의 (부호 기준)에 일관 적용. 이스라엘-하마스(CAR=-0.029)·이스라엘-이란 충돌(CAR=-0.063)이 음수 CAR로 C1 미달 → Weak Haven에서 Diversifier로 강등.

### 폴더별 분석 내용

| 폴더 | 분석 | 주요 방법론 |
|------|------|-------------|
| `DataPipeline/` | GPR 커스텀 지수 생성, master_data 구축 | BigQuery GDELT GKG, F3 공식 |
| `EDA/` | 기술통계, 상관관계, ARCH 검정 | ADF, Ljung-Box, ARCH-LM |
| `EventStudy/` | 이벤트별 CAR 분석 | CMRM / Market Model, Block Bootstrap (5,000회), BH-FDR, Wild Bootstrap (호르무즈 보강) |
| `Quantile/` | 위기 분위수별 β 추정 | HAC Newey-West SE, LOO 강건성, 블록 부트스트랩 |
| `GARCH/` | BTC 조건부 변동성 분석 | GARCH-X / EGARCH Student-t MLE, scipy 직접 구현, **Ljung-Box 잔차 진단 (사용자 검증 추가)** |
| `Dashboard/` | 결과 통합 시각화 | Streamlit + Plotly |
| `validation/` | 독립 검증 | catalog v1.6, **33개 학술 표준 항목 PASS 33/0/0 + 학술 권고 7건** |

> 독립 검증 (`validation/`): catalog v1.6 기준 자동 검증 PASS 33 / WARN 0 / FAIL 0 (red_flag 위반 0건). 매트릭스 ⚠ 표기는 학술 해석 권고(사람 판단)로 §7에 7건 별도 정리.

---

## 4. 최종 결론

### 이벤트별 판정 (2026-05-29 정정본)

| 이벤트 | C1 이벤트 스터디 | C2 분위수 회귀 | C3 GARCH | 점수 | 판정 |
|--------|:---:|:---:|:---:|:---:|------|
| 호르무즈 위기 | ✅ (CAR=+0.081) | ✅ (β=-0.012) | ✅ | 3/3 | **Safe Haven\*** |
| 솔레이마니 암살 | ✅ (CAR=+0.142) | ❌ | ✅ | 2/3 | Weak Haven |
| 러-우 전쟁 | ✅ (CAR=+0.113) | ❌ | ✅ | 2/3 | Weak Haven |
| **이스라엘-하마스** | ❌ **(CAR=-0.029 음수)** | ❌ | ✅ | **1/3** | **Diversifier** |
| **이스라엘-이란 충돌** | ❌ **(CAR=-0.063 음수)** | ❌ | ✅ | **1/3** | **Diversifier** |
| 미-이스라엘-이란 | ✅ (CAR=+0.132) | ❌ | ✅ | 2/3 | Weak Haven |

> \* 호르무즈 Safe Haven\* = 부호 기준 3/3 통과이나 BH 보정 후 비유의 + Placebo 미구분으로 **통계 강도 약함**. Wild Bootstrap(±3·±17) 보강 결과는 `validation/event_study_car_wild_bh.csv` 참조.

### 분포 (Baur & Lucey 2010 부호 기준 엄격 적용)

- **Safe Haven (강도 강함)**: 0건
- **Safe Haven\* (강도 약함)**: 1건 (호르무즈)
- **Weak Haven**: 3건 (솔레이마니, 러-우, 미-이스라엘-이란)
- **Diversifier**: 2건 (이스라엘-하마스, 이스라엘-이란 — 음수 CAR로 C1 미달)
- **Risky Asset**: 0건

### 핵심 발견

- **BTC는 안전자산이 아니다** — Strong Safe Haven 0건, 약한 Safe Haven\* 1건, Diversifier 2건
- **위기 시 동조화 강화** — SP500-BTC 동조화가 극단 하락(τ=0.01)에서 평상시(τ=0.50) 대비 2.2배 증가
- **GPR 상승이 동조화를 강화** — 상호작용항 δ=+0.005 (p=0.037), Safe Haven 조건과 정반대
- **GPR은 변동성에 유의하지 않음** — GARCH·EGARCH 전 모델에서 GPR γ 비유의 (p=0.58~0.96)
- **시장 심리(Fear&Greed)가 BTC 변동성 설명** — fear_greed_lag1 γ=+0.157 (p=0.038), EGARCH에서도 반복 유의 (단 C3 채점은 지정학 변수 한정 운영 정의)
- **호르무즈 Safe Haven\* 판정의 통계 강도 약함** — Wild Bootstrap·Placebo·BH 검정 결과 분산, 분위수 회귀 C2 의존도 높음
- **이스라엘-하마스·이스라엘-이란은 BTC도 시장과 함께 하락** — 음수 CAR (-0.029, -0.063)로 C1 미달, Diversifier 분류
- **Ljung-Box 잔차 진단** — 표준화 잔차 자기상관 없음(3/3 lag), 잔차² lag 5에서 ARCH 잔존(EGARCH가 보완)

---

## 5. 대시보드 이미지

<!-- 대시보드 스크린샷 추가 예정 -->

---

## 6. 팀원 역할

<!-- 팀원 이름 및 담당 파트 추가 예정 -->

---

## 7. 재현 방법 (How to Run)

### 환경 설정

```bash
pip install pandas numpy scipy statsmodels quantreg arch numdifftools \
            streamlit plotly jupyter
```

### 실행 순서

```
1. DataPipeline/master_data_generated.ipynb   ← master_data.csv 생성
2. DataPipeline/GPR_custom_analysis.ipynb     ← GPR_custom 지수 생성
3. EDA/EDA_final.ipynb                        ← 기술통계·ARCH 검정
4. EventStudy/event_study.ipynb               ← CAR·Placebo·BH 분석
5. Quantile/quantile_regression.ipynb         ← 분위수 회귀
6. GARCH/GARCH.ipynb                          ← GARCH-X·EGARCH 분석
7. streamlit run Dashboard/dashboard_ui.py    ← 대시보드 실행
```

### 데이터 위치

| 파일 | 경로 |
|------|------|
| 통합 분석 데이터 | `DataPipeline/processed_data/master_data.csv` |
| 자산 수익률 | `DataPipeline/processed_data/returns.csv` |
| 최종 판정 | `Dashboard/result_csv_png/final_judgment.csv` |
| 독립 검증 보고서 | `validation/VALIDATION_REPORT.md` |
| Ljung-Box 잔차 진단 | `validation/garch_ljung_box.csv` |

---

## 8. 참고문헌

**안전자산 판정 기준**
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229.

**이벤트 스터디**
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361–376. *(Wild Bootstrap, 호르무즈 보강)*

**분위수 회귀**
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.
- Newey, W. K., & West, K. D. (1987). A Simple, Positive Semidefinite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix. *Econometrica*, 55, 703–708.

**GARCH 모형**
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.
- Nelson, D. B. (1991). Conditional Heteroskedasticity in Asset Returns. *Econometrica*, 59(2), 347–370.
- Han, H., & Kristensen, D. (2014). Asymptotic Theory for GARCH-X Models. *Journal of Business & Economic Statistics*, 32(3), 416–429.

**지정학 리스크 지수**
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.

**BTC 변동성 및 심리 변수**
- Bourghelle, D., Jawadi, F., & Rozin, P. (2022). Do Collective Emotions Drive Bitcoin Volatility? *Finance Research Letters*, 45, 102041.
- Liu, Y., Tsyvinski, A., & Wu, X. (2017). GARCH Model With Fat-Tailed Distributions and Bitcoin Exchange Rate Returns. *Journal of Accounting, Business and Management*, 25(1).
