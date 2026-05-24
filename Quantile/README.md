# Quantile Regression — 분위 회귀 분석

## 1. 파일 개요 (Overview)

`quantile_regression.ipynb`는 주식 시장 극단적 하락 구간(τ = 0.05, 0.10)에서 BTC가 안전자산처럼 반대로 움직이는지 검증하는 분위 회귀 분석 노트북입니다.  
기본 모델·상호작용항 모델 두 가지를 두 개의 독립변수 조합(SP500+GPR / Gold+GPR)으로 실행하고, 4종 강건성 검정(GPR 제거·LOO·표준화 변경·블록 부트스트랩)으로 결론의 안정성을 확인합니다.

---

## 2. 분석 목적 (Objective)

- **핵심 질문**: 주식이 폭락하는 극단 구간(τ ≤ 0.10)에서 BTC는 반대로 움직이는가? → Safe Haven인가?
- OLS가 놓치는 **위기 구간(하위 5~10%)의 조건부 관계**를 분위 회귀로 포착
- GPR(지정학 리스크) 상승 시 BTC-주식 동조화 구조가 변하는지 상호작용항(δ)으로 검증
- HAC(Newey-West) 표준오차 + 블록 부트스트랩으로 시계열 이분산·자기상관 보정

---

## 3. 사용 데이터 (Dataset)

**입력 파일**: `master_data.csv`

| 컬럼 | 설명 |
|------|------|
| `BTC` | BTC 일별 로그 수익률 (종속변수) |
| `SP500` | S&P 500 로그 수익률 |
| `Gold` | 금 선물 로그 수익률 |
| `GPR_custom` | 자체 제작 지정학 리스크 지수 (F3_z) |
| `event_name` | 이벤트 구간 레이블 (6개) |

- **분석 표본**: 1,827 거래일 (6개 이벤트 구간 병합)
- **전처리**: Z-score 표준화 (`_z` 컬럼 생성), 결측치 제거 (BTC·SP500·GPR·Gold 동시 존재 행만 사용)
- **분위수(TAUS)**: 0.01, 0.025, 0.05, 0.10, 0.20, 0.25, 0.50, 0.75, 0.80, 0.90, 0.95

---

## 4. 주요 변수 설명 (Features)

| 변수 | 기호 | 설명 |
|------|------|------|
| 분위수 | τ (tau) | 분석 구간 (τ=0.05 → BTC 수익률 하위 5%에서의 조건부 관계) |
| 주 계수 | β (beta) | 독립변수 1σ 변화 → BTC 수익률 변화량 **핵심 분석 대상** |
| GPR 계수 | γ (gamma) | GPR_custom 1σ 변화 → BTC 수익률 변화량 |
| 상호작용 계수 | δ (delta) | GPR 상승 시 β가 강화(δ>0)·약화(δ<0)되는 정도 |
| HAC 대역폭 | bw | Newey-West 시차 수 = `max(1, int(4×(n/100)^(2/9)))` |

**Safe-Haven 판정 기준 (Baur & Lucey 2010)**

| 조건 | 판정 |
|------|------|
| β < 0, p < 0.05 (τ ≤ 0.10) | ✅ Safe Haven |
| β > 0, p < 0.05 (τ ≤ 0.10) | ❌ Risky Asset |
| p ≥ 0.05 | ⚪ 비유의 |
| δ < 0, p < 0.05 | GPR 상승 시 Safe Haven 성격 강화 |
| δ > 0, p < 0.05 | GPR 상승 시 위험자산 동조화 강화 |

---

## 5. 모델 구성 (Model Specification)

**기본 모델 (Step 3)**

```
Q_τ(BTC) = α_τ + β_τ·Asset_z + γ_τ·GPR_custom_z + ε

Model A: Asset = SP500  → 주식 동조화 검증
Model B: Asset = Gold   → 금 동조화 검증
```

**상호작용항 모델 (Step 4)**

```
Q_τ(BTC) = α_τ + β_τ·Asset_z + γ_τ·GPR_custom_z + δ_τ·(Asset_z × GPR_custom_z) + ε

δ < 0, p < 0.05 → GPR↑ 시 동조화 약화 → Safe Haven 강화
δ > 0, p < 0.05 → GPR↑ 시 동조화 강화 → 위험자산 성격
```

---

## 6. 분석 방법론 (Methodology)

| Step | 내용 | 세부 방법 |
|------|------|-----------|
| 0 | 라이브러리 설정 | |
| 1 | 데이터 로드 | master_data.csv |
| 2 | 분석 데이터 준비 | Z-score 표준화, 분위수 확인 |
| 3 | 기본 분위 회귀 | SP500+GPR·Gold+GPR 모델, HAC SE + 블록 부트스트랩, 전체합산 + 이벤트별 |
| 4 | 상호작용항 모델 | δ 계수 추정, 다중공선성 사전 진단 (r>0.7 경고) |
| 5 | 시각화 | β 경로 그래프(분위별), γ 경로, 히트맵 |
| 6 | Baur & Lucey 분류 | Safe Haven / Risky Asset 최종 판정 |
| 7 | 결과 저장 | |
| 8 | 강건성 검정 (4종) | ① GPR 제거, ② LOO, ③ Min-Max 표준화, ④ 블록 부트스트랩 |
| 9 | 전체 결과 저장 | |

**강건성 검정 상세**

| 검정 | 방법 | 목적 |
|------|------|------|
| ① GPR 제거 | GPR_custom 제거 후 β 재추정 | GPR이 SP500·Gold 효과를 왜곡하는지 확인 |
| ② LOO | 이벤트 하나씩 제외 후 전체 재추정 | 특정 이벤트가 결론을 지배하는지 확인 |
| ③ Min-Max | Z-score → Min-Max 표준화 | 표준화 방식에 따른 β 변화 확인 |
| ④ 블록 부트스트랩 | 21일 블록 단위 재샘플링 | 시계열 자기상관 보존하며 p-value 교차 검증 |

---

## 7. 주요 결과 (Key Findings)

**전체 합산 — 기본 모델 β 계수 (SP500+GPR)**

| τ | β (SP500) | p | 해석 |
|---|-----------|---|------|
| 0.01 | +0.024 | <0.001 | ❌ 극단 하락 시 가장 강한 동조화 |
| 0.05 | +0.016 | <0.001 | ❌ Risky Asset |
| 0.10 | +0.016 | <0.001 | ❌ Risky Asset |
| 0.50 | +0.011 | <0.001 | 평상시 기준 |

**전체 합산 — 기본 모델 β 계수 (Gold+GPR)**

| τ | β (Gold) | p | 해석 |
|---|----------|---|------|
| 0.01 | +0.015 | <0.001 | ❌ Risky Asset |
| 0.05 | +0.006 | 0.001 | ❌ Risky Asset |
| 0.10 | +0.004 | 0.005 | ❌ Risky Asset |
| 0.50 | +0.004 | <0.001 | 평상시 기준 |

**이벤트별 Safe-Haven 판정 (τ = 0.05)**

| 이벤트 | SP500 모델 | Gold 모델 | 종합 |
|--------|-----------|----------|------|
| 전체 합산 | ❌ Risky Asset | ❌ Risky Asset | 확고한 위험자산 |
| 호르무즈 위기 | ⚪ 비유의 | ❌ Risky Asset | 금 변동성에 기생 |
| 솔레이마니 암살 | ❌ Risky Asset | ❌ Risky Asset | 주식·금 동반 폭락 |
| 러-우 전쟁 | ❌ Risky Asset | ⚪ 비유의 | 주식 추종 (금과 무관) |
| 이스라엘-하마스 | ❌ Risky Asset | ⚪ 비유의 | 주식 추종 |
| 이스라엘-이란 충돌 | ❌ Risky Asset | ⚪ 비유의 | 주식 추종 |
| 이란 전쟁 | ❌ Risky Asset | ⚪ 비유의 | 주식 추종 |

**상호작용항 결과 (전체합산, τ = 0.05)**

| 모델 | δ (SP500×GPR / Gold×GPR) | p | 해석 |
|------|--------------------------|---|------|
| SP500+GPR+IA | +0.005 | 0.037 | GPR↑ → SP500-BTC 동조화 강화 ❌ |
| Gold+GPR+IA | +0.004 | 0.559 | 비유의 |

**강건성 검정 종합**

| 검정 | SP500 모델 | Gold 모델 |
|------|-----------|----------|
| ① GPR 제거 | 전 분위수 방향 일치, 최대 변화율 8.5% | 전 분위수 방향 일치, 최대 14.8% |
| ② LOO | 6개 이벤트 모두 제외 시 결론 유지 | 호르무즈·솔레이마니 제외 시 비유의 전환 |
| ③ Min-Max | 방향·유의성 모두 일치 | 방향·유의성 모두 일치 |
| ④ 블록 부트스트랩 | HAC p-value와 일관됨 | HAC p-value와 일관됨 |

> **핵심 결론**
> - **BTC는 모든 이벤트·모든 위기 분위수에서 ❌ Risky Asset** — 주식 폭락 시 BTC도 함께 하락
> - 평상시(τ=0.50) 대비 극단 하락(τ=0.01) 구간에서 SP500-BTC 동조화가 오히려 **2.2배 강해짐**
> - GPR 상승 시 동조화가 **완화되지 않고 오히려 강화** → Safe Haven 조건 정반대
> - SP500 모델 결론은 4종 강건성 검정 모두에서 안정적으로 유지됨
> - Gold 모델은 호르무즈·솔레이마니 이벤트 제거 시 판정이 변하여 SP500 모델보다 민감함

---

## 8. 결과 파일 (Output)

| 파일 | 유형 | 내용 |
|------|------|------|
| `result_csv_png/quantreg_main.csv` | CSV | 전체합산·이벤트별 전체 분위 회귀 결과 (β·SE·p·n) |
| `result_csv_png/quantile_results_bh.csv` | CSV | BH 다중검정 보정 적용 결과 |
| `result_csv_png/robust_loo.csv` | CSV | LOO 강건성 검정 결과 |
| `result_csv_png/robust_mm.csv` | CSV | Min-Max 표준화 강건성 결과 |
| `result_csv_png/quantreg_beta_path.png` | PNG | SP500·Gold β 계수 분위별 경로 |
| `result_csv_png/quantreg_gamma_path.png` | PNG | GPR γ 계수 분위별 경로 |
| `result_csv_png/quantreg_heatmap.png` | PNG | 이벤트×분위수 β 히트맵 |

---

## 9. 참고문헌 (References)

- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.
- Koenker, R. (2005). *Quantile Regression*. Cambridge University Press.
- Newey, W. K., & West, K. D. (1987). A Simple, Positive Semidefinite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix. *Econometrica*, 55, 703–708.
- Newey, W. K., & West, K. D. (1994). Automatic Lag Selection in Covariance Matrix Estimation. *The Review of Economic Studies*, 61(4), 631–653.
- Politis, D. N., & Romano, J. P. (1994). The Stationary Bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313.
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229.
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
