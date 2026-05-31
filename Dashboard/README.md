# ₿ BTC Safe Haven Dashboard

## 1. 프로젝트 개요 (Overview)

본 대시보드는 비트코인(BTC)이 지정학적 위기 상황에서 안전자산(Safe Haven) 역할을 수행하는지 검증하기 위해 구축되었다.

연구는 2019~2026년 주요 지정학 이벤트를 대상으로 수행되었으며, Event Study(C1), Quantile Regression(C2), GARCH(C3)의 세 가지 분석 방법을 통합하여 BTC의 안전자산 특성을 평가한다.

대시보드는 각 분석 결과와 최종 판정을 시각적으로 제공하며, 연구 전체 흐름을 한 화면에서 확인할 수 있도록 설계되었다.

---

## 2. Dashboard 구성

대시보드는 총 6개의 탭으로 구성된다.

| 탭                        | 내용                     |
| ------------------------ | ---------------------- |
| 통합 판정                    | Safe Haven 종합 결과       |
| GPR 파이프라인                | Custom GPR 구축 과정       |
| EDA                      | 기초 통계 및 상관관계 분석        |
| Event Study (C1)         | 이벤트 발생 시 초과수익률(CAR) 검정 |
| Quantile Regression (C2) | 극단 하락 구간 Safe Haven 검정 |
| GARCH-X / EGARCH (C3)    | 지정학 리스크의 변동성 영향 검정     |

---

## 3. Safe Haven 평가 체계

본 연구는 Baur & Lucey (2010)의 안전자산 개념을 참고하여 세 가지 조건을 이벤트별로 평가한다.

| 조건 | 설명                                  |
| -- | ----------------------------------- |
| C1 | Event Study 기반 CAR 방향성 검정           |
| C2 | Quantile Regression 기반 하방 위험 동조화 검정 |
| C3 | GARCH 기반 변동성 영향 검정                  |

각 조건 결과를 종합하여 이벤트별 Safe Haven 특성을 평가한다.

---

## 4. 주요 결과 (Key Findings)

### Event Study (C1)

* BTC는 6개 이벤트 중 4개에서 양(+) CAR를 기록하였다.
* 그러나 BH-FDR 다중검정 보정 후 모든 이벤트가 비유의로 나타났다.
* 전쟁 충격 시 일관된 초과수익 증거는 확인되지 않았다.

### Quantile Regression (C2)

* 하방 극단 구간(τ ≤ 0.10)에서 BTC와 SP500의 동조화가 강화되었다.
* 6개 이벤트 중 5개 이벤트에서 Safe Haven 조건을 충족하지 못하였다.
* 시장 급락 시 BTC의 분산 기능은 제한적인 것으로 나타났다.

### GARCH-X / EGARCH (C3)

* GPR 계수(γ)는 GARCH·EGARCH 전 모델에서 비유의로 나타났다.
* Fear & Greed 지수는 반복적으로 유의하였다.
* BTC 변동성은 지정학 리스크보다 시장심리에 더 민감한 것으로 나타났다.

---

## 5. 최종 통합 판정

이벤트별 통합 평가 결과는 다음과 같다.

| 이벤트          | 최종 판정       |
| ------------ | ----------- |
| 호르무즈 위기      | Safe Haven* |
| 솔레이마니 암살     | Weak Haven  |
| 러-우 전쟁       | Weak Haven  |
| 이스라엘-하마스 전쟁  | Diversifier |
| 이스라엘-이란 충돌   | Diversifier |
| 미-이스라엘-이란 충돌 | Weak Haven  |

### 종합 결론

* BTC는 일부 이벤트에서 Safe Haven 방향성을 보였으나 일관된 안전자산으로 확인되지는 않았다.
* Event Study에서는 강한 초과수익 증거가 확인되지 않았다.
* Quantile Regression에서는 대부분의 이벤트에서 주식시장과의 동조화가 관찰되었다.
* GARCH 분석에서는 지정학 리스크보다 시장심리 변수의 설명력이 더 높게 나타났다.
* 따라서 BTC는 전통적 의미의 Safe Haven보다는 조건부·제한적 Weak Haven에 가까운 특성을 보이는 것으로 해석된다.

---

## 6. 실행 방법 (Run Dashboard)

### Local

```bash
streamlit run Dashboard/app.py
```

### Streamlit Cloud

GitHub Repository를 Streamlit Cloud에 연결하여 배포할 수 있다.

---

## 7. Repository Structure

```text
Dashboard/
DataPipeline/
EDA/
EventStudy/
FIGURES/
GARCH/
Quantile/
screenshots/
validation/
```
