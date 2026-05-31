# Dashboard — 결과 통합 시각화

## 1. 파일 개요 (Overview)

`dashboard_ui.py`는 본 연구의 모든 분석 결과(EDA·이벤트 스터디·분위수 회귀·GARCH·통합 판정)를 Streamlit과 Plotly로 통합 시각화하는 인터랙티브 대시보드입니다.

각 분석 노트북(`EDA_final.ipynb`, `event_study.ipynb`, `quantile_regression.ipynb`, `GARCH.ipynb`)의 산출 CSV와 PNG를 입력으로 받아, 멀티 탭 구조로 학술 청중과 일반 청중 모두에게 결과를 제시합니다. 검증자(`validation/` 폴더)의 보정·강건성 결과(BH-FDR, Placebo, Wild Bootstrap, Baur-Lucey 통합 판정)도 함께 시각화에 반영됩니다.

---

## 2. 분석 목적 (Objective)

- **분산된 분석 결과의 일관된 시각화**: 4개 분석 폴더의 CSV·PNG를 단일 인터페이스로 통합
- **두 청중 대상 분리 제공**: 학술 청중에게는 통계 수치·유의성·매트릭스, 일반 청중에게는 직관적인 카드·차트·내러티브
- **금융시장 반응의 직관적 전달**: 통계 검증 결과를 BTC vs Gold 비교·롤링 상관관계 등 시각적 비유로 전환
- **검증 결과 반영**: `validation/` 폴더의 catalog v1.6 점검 결과 + Baur-Lucey 3조건 통합 판정을 카드·표·히트맵으로 직접 노출

---

## 3. 사용 데이터 (Dataset)

대시보드는 본분석 4개 폴더 + 검증자 폴더의 산출물을 입력으로 받습니다.

| 탭 / 섹션 | 입력 파일 | 출처 폴더 |
|---|---|---|
| EDA 요약 | `prices.csv`, `returns.csv`, `plot1~8_*.png` | `EDA/result_csv_png/` |
| 이벤트 스터디 | `event_study_results.csv`, `event_study_car_bh.csv`, `event_study_placebo.csv`, CAR 시계열·막대 PNG | `EventStudy/result_csv_png/` + `validationv2/` |
| Wild Bootstrap (호르무즈) | `event_study_car_wild_bh.csv` | `validationv2/` |
| 분위수 회귀 | `quantreg_main.csv`, `quantreg_ia.csv`, heatmap·beta path PNG | `Quantile/result_csv_png/` |
| GARCH | `garch_model_comparison.csv`, `garch_gamma_results.csv`, `garch_conditional_volatility.csv`, AIC·variance PNG | `GARCH/result_csv_png/` |
| GARCH 잔차 진단 | `garch_ljung_box.csv` | `validationv2/` |
| 통합 판정 (Baur-Lucey) | `final_judgment.csv` | `validationv2/` |
| 학술 검증 보고서 | `validationv2/README.md`, `catalog.json` | `validationv2/` |

---

## 4. 주요 변수 설명 (Features)

### 통합 판정 카드 (`final_judgment.csv`)

| 컬럼 | 카드 표시 |
|---|---|
| `event_label` | 이벤트 한글명 |
| `verdict` | 5단계 분류 (Safe Haven / Safe Haven\* / Weak Haven / Diversifier / Risky Asset) |
| `score` | 3조건 통과 점수 (0~3) |
| `C1_event_study_pass`, `C2_quantile_reg_pass`, `C3_garch_pass` | True/False 체크 |
| `C1_detail`, `C2_detail`, `C3_detail` | 채점 사유 (CAR=+0.081, β=-0.012 등) |
| `C1_statistical_strength` | strong / weak / inconclusive |

### 강건성 카드 (`event_study_car_bh.csv`, `placebo.csv`, `wild_bh.csv`)

| 컬럼 | 카드 표시 |
|---|---|
| `p_norm_bh` | BH-FDR 보정 후 p값 |
| `placebo_p` | Placebo 200회 시뮬 p값 |
| `wild_p` | Wild Bootstrap p값 (호르무즈 한정) |

---

## 5. 분석 방법론 (Methodology)

### 대시보드 구조

| 탭 | 내용 | 청중 |
|---|---|---|
| 👤 일반인 | 큰 결론 카드 + 6 이벤트 verdict 히트맵 + BTC vs Gold 비교 차트 | 비전공자 |
| 📊 EDA | 자산 가격 추이·수익률 분포·상관관계 히트맵 | 학술 |
| 🎯 이벤트 스터디 | CAR 막대그래프·시계열·BH 보정 표·Placebo 결과 | 학술 |
| 📉 분위수 회귀 | β 경로·γ 경로·이벤트×분위수 히트맵 | 학술 |
| 📈 GARCH | 조건부 변동성·γ 계수·EGARCH 비교·잔차 진단 | 학술 |
| ⚖ 통합 판정 | 3조건 매트릭스·verdict 카드·정정 사유 | 학술 |
| 🔬 검증 보고서 | `validation/README.md` 8섹션 + catalog v1.6 | 학술 |

### 시각화 라이브러리

- `streamlit` — 멀티 탭 UI, 위젯, 캐싱
- `plotly` — 인터랙티브 차트 (히트맵, 산점도, 시계열)
- `pandas` — CSV 입출력
- `pillow` — PNG 렌더링

### 구현 원칙

- 모든 본분석 CSV는 원본 그대로 읽음 (값 변환 없음)
- 검증자 보정 결과(`validation/`)는 별도 컬럼으로 병합
- 색상 코드: 양수 CAR/통과 = 녹색, 음수/미달 = 적색, 비유의 = 회색

---

## 6. 주요 결과 (Key Findings)

### 일반인 탭 핵심 메시지

> **비트코인은 강한 안전자산이 아닙니다.** 6개 지정학 이벤트 중 강한 안전자산 판정은 0건, 약한 안전자산\* 1건, 부분 안전자산(Weak Haven) 3건, 단순 분산자산(Diversifier) 2건입니다.

### 통합 판정 분포 카드 (`validation/final_judgment.csv` 기준)

| 분류 | 건수 | 이벤트 |
|---|---:|---|
| Strong Safe Haven | 0 | — |
| Safe Haven\* (강도 약함) | 1 | 호르무즈 위기 |
| Weak Haven | 3 | 솔레이마니·러-우·미-이스라엘-이란 |
| Diversifier | 2 | 이스라엘-하마스·이스라엘-이란 충돌 |
| Risky Asset | 0 | — |

### 학술 탭 핵심 발견

- **위기 시 동조화 강화** — SP500-BTC 분위수 회귀 β가 극단 하락(τ=0.01)에서 평상시(τ=0.50) 대비 2.2배 증가
- **GPR 상승이 동조화를 강화** — 상호작용항 δ=+0.005, p=0.037 (Safe Haven 조건과 정반대)
- **GPR은 변동성에 유의하지 않음** — GARCH·EGARCH 전 모델에서 GPR γ 비유의 (p=0.58~0.96)
- **시장 심리(Fear&Greed)가 BTC 변동성 설명** — fear_greed_lag1 γ=+0.157, p=0.038
- **Ljung-Box 잔차 진단** — 표준화 잔차 자기상관 없음 (3/3 lag 통과)

### 별표(\*) 표기 의미

호르무즈만 Safe Haven\* 표기. 부호 기준(CAR ≥ 0, β ≤ 0) 3조건 모두 통과이나 BH 보정 후 비유의 + Placebo 미구분으로 **통계 강도 약함**. 판정은 분위수 회귀 C2 결과에 주로 의존.

---

## 7. 결과 파일 (Output)

| 파일 | 설명 |
|---|---|
| `dashboard_ui.py` | Streamlit 메인 진입점 (멀티 탭 UI) |
| `Dashboard/result_csv_png/` | 본진 분석 결과 CSV·PNG 집약 (대시보드 입력원) |
| `Dashboard/result_csv_png/final_judgment.csv` | 통합 판정 카드용 (validationv2/와 동기화) |
| `Dashboard/result_csv_png/safe_haven_summary.csv` | 최종 결과 요약 카드용 (추천) |
| `Dashboard/result_csv_png/model_comparison_summary.csv` | GARCH 모델 비교표 (추천) |

### 추천 추가 시각화 (본진 README 원문 우선순위)

| 우선순위 | 파일 | 내용 |
|---|---|---|
| 🔴 반드시 | `FIGURES/main_btc_gold_compare.png` | BTC vs Gold 누적 수익률 (Main Hero) |
| 🔴 반드시 | `EventStudy/result_csv_png/car_comparison.png` | 이벤트별 BTC·Gold·SP500 CAR 막대 |
| 🔴 반드시 | `EDA/result_csv_png/rolling_corr.png` | BTC-SP500·BTC-Gold 롤링 상관관계 |
| 🟡 권장 | `Quantile/result_csv_png/quantreg_heatmap.png` | 분위수별 β 히트맵 |
| 🟡 권장 | `GARCH/result_csv_png/garch_gamma_coefficients.png` | γ 계수 비교 막대 |

---

## 8. 참고문헌 (References)

**안전자산 판정 기준**
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229.

**시각화 도구**
- Streamlit — streamlit.io
- Plotly — plotly.com/python/
- Inkpen, K., et al. (2023). Advancing Human-AI Complementarity. *arXiv:2306.01859* — 시각화-내러티브 통합 원칙

**본 대시보드가 시각화하는 분석 인용**
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39.
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS B*, 57(1), 289–300.
- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361–376.
