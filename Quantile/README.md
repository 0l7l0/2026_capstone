# Quantile Regression — 분위수 회귀 분석

## 1. 파일 개요 (Overview)

`quantile_regression.ipynb`는 지정학적 리스크(GPR) 환경에서 Bitcoin(BTC)의 Safe-Haven 여부를 검증하기 위한 분위수 회귀(Quantile Regression) 분석 노트북이다.

평균 중심 OLS가 아닌 분위수 회귀를 이용하여 BTC 수익률 분포의 극단 구간(τ ≤ 0.10)에서 주식(S&P500) 및 금(Gold)과의 관계를 분석하였다.

또한 GPR 상승 시 BTC-자산 관계가 변화하는지 확인하기 위해 상호작용항(Interaction Term)을 추가하였으며, 다양한 강건성 검정을 통해 결과의 안정성을 검증하였다.

---

## 2. 분석 목적 (Objective)

### 핵심 연구 질문

> 금융시장 급락 구간에서 BTC는 Safe Haven인가?

이를 위해 다음을 검증한다.

* 극단 하락 분위수(τ=0.01~0.10)에서 BTC와 S&P500의 관계
* 극단 하락 분위수에서 BTC와 Gold의 관계
* GPR 상승 시 BTC-자산 관계 변화 여부
* 특정 이벤트 또는 변수 설정에 의존한 결과인지 여부

---

## 3. 사용 데이터 (Dataset)

### 입력 파일

```text
master_data.csv
```

### 주요 변수

| 변수         | 설명               |
| ---------- | ---------------- |
| BTC        | BTC 로그수익률 (종속변수) |
| SP500      | S&P500 로그수익률     |
| Gold       | 금 선물 로그수익률       |
| GPR_custom | 자체 구축 지정학 리스크 지수 |
| event_name | 이벤트 구간 식별 변수     |

### 이벤트 구간

* Hormuz Crisis
* Soleimani Assassination
* Russia–Ukraine War
* Israel–Hamas War
* Israel–Iran Conflict
* US–Israel–Iran Conflict

### 표본

```text
약 1,827 거래일
6개 이벤트 구간 통합
```

### 전처리

* 결측치 제거
* Z-score 표준화
* Min-Max 표준화 (강건성 검정)
* 상호작용항 생성

---

## 4. 주요 변수 설명 (Features)

| 변수      | 기호    | 설명               |
| ------- | ----- | ---------------- |
| 분위수     | τ     | 조건부 수익률 분위       |
| 시장효과    | β     | SP500 또는 Gold 효과 |
| 지정학 리스크 | γ     | GPR 효과           |
| 상호작용    | δ     | Asset × GPR 효과   |
| 표준오차    | HAC   | Newey-West 보정    |
| 유효표본수   | eff_n | Kernel 기반 유효 표본수 |

---

## 5. 모델 구성 (Model Specification)

### 5.1 기본 분위수 회귀

```text
Qτ(BTC)
=
ατ
+
βτ · Asset_z
+
γτ · GPR_custom_z
+
ετ
```

### 모델 구성

| 모델        | 설명                |
| --------- | ----------------- |
| SP500+GPR | BTC ~ SP500 + GPR |
| Gold+GPR  | BTC ~ Gold + GPR  |

---

### 5.2 상호작용항 모델

```text
Qτ(BTC)
=
ατ
+
βτ · Asset_z
+
γτ · GPR_custom_z
+
δτ · (Asset_z × GPR_custom_z)
+
ετ
```

### 상호작용항 모델

| 모델           | 설명          |
| ------------ | ----------- |
| SP500+GPR+IA | SP500 × GPR |
| Gold+GPR+IA  | Gold × GPR  |

---

### 5.3 Safe-Haven 판정 기준

(Baur & Lucey, 2010)

| 조건               | 판정           |
| ---------------- | ------------ |
| β < 0 & p < 0.05 | ✅ Safe Haven |
| β > 0 & p < 0.05 | ❌ Risk Asset |
| p ≥ 0.05         | ⚪ 비유의        |

### 상호작용항 해석

| 조건               | 해석                     |
| ---------------- | ---------------------- |
| δ < 0 & p < 0.05 | GPR 상승 시 Safe-Haven 강화 |
| δ > 0 & p < 0.05 | GPR 상승 시 위험자산 동조화 강화   |
| p ≥ 0.05         | 상호작용 효과 없음             |

---

## 6. 분석 절차 (Methodology)

| Step    | 내용            |
| ------- | ------------- |
| Step 1  | 데이터 로드        |
| Step 2  | 표준화(Z-score)  |
| Step 3  | 전체 분위수 회귀     |
| Step 4  | 이벤트별 분위수 회귀   |
| Step 5  | 상호작용항 분위수 회귀  |
| Step 6  | β 경로 시각화      |
| Step 7  | γ 경로 시각화      |
| Step 8  | 이벤트×분위수 히트맵   |
| Step 9  | Safe-Haven 판정 |
| Step 10 | 강건성 검정        |
| Step 11 | 결과 저장         |

---

## 7. 강건성 검정 (Robustness Tests)

### ① GPR 제거 검정

```text
기존:
BTC ~ Asset + GPR

수정:
BTC ~ Asset
```

목적:

* GPR이 β 추정을 왜곡하는지 확인

결과:

```text
SP500 : 방향 일치 10/10
Gold  : 방향 일치 10/10
```

→ GPR 포함 여부와 무관하게 결론 유지

---

### ② Leave-One-Event-Out (LOO)

방법:

```text
이벤트 1개 제거
→ 전체 분석 반복
```

목적:

* 특정 이벤트가 결과를 지배하는지 확인

결과:

```text
SP500 모델 결론 유지
Gold 모델 일부 민감성 존재
```

---

### ③ 표준화 변경 검정

```text
Z-score
↓
Min-Max Scaling
```

목적:

* 스케일링 방식 의존성 확인

결과:

```text
방향 동일
유의성 동일
```

---

## 8. 주요 결과 (Key Findings)

### SP500 모델

| τ    | β        | p-value | 해석         |
| ---- | -------- | ------- | ---------- |
| 0.01 | +0.02682 | <0.001  | 강한 동조화     |
| 0.05 | +0.01766 | <0.001  | Risk Asset |
| 0.10 | +0.01575 | <0.001  | Risk Asset |
| 0.50 | +0.01099 | <0.001  | 평상시 기준     |

### 핵심 해석

```text
주식이 급락할수록
BTC도 함께 하락

→ Safe Haven 아님
→ Risk Asset
```

---

### Gold 모델

| τ    | β        | p-value |
| ---- | -------- | ------- |
| 0.01 | +0.01769 | <0.001  |
| 0.05 | +0.00614 | <0.001  |
| 0.10 | +0.00426 | 0.003   |

결론:

```text
Gold와도 같은 방향

→ Gold-like Safe Haven 아님
```

---

### GPR 효과

결과:

```text
γ(GPR) 대부분 비유의
```

해석:

```text
지정학 리스크 자체가
BTC 수익률을 직접 설명하지 못함
```

---

### 상호작용항 결과

SP500 × GPR

```text
δ > 0
```

해석:

```text
GPR 상승 시
SP500-BTC 동조화 강화

→ Safe Haven 강화 아님
```

---

## 9. 최종 결론 (Conclusion)

### 연구 결과

BTC는

```text
모든 주요 이벤트
모든 극단 하락 분위수
모든 강건성 검정
```

에서

```text
Safe Haven으로 확인되지 않음
```

오히려

```text
SP500과 유의한 양(+)의 관계
```

를 유지하며

```text
Risk Asset 성격
```

을 보였다.

또한 GPR 상승 시 BTC의 Safe-Haven 기능이 강화되지 않았으며, 일부 구간에서는 시장과의 동조화가 오히려 증가하였다.

---

## 10. 산출물 (Output)

### CSV

| 파일                        | 설명               |
| ------------------------- | ---------------- |
| quantreg_main.csv         | 기본 분위수 회귀 전체 결과  |
| quantreg_ia.csv           | 상호작용항 회귀 결과      |
| quantreg_results.csv      | 요약 결과            |
| quantreg_results_ia.csv   | 상호작용항 요약 결과      |
| robust_iv.csv             | GPR 제거 검정        |
| robust_loo.csv            | Leave-One-Out 검정 |
| robust_mm.csv             | Min-Max 검정       |
| quantreg_beta_path.csv    | β 경로 데이터         |
| quantreg_beta_path_ia.csv | β 경로 (상호작용항)     |
| quantreg_heatmap.csv      | 히트맵 원본 데이터       |
| quantreg_heatmap_ia.csv   | 상호작용 히트맵 데이터     |

### PNG

| 파일                         | 설명               |
| -------------------------- | ---------------- |
| quantreg_beta_path.png     | β 분위수 경로         |
| quantreg_beta_path_ia.png  | β 분위수 경로 (상호작용항) |
| quantreg_gamma_path.png    | γ 분위수 경로         |
| quantreg_gamma_path_ia.png | γ 분위수 경로 (상호작용항) |
| quantreg_heatmap.png       | 이벤트×분위수 히트맵      |
| quantreg_heatmap_ia.png    | 상호작용항 히트맵        |

---

## 11. 참고문헌 (References)

- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.
- Koenker, R. (2005). *Quantile Regression*. Cambridge University Press.
- Newey, W. K., & West, K. D. (1987). A Simple, Positive Semidefinite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix. *Econometrica*, 55, 703–708.
- Newey, W. K., & West, K. D. (1994). Automatic Lag Selection in Covariance Matrix Estimation. *The Review of Economic Studies*, 61(4), 631–653.
- Politis, D. N., & Romano, J. P. (1994). The Stationary Bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313.
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229.
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
