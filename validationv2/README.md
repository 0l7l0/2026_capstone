# Validation — 검증의 검증

본분석 3종(이벤트 스터디, GARCH-X, 분위수 회귀)에 대한 학술 표준 점검과 통합 판정 결과를 모은 폴더입니다. 본분석 측이 산출한 CSV를 입력으로 받아, 학술 논문의 표준 절차에 비추어 누락된 검정이나 채점 오류가 없는지 점검하고, Baur & Lucey (2010)의 안전자산 3조건을 기계적으로 채점한 결과를 함께 제공합니다.

---

## 1. 파일 개요 (Overview)

본 폴더는 "검증의 검증"이라는 두 번째 단계를 담당합니다. 본분석에서 비트코인이 지정학적 위기에서 어떻게 움직였는지를 통계적으로 검정했다면, 본 폴더는 그 검정이 학술 논문에서 통용되는 절차를 제대로 따랐는지, 결과 해석에 누락이나 비약은 없는지를 다시 한 번 점검합니다.

점검 기준은 `catalog.json` 한 파일에 정리되어 있습니다. catalog는 7개 방법론(이벤트 스터디, GARCH-X, 분위수 회귀, BH-FDR 다중검정 보정, 플라시보 검정, Wild Bootstrap, Ljung-Box 잔차 진단)에 대해 표준 논문에서 권장하는 파라미터(`recommended_params`)와 절대 위반하면 안 되는 항목(`red_flag`)을 명시합니다. 본분석 노트북과 결과 CSV는 이 기준에 비추어 자동·수동 점검됩니다.

---

## 2. 분석 목적 (Objective)

본 폴더가 답하고자 하는 질문은 네 가지입니다.

첫째, 본분석이 학술 표준의 어디까지를 충족했는가. catalog v1.6에 정의된 33개 점검 항목을 본분석에 적용해, 통과·미통과를 정리합니다.

둘째, 자동 검증으로 잡을 수 없는 학술 해석 영역은 무엇이 남는가. 사후 변경된 파라미터의 정당화 여부, 소표본 한계, 보조 검정의 누락처럼 사람의 판단이 필요한 부분을 별도로 정리합니다.

셋째, Baur & Lucey (2010) 안전자산 정의에 따른 통합 판정 결과는 어떤가. C1(이벤트 스터디 CAR이 음이 아님), C2(분위수 회귀 베타가 양이 아님), C3(GARCH 외생변수 계수가 비유의 또는 음수)의 세 조건을 6개 이벤트별로 채점합니다.

넷째, 본분석에 적용하지 않은 강건성 검정을 추가로 적용했을 때 결론이 어떻게 달라지는가. BH-FDR 다중검정 보정, 플라시보 200회 시뮬레이션, Wild Bootstrap을 본분석 결과 위에 덧붙여 결론의 견고성을 점검합니다.

---

## 3. 사용 데이터 (Dataset)

검증의 입력은 본분석이 만든 결과 CSV들입니다. 원자료는 본분석과 동일한 `master_data.csv` (1,827 거래일, 2019-01-02 ~ 2026-04-30)와 `returns.csv` (1,843 거래일)를 사용합니다.

본분석 3종의 검증 항목은 다음과 같이 나뉩니다.

| 본분석 | 위치 | 점검 항목 수 | 자동 검증 결과 |
|---|---|---:|---|
| 이벤트 스터디 | `EventStudy/` | 11 | 11건 통과 |
| GARCH-X | `GARCH/` | 14 | 14건 통과 |
| 분위수 회귀 | `Quantile/` | 9 | 9건 통과 (라벨 매핑 정정 후) |

분석 대상 이벤트는 본분석과 동일한 6건입니다. 호르무즈 위기(2019-06-13), 솔레이마니 암살(2020-01-03), 러시아-우크라이나 전쟁(2022-02-24), 이스라엘-하마스 전쟁(2023-10-07), 이스라엘-이란 충돌(2024-04-14), 미-이스라엘-이란 전쟁(2026-02-28). COVID-19는 지정학 이벤트가 아니라는 판단으로 본분석과 마찬가지로 제외했습니다.

---

## 4. 주요 변수 설명 (Features)

본 폴더에서 가장 자주 참조되는 컬럼은 통합 판정 파일(`final_judgment.csv`)에 있습니다.

`C1_event_study_pass`는 비트코인의 누적 비정상 수익률(CAR)이 0 이상인지를 부호 기준으로 판정한 결과입니다. True는 부호 기준 통과, False는 음수로 미달을 뜻합니다. 이 컬럼은 유의성이 아니라 부호만을 보고 판정하므로, 별도로 `C1_statistical_strength` 컬럼에 통계 강도(strong/weak/inconclusive)가 함께 기록됩니다. 이 두 컬럼을 함께 읽어야 "부호는 맞지만 강도가 약한" 경우와 "부호도 맞고 강도도 강한" 경우를 구분할 수 있습니다.

`C2_quantile_reg_pass`는 SP500-BTC 분위수 회귀에서 베타 계수가 0 이하인지를, `C3_garch_pass`는 GARCH-X 모형에서 지정학 외생변수의 계수(감마)가 0 이하이거나 비유의한지를 같은 방식으로 채점합니다. 세 조건의 통과 개수를 `score`에 0부터 3까지 합산하고, 이를 바탕으로 `verdict`에 Safe Haven, Safe Haven*, Weak Haven, Diversifier, Risky Asset 중 하나가 들어갑니다.

강건성 검정 파일들은 별도의 p값 컬럼을 가집니다. `p_norm_bh`는 BH-FDR(Benjamini & Hochberg 1995)로 보정한 후의 p값이고, `placebo_p`는 무작위로 잡은 200개 가짜 이벤트의 분포에서 실제 이벤트가 차지하는 위치를 p값으로 환산한 값입니다. `wild_p`는 호르무즈 위기처럼 추정창이 짧은 이벤트에 한해 Davidson & MacKinnon (1999)의 Wild Bootstrap을 적용한 결과입니다.

---

## 5. 분석 방법론 (Methodology)

### 학술 표준의 기준이 되는 catalog.json

검증의 출발점은 `catalog.json`에 정리된 7개 방법론의 표준입니다. 각 방법론마다 핵심 인용(MacKinlay 1997, Engle 1982, Bollerslev 1986, Koenker & Bassett 1978 등), 권장 파라미터, 그리고 절대 위반하면 안 되는 항목이 함께 정의되어 있습니다. 예를 들어 이벤트 스터디는 추정창 길이, 이벤트창 길이, 정상 수익률 모델(CMRM 또는 Market Model)의 선택 근거가 점검 대상입니다. GARCH-X는 GARCH(1,1) 차수, Student-t 최대우도추정, 외생변수의 시차 처리가 점검 대상이고, 분위수 회귀는 분위수 τ 값(0.05·0.10·0.50·0.90·0.95)과 HAC Newey-West 표준오차의 사용 여부가 점검 대상입니다.

### 자동 검증 도구

`_verifier/` 폴더의 다섯 개 파이썬 스크립트가 catalog를 입력으로 받아 자동 점검을 수행합니다. `verifier.py`는 본분석 노트북을 정규식으로 파싱해 red_flag 항목 위반 여부를 PASS/WARN/FAIL로 판정합니다. `multiple_testing.py`는 본분석 결과 위에 BH-FDR 보정을 덧붙입니다. `placebo_test.py`는 200회 시뮬레이션을 돌립니다. 호르무즈 위기처럼 이벤트 이전 추정 기간이 짧은 경우(86 거래일)에는 자동으로 forward-only 모드로 전환됩니다. `wild_bootstrap.py`는 호르무즈에 한해 Davidson-MacKinnon Wild Bootstrap을 추가 적용하고, `final_judgment.py`는 위 결과들을 종합해 Baur & Lucey 3조건을 채점합니다.

### red_flag와 학술 권고의 구분

검증 결과는 두 차원으로 보고됩니다. red_flag는 catalog에 명시된 절대 금지 항목으로, `verifier.py`가 자동으로 잡습니다. 본 폴더 작성 시점 기준으로 33개 항목 전부 통과(PASS 33 / WARN 0 / FAIL 0)했습니다. 한편 사후 변경된 파라미터의 정당화 여부, 소표본 한계 명시, 보조 검정의 누락처럼 일반적으로 학술 논문에서 주의해야 하는 항목들은 자동으로 잡히지 않습니다. 이런 사항은 §6의 학술 권고 7건에 별도로 정리했습니다.

### 정정 사항 (2026-05-28 ~ 05-29)

검증 과정에서 네 가지 누락·오류가 발견되어 정정되었습니다.

첫째, Ljung-Box 잔차 진단이 본분석 노트북에 코드는 있으나 실제 실행 결과가 출력되지 않은 채로 남아 있었습니다(noteook 셀 출력이 "잔차 진단 결과 없음"). `garch_conditional_volatility.csv`와 `garch_model_params.csv`에서 평균(0.094)을 가져와 표준화 잔차에 직접 Ljung-Box를 적용한 결과를 `garch_ljung_box.csv`로 산출했습니다. 표준화 잔차는 lag 5·10·20 모두 자기상관 없음으로 통과했고, 잔차 제곱의 lag 5에서 ARCH 효과가 약하게 남았으나(p=0.005) EGARCH 모형의 비대칭 효과가 이를 흡수합니다.

둘째, `final_judgment.py`의 채점 분기 중 "음수 CAR이라도 비유의하면 C1 통과"로 처리하는 부분이 발견되어 제거했습니다. Baur & Lucey (2010)의 원래 정의는 부호 기준이며, 음수는 안전자산 증거 부족에 해당합니다. 이 정정으로 이스라엘-하마스(CAR=-0.029)와 이스라엘-이란 충돌(CAR=-0.063)이 Weak Haven에서 Diversifier로 강등됐습니다.

셋째, `us_israel_iran`이라는 영문 이벤트 키와 분위수 회귀 노트북에서 사용한 "이란 전쟁"이라는 한글 라벨이 일치하지 않아 C2 채점이 누락되던 문제가 있었습니다. 별칭 매핑을 추가해 정상 채점되도록 했습니다.

넷째, C3 채점 시 어떤 외생변수를 대상으로 할지가 모호했습니다. Bourghelle et al. (2022)이 Fear & Greed와 VIX를 통제변수로 사용한 사례를 참고해, 본 검증의 운영 정의는 "지정학 변수(GPR_custom, GPR_acts, GPR_threats)에 한해 C3 채점, F&G와 VIX는 별도 보고"로 명시했습니다.

---

## 6. 주요 결과 (Key Findings)

### 자동 검증 매트릭스

catalog v1.6의 33개 항목 점검 결과, 모든 본분석이 red_flag 위반 없이 통과했습니다. 본분석 3종을 가르면 이벤트 스터디 11/11, GARCH-X 14/14, 분위수 회귀 9/9입니다. 분위수 회귀의 9건은 위에서 언급한 라벨 매핑 정정 이후 기준이며, 정정 이전에는 미-이스라엘-이란 이벤트가 별칭 불일치로 누락되어 8/9로 보고됐습니다.

자동 검증과 별개로 학술 해석 영역에서 7건의 권고를 §6 마지막에 정리했습니다. 두 차원은 별도로 봐야 합니다. 자동 검증을 모두 통과했다고 해서 학술 권고가 자동으로 해결되는 것은 아닙니다.

### Baur & Lucey 3조건 통합 판정

| 이벤트 | C1 (CAR≥0) | C2 (β≤0) | C3 (γ≤0 또는 비유의) | 점수 | 판정 |
|---|:---:|:---:|:---:|:---:|---|
| 호르무즈 위기 | True (CAR=+0.081) | True (β=-0.012) | True | 3/3 | Safe Haven\* |
| 솔레이마니 암살 | True (CAR=+0.142) | False (β=+0.014 유의) | True | 2/3 | Weak Haven |
| 러-우 전쟁 | True (CAR=+0.113) | False (β=+0.032 유의) | True | 2/3 | Weak Haven |
| 이스라엘-하마스 | False (CAR=-0.029) | False (β=+0.013 유의) | True | 1/3 | Diversifier |
| 이스라엘-이란 충돌 | False (CAR=-0.063) | False (β=+0.024 유의) | True | 1/3 | Diversifier |
| 미-이스라엘-이란 | True (CAR=+0.132) | False (β=+0.015 유의) | True | 2/3 | Weak Haven |

6건의 분포는 Strong Safe Haven 0건, Safe Haven\* 1건(호르무즈), Weak Haven 3건(솔레이마니·러-우·미-이스라엘-이란), Diversifier 2건(이스라엘-하마스·이스라엘-이란), Risky Asset 0건입니다. 별표(\*) 표시는 부호 기준으로 3조건을 모두 통과했으나 BH-FDR 보정과 플라시보 검정에서 유의성이 확보되지 않아 통계 강도가 약함을 의미합니다. 호르무즈의 Safe Haven 판정은 분위수 회귀 결과(C2)에 주로 의존하고 있으며, 이벤트 스터디 단독으로는 강한 결론을 내리기 어렵습니다.

### C1 채점 해석 (팀원 FAQ)

본분석 회의에서 자주 나오는 세 가지 질문에 대한 정리입니다.

**`C1_event_study_pass`의 True는 무엇을 의미하는가.** True는 비트코인의 누적 비정상 수익률(CAR)이 0 이상이라는 부호 기준 통과를 의미하고, False는 음수로 미달을 의미합니다. 유의성은 별도 컬럼(`C1_statistical_strength`)에 강도(strong/weak)로 표시되며, True/False 자체는 부호만을 본다는 점이 중요합니다.

**CAR은 어떤 자산의 값인가.** 본 가설이 "비트코인이 안전자산인가"이므로, `final_judgment.csv`의 C1 컬럼은 비트코인의 CAR만을 채점 대상으로 합니다. Gold·TLT·DXY·NASDAQ의 이벤트 스터디 결과는 본분석 노트북에서 산출되어 `EventStudy/result_csv_png/event_study_results.csv`에 별도로 저장되어 있으나, 통합 판정에는 사용하지 않습니다.

**방향성이 일치하지 않고 비유의한 이벤트는 안전자산도 위험자산도 아닌 것 아닌가.** 일반적인 가설 검정 관점에서는 그 우려가 정당합니다. 다만 Baur & Lucey (2010)의 원래 정의는 부호 기준을 1순위로 두고, 유의성은 강도 정보로 활용합니다. 본 검증은 이 정의를 따라 네 가지 경우를 다음과 같이 처리합니다.

| CAR 부호 | p_BH | C1_pass | 표기 | 의미 |
|---|---|---|---|---|
| 양수 | 유의 | True | Strong | 강한 안전자산 |
| 양수 | 비유의 | True | Weak non-neg | 부호 통과, 강도 약함 (별표 표기) |
| 음수 | 비유의 | False | 비유의 음수 → 안전자산 미달 | 부호 위반, 증거 부족 |
| 음수 | 유의 | False | 유의 음수 → 위험자산 | 위험자산 |

이 처리 방식의 핵심은 네 가지로 요약할 수 있습니다. 첫째, 부호가 1순위입니다. Baur-Lucey의 원래 정의는 CAR이 0 이상인지를 본다. 둘째, 유의성은 보조 정보입니다. p값은 안전자산이냐 아니냐를 가르는 기준이 아니라, 그 통과가 얼마나 강한지(Strong인지 Weak인지)를 표시합니다. 셋째, 비유의여도 부호가 맞으면 통과로 처리하되 별표를 붙여 강도가 약하다는 사실을 따로 명시합니다. 넷째, 비유의 음수는 "위험자산"이라고 단정하지 않고 "안전자산 증거 부족"이라는 보수적 표현을 씁니다. 위험자산이라는 강한 결론은 p값이 유의하고 음수인 경우에 한정합니다.

본 분석의 6개 이벤트를 위 표에 대입하면 다음과 같이 처리됩니다.

| 이벤트 | CAR | p_BH | 케이스 | C1_pass | 종합 판정 |
|---|---|---|---|---|---|
| 호르무즈 위기 | +0.081 | 0.849 | 양수 + 비유의 | True | Safe Haven\* (강도 약함) |
| 솔레이마니 암살 | +0.142 | 0.849 | 양수 + 비유의 | True | Weak Haven |
| 러-우 전쟁 | +0.113 | 0.849 | 양수 + 비유의 | True | Weak Haven |
| **이스라엘-하마스** | **-0.029** | 0.849 | **음수 + 비유의** | **False** | **Diversifier** |
| **이스라엘-이란 충돌** | **-0.063** | 0.849 | **음수 + 비유의** | **False** | **Diversifier** |
| 미-이스라엘-이란 | +0.132 | 0.849 | 양수 + 비유의 | True | Weak Haven |

6개 이벤트는 방향성으로는 양수 4건과 음수 2건으로 갈리고, 유의성으로는 BH-FDR 보정 후 전부 비유의합니다. 이 두 차원을 부호 기준에 따라 일관되게 처리한 결과, 음수인 두 이벤트(이스라엘-하마스, 이스라엘-이란 충돌)는 부호 위반으로 C1에 미달해 Diversifier로 분류되고, 양수인 네 이벤트는 C1을 통과하나 강도가 약해 Safe Haven\* 또는 Weak Haven으로 표기됩니다.

이 채점 방식은 2026-05-29에 정정된 것입니다. 이전에는 음수 CAR이라도 비유의하면 통과 처리하던 분기가 있었으나, Baur-Lucey 정의에 위배되므로 제거했습니다. 이 정정으로 이스라엘-하마스와 이스라엘-이란 충돌이 Weak Haven에서 Diversifier로 강등되었으며, 그 결과 비트코인이 일부 위기에서 실제로 시장과 함께 하락했다는 사실이 통합 판정 결과에 직접 드러나게 되었습니다.

### 강건성 검정

BH-FDR 다중검정 보정을 30개 이벤트×자산 p값에 적용한 결과, 본분석에서 유일하게 유의했던 Gold의 이스라엘-이란 이벤트(원본 p=0.040)가 보정 후 비유의(p_BH=0.849)로 바뀝니다. 비트코인의 6개 이벤트는 모두 보정 전후 비유의로 일관됩니다.

플라시보 검정은 각 이벤트별로 무작위 200개의 가짜 이벤트일을 잡아 CAR 분포를 만들고, 실제 이벤트의 CAR이 이 분포에서 차지하는 위치를 p값으로 환산합니다. 호르무즈는 이벤트 이전 데이터가 부족해 자동으로 forward-only 모드로 전환되었으며(이벤트 이후 구간만 사용), 그 결과 p=0.28로 가짜 이벤트와 잘 구분되지 않습니다. 나머지 이벤트도 모두 p>0.05입니다.

Wild Bootstrap은 추정창이 86일로 짧은 호르무즈에 한해 적용했습니다. Stationary Bootstrap 기준 비트코인 CAR p=0.236이던 결과가 Wild Bootstrap에서는 p<0.001로 크게 달라지는데, Davidson & MacKinnon (1999)의 권고처럼 소표본에서는 이 차이가 곧 과대자신감의 신호일 수 있습니다. 즉 호르무즈의 통계적 강도는 매우 약한 것으로 보아야 합니다.

### 학술 권고 7건

자동 검증으로 잡히지 않으나 학술 논문 작성 시 반영이 필요한 사항입니다. 우선순위는 학사 발표용 즉시 수정(2건), 논문 reviewer 대응 권장(2건), 추가 보강(3건)으로 나뉩니다.

| # | 사항 | 위치 | 권고 |
|---|---|---|---|
| 1 | 이벤트창이 ±17에서 ±3으로 사후 변경됨 | EventStudy 노트북 | 단기 효과 측정 의도임을 마크다운 셀로 정당화 |
| 2 | 호르무즈 추정창이 표준 95일에서 86일로 짧음 | EventStudy 노트북 | Wild Bootstrap 보강 적용 사실 명시 |
| 3 | EGARCH AIC(9559)가 GARCH(9578)보다 낮으나 부록 처리됨 | GARCH 노트북 | 본문에 통합하거나 결론에 명시 |
| 4 | 분위수 회귀 BH family 정의가 사전 등록 안 됨 | Quantile 노트북 | family 정의를 마크다운 셀로 명시 |
| 5 | GARCH-X 외생성 검증 부재 | GARCH 노트북 | Granger 인과·Hausman 검정 추가 (논문화 시) |
| 6 | ADF 검정에 구조변화 미반영 | GARCH 노트북 | Zivot-Andrews 검정 추가 (논문화 시) |
| 7 | 분위수 회귀 호르무즈 표본 부족 | Quantile 노트북 | 표본 수(n=9) 명시 + 해석 보류 |

Ljung-Box 미실시는 정정 사항에서 다룬 대로 2026-05-28 본 폴더에서 실제 실행 완료되어 권고 목록에서 제외되었습니다.

### 최종 결론

검증 결과를 종합하면, 비트코인은 본 분석 기간(2019~2026) 6개 지정학 이벤트에서 **강한 의미의 안전자산으로 기능하지 않았습니다**. 부호 기준으로 모든 조건을 통과한 이벤트는 호르무즈 위기 한 건이며, 그마저도 통계 강도가 약합니다. 이스라엘-하마스와 이스라엘-이란 충돌에서는 비트코인이 시장과 함께 하락해 음수 CAR을 기록했고, 이는 안전자산 가설의 핵심 예측과 반대됩니다.

흥미로운 부수 발견은 분위수 회귀에서 드러납니다. 극단적 시장 하락(τ=0.01)에서 비트코인-SP500 동조화 계수가 평상시(τ=0.50)의 약 2.2배로 증가하며, 지정학 리스크가 높아질수록 이 동조화가 더 강해지는 상호작용(δ=+0.005, p=0.037)이 관찰됩니다. 즉 위기일수록 비트코인은 시장으로부터 분리되는 것이 아니라 오히려 시장에 끌려갑니다. 한편 GARCH-X 결과에서는 지정학 변수 자체(GPR γ)는 비트코인 변동성에 유의한 영향을 주지 않으며(p=0.58~0.96), 변동성을 설명하는 것은 Fear & Greed 같은 시장 심리 변수(γ=+0.157, p=0.038)입니다. 본 통합 판정의 C3에서는 이 부분이 운영 정의상 채점에 포함되지 않으나, 해석에는 함께 고려할 만한 사실입니다.

---

## 7. 결과 파일 (Output)

| 파일 | 설명 |
|---|---|
| `README.md` | 본 통합 문서 |
| `catalog.json` | 학술 표준 정의 (v1.6) — 7개 방법론별 red_flag와 권장 파라미터 |
| `final_judgment.csv` | Baur-Lucey 3조건 자동 판정 결과 (6 이벤트) |
| `final_report.md` | 학술 1장 분량 요약 (발표·논문 첫 페이지용) |
| `event_study_car_bh.csv` | 이벤트 스터디 CAR + BH-FDR 보정 후 p값 (30행: 6 이벤트 × 5 자산) |
| `event_study_placebo.csv` | 플라시보 200회 시뮬레이션 결과 (호르무즈는 forward-only) |
| `event_study_car_wild_bh.csv` | Wild Bootstrap (호르무즈 한정, ±3·±17 양 윈도우) |
| `multiple_testing_adjusted.csv` | 이벤트 스터디 + 분위수 회귀 통합 BH-FDR 156건 |
| `garch_ljung_box.csv` | GARCH 표준화 잔차의 Ljung-Box 자기상관 검정 + 잔차 제곱 ARCH 잔존 검사 |

---

## 8. 참고문헌 (References)

**안전자산 판정 기준**

Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? An Analysis of Stocks, Bonds and Gold. *Financial Review*, 45(2), 217–229.

**이벤트 스터디**

MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39.

Brown, S. J., & Warner, J. B. (1985). Using Daily Stock Returns: The Case of Event Studies. *Journal of Financial Economics*, 14(1), 3–31.

Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-Study Methodology under Conditions of Event-Induced Variance. *Journal of Financial Economics*, 30(2), 253–272.

**분위수 회귀**

Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.

Newey, W. K., & West, K. D. (1987). A Simple, Positive Semidefinite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix. *Econometrica*, 55, 703–708.

Bouri, E., Molnár, P., Azzi, G., Roubaud, D., & Hagfors, L. I. (2017). On the hedge and safe haven properties of Bitcoin: Is it really more than a diversifier? *Finance Research Letters*, 23, 87–95.

**GARCH 모형 및 잔차 진단**

Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*, 50(4), 987–1007.

Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.

Nelson, D. B. (1991). Conditional Heteroskedasticity in Asset Returns: A New Approach. *Econometrica*, 59(2), 347–370.

Han, H., & Kristensen, D. (2014). Asymptotic Theory for GARCH-X Models. *Journal of Business & Economic Statistics*, 32(3), 416–429.

Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297–303.

**다중검정 보정 및 강건성**

Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.

Politis, D. N., & Romano, J. P. (1994). The Stationary Bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313.

Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361–376.

Mammen, E. (1993). Bootstrap and Wild Bootstrap for High Dimensional Linear Models. *Annals of Statistics*, 21(1), 255–285.

**지정학 리스크 지수 및 비트코인 변동성**

Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.

Bourghelle, D., Jawadi, F., & Rozin, P. (2022). Do Collective Emotions Drive Bitcoin Volatility? A Triple Regime-Switching Vector Approach. *Finance Research Letters*, 45, 102041.
