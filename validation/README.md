# Validation — 독립 검증

본분석 3종(이벤트 스터디, 분위수 회귀, GARCH-X)의 학술 표준 충족 여부를 독립적으로 점검하고, Baur & Lucey (2010) 안전자산 3조건을 기계적으로 채점한 결과를 제공합니다.

분석 대상 기간은 2019-01-02 ~ 2026-04-30 (1,800 거래일)이며, 6개 지정학 이벤트를 대상으로 수행되었습니다.

---

## 1. 검증 목적

본분석이 통계적 결론을 올바르게 도출했는지 다음 세 가지 측면에서 점검합니다.

1. **학술 표준 충족 여부** — `catalog.json`에 정의된 33개 점검 항목 기준으로 본분석의 파라미터 설정·검정 절차·누락 여부를 확인
2. **통합 판정 재현** — Baur & Lucey (2010) C1·C2·C3 조건을 6개 이벤트별로 기계적으로 채점
3. **추가 강건성 검정** — 본분석에서 수행하지 않은 BH-FDR 다중검정 보정, Placebo 검정(200회), Wild Bootstrap을 보완 적용

---

## 2. 검증 기준 (catalog.json)

`catalog.json`은 7개 방법론에 대해 학술 표준을 정의합니다.

| 방법론 | 주요 점검 항목 |
|--------|--------------|
| 이벤트 스터디 | 추정창 길이, 이벤트창 설정, 정상 수익률 모델 선택 |
| GARCH-X | GARCH(1,1) 차수, Student-t MLE, 외생변수 시차 처리 |
| 분위수 회귀 | 분위수 τ 값(0.05·0.10·0.50), HAC Newey-West SE 적용 |
| BH-FDR | 다중검정 family 정의, step-up 절차 적용 |
| Placebo 검정 | 무작위 이벤트 200회 시뮬레이션 |
| Wild Bootstrap | 소표본 이벤트 적용 기준 |
| Ljung-Box | 표준화 잔차 자기상관 및 ARCH 잔존 검사 |

---

## 3. 검증 결과

### 학술 표준 점검

catalog v1.6 기준 33개 항목 전부 통과했습니다.

| 분석 | 점검 항목 수 | 결과 |
|------|:-----------:|------|
| 이벤트 스터디 | 11 | PASS 11/11 |
| GARCH-X | 14 | PASS 14/14 |
| 분위수 회귀 | 9 | PASS 9/9 |
| **합계** | **34** | **PASS 34/0/0** |

### Baur & Lucey (2010) 3조건 통합 판정

| 이벤트 | C1 (CAR ≥ 0) | C2 (β ≤ 0) | C3 (GPR γ 비유의) | 점수 | 판정 |
|--------|:-----------:|:----------:|:-----------------:|:----:|------|
| 호르무즈 위기 | ✅ +0.081 | ✅ −0.012 | ✅ | 3/3 | Safe Haven* |
| 솔레이마니 암살 | ✅ +0.142 | ❌ +0.014 | ✅ | 2/3 | Weak Haven |
| 러-우 전쟁 | ✅ +0.113 | ❌ +0.032 | ✅ | 2/3 | Weak Haven |
| 이스라엘-하마스 | ❌ −0.029 | ❌ +0.013 | ✅ | 1/3 | Diversifier |
| 이스라엘-이란 충돌 | ❌ −0.063 | ❌ +0.024 | ✅ | 1/3 | Diversifier |
| 미-이스라엘-이란 | ✅ +0.132 | ❌ +0.015 | ✅ | 2/3 | Weak Haven |

> \* Safe Haven 조건은 부호 기준 충족하나, BH-FDR 보정 및 Placebo 검정에서 통계적 유의성이 확보되지 않아 강도가 약함.

**C3 기준**: GPR 관련 변수(GPR_custom, GPR_zscore)를 포함한 4개 모델(Model1·2·4·5)에서 γ 계수가 모두 비유의(p = 0.61~0.89). VIX와 Fear & Greed는 통제변수로 별도 보고.

### 추가 강건성 검정 결과

| 검정 | 결과 |
|------|------|
| BH-FDR 보정 (30개 검정) | Gold 이스라엘-이란 유일 유의(원본 p=0.040) → 보정 후 비유의(p=0.849). BTC 전체 비유의 |
| Placebo 검정 (200회) | 6개 이벤트 모두 p > 0.05 — 실제 이벤트 효과가 무작위 창과 통계적으로 구분되지 않음 |
| Wild Bootstrap (호르무즈) | 추정창 86일로 짧아 별도 적용. p=0.236 → 통계 강도 약함 확인 |
| Ljung-Box 잔차 진단 | lag 5·10·20 자기상관 없음 (p=0.42·0.57·0.55). 잔차 제곱 lag 5에서 ARCH 효과 약하게 잔존(p=0.009)하나 EGARCH 비대칭 효과로 흡수 |

---

## 4. 학술 권고 사항

자동 점검과 별개로, 논문화 시 보완이 권고되는 사항입니다.

| # | 사항 | 권고 |
|---|------|------|
| 1 | 호르무즈 추정창 86일 (표준 95일보다 짧음) | Wild Bootstrap 적용 사실 및 한계 명시 |
| 2 | EGARCH AIC(9,559)가 GARCH(9,578)보다 낮으나 부록 처리 | 본문에 모델 선정 근거 명시 |
| 3 | 분위수 회귀 BH family 사전 정의 누락 | 분석 전 family 범위를 마크다운으로 명시 |
| 4 | GARCH-X 외생변수 외생성 검증 미수행 | Granger 인과·Hausman 검정 추가 (논문화 시) |
| 5 | ADF 검정에 구조변화 미반영 | Zivot-Andrews 검정 추가 (논문화 시) |
| 6 | 분위수 회귀 호르무즈 유효 표본 n ≈ 9 | 소표본 한계 명시 및 해석 보류 |

---

## 5. 결과 파일

| 파일 | 설명 |
|------|------|
| `catalog.json` | 학술 표준 정의 v1.6 — 7개 방법론별 점검 기준 |
| `final_judgment.csv` | Baur-Lucey 3조건 채점 결과 (6개 이벤트) |
| `final_report.md` | 학술 요약 보고서 |
| `event_study_car_bh.csv` | CAR + BH-FDR 보정 p값 (6 이벤트 × 5 자산) |
| `event_study_placebo.csv` | Placebo 200회 시뮬레이션 결과 |
| `event_study_car_wild_bh.csv` | Wild Bootstrap 결과 (호르무즈 한정) |
| `multiple_testing_adjusted.csv` | 이벤트 스터디·분위수 회귀 통합 BH-FDR 결과 |
| `garch_ljung_box.csv` | GARCH 잔차 Ljung-Box 검정 결과 |
| `garch_gpr_gamma_extraction.csv` | C3 채점 기준 GPR γ 추출값 (Model1·2·4·5) |
| `garch_all_gamma_extraction.csv` | 전체 γ 계수 (GPR·VIX·Fear&Greed) |

---

## 6. 참고문헌

**안전자산 판정**
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229.

**이벤트 스터디**
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39.

**분위수 회귀**
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.
- Newey, W. K., & West, K. D. (1987). HAC Covariance Matrix. *Econometrica*, 55, 703–708.

**GARCH**
- Engle, R. F. (1982). ARCH. *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). GARCH. *Journal of Econometrics*, 31(3), 307–327.
- Nelson, D. B. (1991). EGARCH. *Econometrica*, 59(2), 347–370.

**다중검정 보정 및 강건성**
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS-B*, 57(1), 289–300.
- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361–376.

**지정학 리스크**
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *AER*, 112(4), 1194–1225.
- Bourghelle, D., Jawadi, F., & Rozin, P. (2022). Do Collective Emotions Drive Bitcoin Volatility? *Finance Research Letters*, 45, 102041.
