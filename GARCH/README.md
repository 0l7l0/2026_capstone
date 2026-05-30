# GARCH — 변동성 분석

## 1. 파일 개요 (Overview)

`GARCH.ipynb`는 지정학적 리스크(GPR)와 시장 심리 변수가 BTC 조건부 변동성에 미치는 영향을 분석하는 통합 최종본입니다.

본 분석은 다음 세 축으로 구성됩니다.

* GARCH-X 주 분석
* 이벤트 더미 기반 강건성 검증
* EGARCH 기반 비대칭 변동성 강건성 검증

`arch` 라이브러리의 외생변수 처리 한계를 보완하기 위해 `scipy.optimize.minimize` 기반 직접 MLE(Maximum Likelihood Estimation)를 구현하였습니다.

---

## 2. 분석 목적 (Objective)

핵심 질문:

> 지정학적 리스크(GPR)가 상승할 때 BTC 변동성은 증가하는가?
> BTC는 안전자산(Safe Haven)인가 위험자산(Risk Asset)인가?

세부 목적:

* 자체 제작 지정학 리스크 지수(`GPR_custom`)의 설명력 검증
* 공식 GPR(`GPR_zscore`)와 비교
* VIX 및 Fear&Greed 시장심리 변수와의 상대 설명력 비교
* GARCH-X와 EGARCH-X 구조에서 결론이 유지되는지 강건성 검증

---

## 3. 사용 데이터 (Dataset)

입력 파일:

```text
../datapipeline/master_data/master_data.csv
```

### 주요 컬럼

| 컬럼              | 설명                          |
| --------------- | --------------------------- |
| BTC             | BTC 로그 수익률                  |
| Gold            | 금 로그 수익률                    |
| SP500           | S&P500 로그 수익률               |
| NASDAQ          | NASDAQ 로그 수익률               |
| VIX             | 시장 공포 지수 (변동성 지수)                       |
| fear_greed      | CNN Fear & Greed            |
| fear_greed_lag1 | 전일 CNN 탐욕·공포 지수          |
| GPR_custom      | 자체 제작 지정학 리스크 지수 (F3_z)                 |
| GPR_zscore      |  Caldara & Iacoviello (2022) 공식 GPR Z-score|
| event_name      | 이벤트 구간 레이블                  |

### 표본 구성

* 분석 표본: 약 1,800 거래일
* 이벤트 기준 병합 데이터셋 사용
* BTC 수익률은 수렴 안정화를 위해 ×100 변환:

```text
returns_pct = BTC × 100
```

### 전처리

* 외생변수 Z-score 표준화
* X(t−1) 시차 적용
* 시간순 정렬
* 결측치 제거

---

## 4. GARCH-X / EGARCH-X 모형 구조

### GARCH-X 수식

```text
수익률 방정식:
r(t) = μ + ε(t),   ε(t) ~ Student-t(0, h(t), ν)

분산 방정식:
h(t) = ω + α·ε²(t−1) + β·h(t−1) + γ·X(t−1)
```

### EGARCH-X 수식 (강건성 검증용)

```text
ln h(t)
= ω
+ β·ln h(t−1)
+ α·(|z(t−1)| − E|z|)
+ γ_asym·z(t−1)
+ δ·X(t−1)
```

(Student-t 분포 사용: BTC 수익률의 fat-tail 특성 반영)

### 주요 파라미터 설명

| 파라미터     | 기호        | 설명                                  |
| -------- | --------- | ----------------------------------- |
| 기저 변동성   | ω (omega) | 기저 분산 상수, ≥ 0.05 강제 (과적합 방지)        |
| ARCH 효과  | α (alpha) | 전일 충격이 오늘 변동성에 미치는 영향               |
| GARCH 효과 | β (beta)  | 전일 변동성의 오늘 지속성                      |
| 외생변수 효과  | γ / δ     | 외생변수 1σ 증가에 따른 변동성 변화               |
| 비대칭 효과   | γ_asym    | 음·양 충격 비대칭 반응 (레버리지 효과)             |
| t분포 자유도  | ν (nu)    | fat-tail 두께 (>2 유지)                 |
| α + β    | —         | 충격 지속성 지표 (1에 가까울수록 persistence 강화) |

---

## 5. 모델 구성 (Model Specification)

### GARCH-X 모델 구성

| 모델     | 외생변수                               | 목적                |
| ------ | ---------------------------------- | ----------------- |
| Model1 | GPR_zscore                         | 공식 GPR 단독 벤치마크    |
| Model2 | GPR_custom                         | 자체 GPR 단독 설명력     |
| Model3 | VIX + fear_greed_lag1              | 시장 심리 설명력         |
| Model4 | GPR_zscore + VIX + fear_greed_lag1 | 공식 GPR + 시장 심리 통합 |
| Model5 | GPR_custom + VIX + fear_greed_lag1 | 자체 GPR + 시장 심리 통합 |

### EGARCH-X 모델 구성

| 모델        | 외생변수                               | 목적             |
| --------- | ---------------------------------- | -------------- |
| EGARCH_E1 | GPR_custom                         | 커스텀 GPR 단독 강건성 |
| EGARCH_E2 | GPR_zscore                         | 공식 GPR 단독 강건성  |
| EGARCH_E3 | VIX + fear_greed_lag1              | 시장심리 강건성 검증    |
| EGARCH_E4 | GPR_custom + VIX + fear_greed_lag1 | 통합 변수 강건성      |
| EGARCH_E5 | ΔGPR + VIX + fear_greed_lag1       | GPR 변화율 기반 검증  |
| EGARCH_E6 | GPR Dummy + VIX + fear_greed_lag1  | 이벤트 더미 기반 검증   |

### γ 해석 기준

| 조건              | 해석                            |
| --------------- | ----------------------------- |
| γ > 0, p < 0.05 | GPR↑ → BTC 변동성↑ (위험자산 특성)     |
| γ < 0, p < 0.05 | GPR↑ → BTC 변동성↓ (안전자산 특성)     |
| p ≥ 0.05        | 해당 변수가 BTC 변동성을 통계적으로 설명하지 못함 |

---

### 5.1. GARCH-X 모형 선택 근거

| 선택                | 논문                      | 근거 요약            |
| ----------------- | ----------------------- | ---------------- |
| ARCH 채택           | Engle (1982)            | 조건부 이분산성 존재 실증   |
| GARCH(1,1) 확장     | Bollerslev (1986)       | 변동성 지속성 구조 반영    |
| 외생변수 포함 (GARCH-X) | Han & Kristensen (2014) | 외생변수의 추가 설명력 정당화 |

---

### 5.2. 외생변수 선택 근거

| 변수           | 논문                          | 근거 요약                |
| ------------ | --------------------------- | -------------------- |
| GPR          | Caldara & Iacoviello (2022) | 지정학 리스크 공식 지수        |
| Fear & Greed | Bourghelle et al. (2022)    | BTC 변동성과 lead-lag 관계 |
| VIX          | Su et al. (2022)            | 시장 불확실성 대표 지표        |

---

### 5.3. Student-t 오차항 사용 근거

| 선택            | 논문                | 근거 요약                       |
| ------------- | ----------------- | --------------------------- |
| Student-t MLE | Liu et al. (2017) | BTC fat-tail 특성 반영 시 적합도 개선 |

---

### 5.4. α+β ≈ 1 해석 (near-IGARCH)

| 선택             | 논문                    | 근거 요약                |
| -------------- | --------------------- | -------------------- |
| α+β < 1 정상성 조건 | Bollerslev (1986)     | 정상성 경계 조건            |
| near-IGARCH 해석 | Bergsli et al. (2022) | 장기 persistence 구조 의미 |

---

### 5.5. MLE 추정 구현 근거

| 선택            | 논문                      | 근거 요약                        |
| ------------- | ----------------------- | ---------------------------- |
| Hessian 기반 SE | Calzolari et al. (1993) | 공분산행렬 추정 표준 방식               |
| 제약 파라미터 변환    | Doornik & Ooms (2003)   | constrained optimization 정당화 |
| Delta Method  | Anastasiou & Ley (2017) | 표준오차 복원 근거                   |
| 다중 초기값 탐색     | Mahmood & Khan (2020)   | likelihood multimodality 완화  |

---

### 5.6. 강건성 검증 근거

| 방법     | 논문                         | 근거 요약      |
| ------ | -------------------------- | ---------- |
| 이벤트 더미 | Spyrou & Kassimatis (1999) | 구조 변화 통제   |
| EGARCH | Nelson (1991)              | 비대칭 변동성 검증 |

---

### 5.7. AIC/BIC 기반 모형 선택 근거

AIC와 BIC는 로그우도(Log-Likelihood)를 기반으로 하되, 모형 복잡도에 대한 벌점을 함께 고려하는 대표적인 모형 선택 기준이다.

* AIC: 예측력 중심 기준
* BIC: 복잡도 패널티 강화 기준

본 연구에서는:

* 낮은 AIC/BIC
* 반복적 강건성 유지
* 경제적 해석 가능성

을 동시에 만족하는 모델을 최종 채택하였다.

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

## 7. 주요 결과 (Key Findings)

### 7.1 GARCH-X 모델 비교

| 모델     | 설명               |      AIC |      BIC |    α+β |
| ------ | ---------------- | -------: | -------: | -----: |
| Model3 | VIX + Fear&Greed | 9469.786 | 9508.231 | 0.9946 |
| Model4 | 공식 GPR + 시장심리    | 9471.506 | 9515.444 | 0.9944 |
| Model5 | 커스텀 GPR + 시장심리   | 9471.637 | 9515.575 | 0.9958 |
| Model2 | 커스텀 GPR 단독       | 9472.586 | 9505.540 | 0.9930 |
| Model1 | 공식 GPR 단독        | 9472.71 | 9505.664 | 0.9930 |

해석:

* AIC 기준 최적 모델은 `Model3`
* Fear & Greed 기반 시장심리 설명력이 가장 강함
* GPR 변수 추가 시 AIC 개선 미미

---

### 7.2 외생변수 γ 결과

| 모델     | 변수              |       γ | p-value |
| ------ | --------------- | ------: | ------: |
| Model1 | GPR_zscore      | -0.01057 |   0.8867 |
| Model2 | GPR_custom      | 0.03186 |   0.7092 |
| Model3 | VIX             | 0.00611 |   0.9527 |
| Model3 | fear_greed_lag1 |  0.1625 |   0.0467 |
| Model4 | GPR_zscore      |  0.02594 |   0.7051 |
| Model4 | fear_greed_lag1 |  0.16872 |   0.0438 |
| Model5 | GPR_custom      |  0.03994 |   0.6066 |
| Model5 | fear_greed_lag1 |  0.16464 |   0.0444 |

핵심 해석:

* GPR 관련 변수는 반복적으로 비유의
* Fear & Greed는 반복적으로 유의
* BTC 변동성은 지정학 자체보다 시장 심리에 더 민감

---

### 7.3 EGARCH 강건성 검증

| 모델        | 설명                            |      AIC |
| --------- | ----------------------------- | -------: |
| EGARCH_E3 | VIX + Fear&Greed              | 9450.125 |
| EGARCH_E6 | GPR Dummy + VIX + Fear&Greed  | 9450.972 |
| EGARCH_E4 | GPR_custom + VIX + Fear&Greed | 9451.524 |
| EGARCH_E5 | ΔGPR + VIX + Fear&Greed       | 9451.997 |
| EGARCH_E2 | GPR_zscore                    | 9454.858 |
| EGARCH_E1 | GPR_custom                    | 9455.470 |

해석:

* EGARCH에서도 Fear & Greed 중심 결론 유지
* EGARCH_E3가 최저 AIC
* 비대칭 구조를 허용해도 GPR은 핵심 변수로 나타나지 않음

---

### 7.4 EGARCH 외생변수 유의성

| 모델        | 변수                     | p-value |
| --------- | ---------------------- | ------: |
| EGARCH_E3 | fear_greed_lag1_scaled |  0.0292 |
| EGARCH_E4 | fear_greed_lag1_scaled |  0.0236 |
| EGARCH_E5 | fear_greed_lag1_scaled |  0.0318 |
| EGARCH_E6 | fear_greed_lag1_scaled |  0.0223 |

해석:

Fear & Greed 변수는 EGARCH 구조에서도 반복적으로 유의.

---

### 7.5 EGARCH 비대칭 효과

| 모델        | gamma_asym | p-value |
| --------- | ---------: | ------: |
| EGARCH_E1 |     0.0061 |  0.7435 |
| EGARCH_E2 |     0.0040 |  0.8308 |
| EGARCH_E3 |    -0.0134 |  0.5045 |
| EGARCH_E4 |    -0.0157 |  0.4381 |
| EGARCH_E5 |    -0.0131 |  0.5148 |
| EGARCH_E6 |    -0.0161 |  0.4262 |

해석:

* 레버리지 효과는 통계적으로 유의하지 않음
* EGARCH는 “비대칭성 입증”보다는 강건성 검증 역할

---

## 8. 최종 결론

### 핵심 결론

* BTC 변동성은 지정학 리스크보다 시장심리(Fear & Greed)의 영향을 더 크게 받음
* GPR 및 Custom GPR 변수는 모든 GARCH 모형에서 유의하지 않음
* Fear & Greed는 반복적으로 유의한 설명변수로 확인됨
* GARCH 기준 최적 모델은 Model3(VIX + Fear & Greed)
* α+β≈0.995로 변동성 충격의 지속성이 매우 높음
* BTC 변동성은 지정학 이벤트 자체보다 투자심리 변화에 더 민감하게 반응함

### 종합 판단

> BTC는 지정학 충격에 의해 직접적으로 변동성이 확대되기보다는,
> 시장 참여자의 위험선호와 투자심리에 의해 변동성이 결정되는 경향이 강하게 나타났다.
> 따라서 본 연구에서는 Safe Haven보다는 시장심리에 민감한 Risk Asset 특성이 더 우세한 것으로 판단된다.

---

## 9. 저장 결과 파일 (Output)

### CSV

| 파일                                     | 내용                                          |
| -------------------------------------- | ------------------------------------------- |
| `garch_model_comparison.csv`           | GARCH 주요 모델(Model1~5)의 LogLik·AIC·BIC 비교 결과 |
| `garch_gamma_results.csv`              | GARCH 외생변수 γ 계수 및 p-value 결과                |
| `garch_model_params.csv`               | 각 GARCH 모델의 전체 추정 파라미터(ω·α·β·γ·ν) 저장        |
| `garch_event_dummy_comparison.csv`     | 이벤트 더미 포함 전·후 GARCH 모델 성능 비교                |
| `garch_conditional_volatility.csv`     | 시점별 조건부 변동성 σ(t) 저장                         |
| `egarch_model_comparison.csv`          | EGARCH 모델 간 AIC/BIC 비교 결과                   |
| `egarch_exog_coefficients.csv`         | EGARCH 외생변수 계수(δ) 및 p-value 결과              |
| `garch_egarch_integrated_summary.csv`  | GARCH·EGARCH 전체 모델 비교 통합 요약표                |
| `egarch_step_b3_coefficients_long.csv` | EGARCH 계수 long-format 저장 (Plotly·Heatmap용)  |
| `egarch_step_b3_coefficients_wide.csv` | EGARCH 계수 wide-format 저장 (논문 표 정리용)         |
| `garch_significance_matrix.csv`        | γ/δ 계수 유의성 여부(0/1) 정리 행렬                    |
| `garch_persistence.csv`                | 모델별 α·β·α+β persistence 비교                  |
| `garch_model_ranking.csv`              | AIC 기준 GARCH/EGARCH 모델 순위표                  |
| `garch_event_volatility.csv`           | 이벤트 ±30일 구간 평균·최대 변동성 비교                    |
| `garch_gamma_long.csv`                 | γ 계수 long-format 저장 (대시보드 interactive 시각화용) |

---

### PNG

| 파일                               | 내용                          |
| -------------------------------- | --------------------------- |
| `garch_conditional_vol.png`      | GARCH 조건부 변동성 시계열 그래프       |
| `garch_gamma_coefficients.png`   | γ 계수 및 유의성 비교 시각화           |
| `garch_model_comparison.png`     | GARCH 모델별 AIC/BIC 비교 차트     |
| `egarch_model_aic_bic.png`       | EGARCH 모델 간 적합도(AIC/BIC) 비교 |
| `egarch_cond_vol_comparison.png` | GARCH vs EGARCH 조건부 변동성 비교  |
| `egarch_gpr_coef_compare.png`    | GPR 관련 계수 비교 시각화            |


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
