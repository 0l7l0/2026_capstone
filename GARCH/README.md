# GARCH — 변동성 분석

## 1. 파일 개요 (Overview)

`GARCH.ipynb`는 지정학적 리스크(GPR)와 시장 심리 변수가 BTC 조건부 변동성에 미치는 영향을 분석하는 통합 최종본입니다.  
두 노트북(`GARCH-X 주 분석`, `EGARCH 비교 분석`)을 13개 Step으로 통합하였으며, GARCH-X 기주 분석 + 이벤트 더미·EGARCH 강건성 검증으로 구성됩니다.

---

## 2. 분석 목적 (Objective)

- **핵심 질문**: 지정학적 리스크(GPR) 상승 시 BTC 변동성은 증가하는가? 안전자산인가, 위험자산인가?
- 자체 제작 GPR(`GPR_custom`)과 공식 GPR(`GPR_zscore`)의 BTC 변동성 설명력 비교
- 시장 심리 변수(VIX, Fear&Greed)와의 상대적 설명력 검증
- `arch` 라이브러리의 외생변수 처리 한계를 극복하기 위해 `scipy`로 직접 MLE 구현

---

## 3. 사용 데이터 (Dataset)

**입력 파일**: `../datapipeline/master_data/master_data.csv`

| 컬럼 | 설명 |
|------|------|
| `BTC` | BTC 일별 로그 수익률 |
| `GPR_custom` | 자체 제작 지정학 리스크 지수 (F3_z) |
| `GPR_zscore` | Caldara & Iacoviello (2022) 공식 GPR Z-score |
| `VIX` | 시장 공포 지수 (변동성 지수) |
| `fear_greed_lag1` | 전일 CNN 탐욕·공포 지수 |
| `event_name` | 이벤트 구간 레이블 |

- **분석 표본**: 1,821 거래일 (이벤트 구간 병합)
- **종속변수**: `returns_pct = BTC × 100` (GARCH 수렴 안정화를 위한 단위 변환)
- **외생변수**: Z-score 표준화 후 1일 시차(lag 1) 적용 — 내생성 문제 방지

---

## 4. 주요 변수 설명 (Features)

**GARCH-X 파라미터**

| 파라미터 | 기호 | 설명 |
|---------|------|------|
| 기저 변동성 | ω (omega) | 기저 분산 상수, ≥ 0.05 강제 (과적합 방지) |
| ARCH 효과 | α (alpha) | 전일 충격이 오늘 변동성에 미치는 영향 |
| GARCH 효과 | β (beta) | 전일 변동성의 오늘 지속성 |
| 외생변수 효과 | γ (gamma) | 외생변수 1σ 증가 → 변동성 변화 **핵심 분석 대상** |
| t분포 자유도 | ν (nu) | 팻테일 두께 (> 2 강제, 낮을수록 극단값 빈번) |
| α + β | — | 충격 지속성, 1에 가까울수록 충격이 오래 지속 (< 1 유지) |

---

## 5. 모델 구성 (Model Specification)

**GARCH-X 수식**

```
수익률 방정식:  r(t) = μ + ε(t),   ε(t) ~ Student-t(0, h(t), ν)
분산 방정식:   h(t) = ω + α·ε²(t-1) + β·h(t-1) + γ·X(t-1)
```

**EGARCH-X 수식** (강건성 검증용)

```
ln h(t) = ω + β·ln h(t-1) + α·(|z(t-1)| − E|z|) + γ_asym·z(t-1) + δ·X(t-1)
```

**5개 모델 구성**

| 모델 | 외생변수 | 목적 |
|------|---------|------|
| Model1 | GPR_zscore | 공식 GPR 단독 벤치마크 |
| Model2 | GPR_custom | 자체 GPR 단독 설명력 |
| Model3 | VIX + fear_greed_lag1 | 시장 심리 설명력 |
| Model4 | GPR_zscore + VIX + fear_greed_lag1 | 공식 GPR + 시장 심리 통합 |
| Model5 | GPR_custom + VIX + fear_greed_lag1 | 자체 GPR + 시장 심리 통합 |

**γ 해석 기준**

| 조건 | 해석 |
|------|------|
| γ > 0, p < 0.05 | GPR↑ → BTC 변동성↑ (위험자산 특성) |
| γ < 0, p < 0.05 | GPR↑ → BTC 변동성↓ (안전자산 특성) |
| p ≥ 0.05 | 해당 변수가 BTC 변동성을 통계적으로 설명하지 못함 |

---

## 6. 분석 방법론 (Methodology)

| Step | 내용 | 세부 방법 |
|------|------|-----------|
| 0 | 라이브러리·환경 설정 | scipy MLE 직접 구현 (`arch` 라이브러리 외생변수 한계 우회) |
| 1 | master_data.csv 로드 | 컬럼 확인, event_name 정합성 검증 |
| 2 | 분석 데이터 준비 | BTC×100 단위 변환, Z-score 표준화, X(t-1) 시차 생성, 시간순 정렬 |
| 3 | GARCH-X MLE 함수 정의 | Student-t 로그우도, bounds 설정, clip/strict 분산 처리 방식 |
| 4 | Model1~5 추정 (clip) | 10개 초기값 격자 탐색(L-BFGS-B), 최저 음의 로그우도 채택 |
| 5 | SE·p-value 계산 | numdifftools Richardson 외삽법 Hessian + delta method |
| 6 | γ 계수 요약 | 외생변수별 방향·유의성 정리 |
| 7 | 모델 비교 (AIC/BIC) | AIC·BIC 기준 최적 모델 선택 |
| 8 | 분산 처리 강건성 | clip vs strict 방식 최적 모델 일치 여부 확인 |
| 9 | 이벤트 더미 강건성 | 이벤트별 구조 차이 통제 (hormuz_crisis 기준, 4개 더미 추가) |
| 10-1~6 | EGARCH 강건성 | 비대칭 변동성 구조에서 GARCH 결론 유지 여부 확인 |
| 11 | 시각화 | 조건부 변동성 시계열·γ 계수 막대그래프·AIC/BIC 비교 |
| 12 | 결과 저장 | CSV 10종 + PNG 5종 |
| 13 | 최종 결론 | GARCH·이벤트 더미·EGARCH 통합 해석 |

---

## 7. 이론적 근거 (Theoretical Background)

각 방법론적 선택이 어떤 논문을 근거로 하는지 정리합니다.

### GARCH-X 모형 선택 근거

| 선택 | 논문 | 근거 요약 |
|------|------|-----------|
| ARCH 채택 | Engle (1982) | 기존 일정분산 가정을 기각 — 과거 정보가 미래 변동성 예측에 유용하다는 조건부 이분산성 실증 |
| GARCH(1,1) 확장 | Bollerslev (1986) | h(t-1) 항 추가로 ARCH보다 간결·유연한 변동성 구조 제공, α+β<1 약정상성 조건 제시 |
| 외생변수 포함 (GARCH-X) | Han & Kristensen (2014) | 외생변수가 분산식에서 유의함을 점근적 이론으로 수립, 추가 설명력 정당화 |

### 외생변수 선택 근거

| 변수 | 논문 | 근거 요약 |
|------|------|-----------|
| GPR | Caldara & Iacoviello (2022) | 지정학적 리스크 공식 지수 원전 — 대리변수로서 이론적 정당성 확보 |
| Fear & Greed | Bourghelle et al. (2022) | F&G와 BTC 변동성 간 유의한 양방향 lead-lag 관계, 극단 공포 → 패닉 매도 → 과도한 변동성 유발 확인 |
| VIX | Su et al. (2022) | VIX는 시장 불확실성 척도로 알려짐, VIX↑ → 투자자 위험심리 반영 |

### Student-t 오차항 사용 근거

| 선택 | 논문 | 근거 요약 |
|------|------|-----------|
| Student-t MLE | Liu et al. (2017) | BTC 수익률 fat-tail 분포 확인, Student-t GARCH가 정규 GARCH 대비 AIC·BIC 기준 우수 |

### α+β ≈ 1 해석 (near-IGARCH)

| 선택 | 논문 | 근거 요약 |
|------|------|-----------|
| α+β < 1 정상성 조건 | Bollerslev (1986) | α+β → 1 시 정상성 경계, 충격이 장기 지속되는 구조 |
| near-IGARCH 설명 | Bergsli et al. (2022) | α+β ≈ 1 → 무조건분산 미존재, 고지속성(long-memory) 변동성 구조 |

### MLE 추정 구현 근거

| 선택 | 논문 | 근거 요약 |
|------|------|-----------|
| Hessian 기반 SE | Calzolari et al. (1993) | GARCH 추정 후 공분산행렬 산출 시 Hessian 역행렬 사용의 표준 근거 |
| 제약 파라미터 변환 | Doornik & Ooms (2003) | 제약 공간 → unconstrained 공간 변환(지수/로짓), Jacobian 연결 |
| Delta method | Anastasiou & Ley (2017) | 변환된 추정량의 점근정규성 수립, Jacobian으로 원 파라미터 SE 복원 |
| 다중 초기값 | Mahmood & Khan (2020) | GARCH 우도함수의 다봉성 — 국소최적해 회피를 위한 다중 초기값 격자 탐색 필요 |

### 강건성 검증 근거

| 방법 | 논문 | 근거 요약 |
|------|------|-----------|
| 이벤트 더미 | Spyrou & Kassimatis (1999) | 분산식에 0/1 더미 포함 → 특정 기간 구조적 변화 통제, 결론 안정성 확인 |
| EGARCH | Nelson (1991) | 충격 부호별 비대칭 반응(레버리지 효과) 포착 — GARCH 결론의 강건성 교차 검증 |

### AIC/BIC 기반 모형 선택 근거

AIC·BIC는 로그우도를 높이려는 경향을 복잡도 벌점으로 보정하는 모형선택 기준입니다. 파라미터 수가 많아도 적합도 개선이 충분히 클 때만 복잡한 모형을 지지하며, 두 기준이 일치하는 모형을 최적으로 채택합니다.

---

## 8. 주요 결과 (Key Findings)

**GARCH-X 모델 비교** (AIC 오름차순)

| 모델 | 설명 | AIC | BIC | α+β |
|------|------|-----|-----|-----|
| **Model3** | VIX + Fear&Greed | **9578.71** | 9617.26 | 0.9961 |
| Model4 | 공식 GPR + 시장심리 | 9580.39 | 9624.45 | 0.9975 |
| Model5 | 커스텀 GPR + 시장심리 | 9580.42 | 9624.47 | 0.9960 |
| Model2 | 커스텀 GPR 단독 | 9582.40 | 9615.45 | 0.9937 |
| Model1 | 공식 GPR 단독 | 9582.52 | 9615.56 | 0.9937 |

**γ 계수 유의성 요약**

| 모델 | 변수 | γ | p-value | 해석 |
|------|------|---|---------|------|
| Model1 | GPR_zscore | -0.0045 | 0.960 | 비유의 |
| Model2 | GPR_custom | +0.0263 | 0.735 | 비유의 |
| Model3 | VIX | -0.0231 | 0.801 | 비유의 |
| Model3 | **fear_greed_lag1** | **+0.1573** | **0.038** | **✅ 유의 (p<0.05)** |
| Model4 | GPR_zscore | +0.0440 | 0.583 | 비유의 |
| Model4 | **fear_greed_lag1** | **+0.1667** | **0.032** | **✅ 유의 (p<0.05)** |
| Model5 | GPR_custom | +0.0364 | 0.596 | 비유의 |
| Model5 | **fear_greed_lag1** | **+0.1615** | **0.034** | **✅ 유의 (p<0.05)** |

**EGARCH 강건성 확인 — fear_greed_lag1 (p-value)**

| 모델 | p-value | 유의성 |
|------|---------|--------|
| EGARCH E3 (VIX + F&G) | 0.019 | ✅ |
| EGARCH E4 (GPR_custom + VIX + F&G) | 0.017 | ✅ |
| EGARCH E6 (GPR_custom_high + VIX + F&G) | 0.014 | ✅ |

> **핵심 결론**
> - **Model3 (VIX + Fear&Greed)** 이 AIC 기준 최적 모델
> - `GPR_custom`은 GARCH·EGARCH 전 모델에서 **통계적 유의성 미확보**
> - `fear_greed_lag1`은 GARCH·EGARCH 모두에서 **반복적으로 유의** → BTC 변동성 설명에 더 안정적인 변수
> - 이벤트 더미 추가 시 AIC 개선, BIC 악화 → 주모형 대체가 아닌 강건성 검증으로 해석
> - α+β ≈ 0.996 → near-IGARCH 구조 (충격의 지속성이 매우 강함)

---

## 9. 결과 파일 (Output)

| 파일 | 유형 | 내용 |
|------|------|------|
| `result_csv_png/garch_model_comparison.csv` | CSV | 모델별 AIC·BIC·LogLik·α+β 비교 |
| `result_csv_png/garch_gamma_results.csv` | CSV | 외생변수 γ 계수 + p-value 요약 |
| `result_csv_png/garch_model_params.csv` | CSV | 전체 파라미터 상세 (ω·α·β·γ·ν) |
| `result_csv_png/garch_event_dummy_comparison.csv` | CSV | 이벤트 더미 강건성 검증 결과 |
| `result_csv_png/garch_conditional_volatility.csv` | CSV | 최적 모델 조건부 변동성 시계열 |
| `result_csv_png/egarch_model_comparison.csv` | CSV | EGARCH 모델 비교 |
| `result_csv_png/egarch_exog_coefficients.csv` | CSV | EGARCH 외생변수 계수 + p-value |
| `result_csv_png/egarch_step_b3_coefficients_long.csv` | CSV | Step 10-3 계수 (long format) |
| `result_csv_png/egarch_step_b3_coefficients_wide.csv` | CSV | Step 10-3 계수 (wide format) |
| `result_csv_png/garch_egarch_integrated_summary.csv` | CSV | GARCH·이벤트 더미·EGARCH 통합 요약 |
| `result_csv_png/garch_conditional_vol.png` | PNG | 조건부 변동성 σ(t) 시계열 |
| `result_csv_png/garch_gamma_coefficients.png` | PNG | γ 계수 방향·크기 비교 막대그래프 |
| `result_csv_png/garch_model_comparison.png` | PNG | 모델별 AIC·BIC 비교 |
| `result_csv_png/egarch_model_aic_bic.png` | PNG | EGARCH 강건성 AIC·BIC 비교 |
| `result_csv_png/egarch_cond_vol_comparison.png` | PNG | GARCH·EGARCH 조건부 변동성 비교 |
| `result_csv_png/egarch_gpr_coef_compare.png` | PNG | GPR 계수 GARCH·EGARCH 비교 |

---

## 10. 참고문헌 (References)

**모형 근거**
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation. *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.
- Nelson, D. B. (1991). Conditional Heteroskedasticity in Asset Returns: A New Approach. *Econometrica*, 59(2), 347–370.
- Han, H., & Kristensen, D. (2014). Asymptotic Theory for the Quasi-Maximum Likelihood Estimator for GARCH Models with Covariates. *Journal of Business & Economic Statistics*, 32(3), 416–429.

**외생변수 선택**
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
- Bourghelle, D., Jawadi, F., & Rozin, P. (2022). Do collective emotions drive bitcoin volatility? *Finance Research Letters*, 45, 102041.
- Su, C.-W., Qin, M., Tao, R., & Umar, M. (2022). Can Bitcoin Be a Safe Haven in Fear Sentiment? *Technological Forecasting and Social Change*, 174, 121186.

**분포 및 파라미터 추정**
- Liu, Y., Tsyvinski, A., & Wu, X. (2017). GARCH Model With Fat-Tailed Distributions and Bitcoin Exchange Rate Returns. *Journal of Accounting, Business and Management*, 25(1).
- Calzolari, G., Fiorentini, G., & Panattoni, L. (1993). Alternative Estimators of the Covariance Matrix in GARCH Models. *Econometrics Working Paper*.
- Doornik, J. A., & Ooms, M. (2003). Multimodality in the GARCH Regression Model. *Working Paper*.
- Anastasiou, D., & Ley, C. (2017). Bounds for the Asymptotic Normality of the Maximum Likelihood Estimator Using the Delta Method. *ESAIM: Probability and Statistics*, 21, 332–350.
- Mahmood, I., & Khan, M. I. (2020). Multi-modality in the Likelihood Function of GARCH Model. *Working Paper*.

**강건성 검증**
- Bergsli, L. Ø., Lind, A. F., Molnár, P., & Polasik, M. (2022). Forecasting Volatility of Bitcoin. *Research in International Business and Finance*, 59, 101540.
- Spyrou, S. I., & Kassimatis, K. (1999). Did Equity Market Volatility Increase Following the Opening of Stock Markets to Foreign Investors? *Journal of Economic Development*, 24(1).

**수치 계산**
- Numdifftools Python library — Richardson extrapolation for numerical Hessian
