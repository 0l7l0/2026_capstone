# Validation — 검증의 검증 (Complete Document)

> 작성: sgggg123 (검증자) / 2026-05-25 작성 / 2026-05-31 통합본 / catalog v1.6 / cycle_8 PASS 33 / WARN 0 / FAIL 0 (자동) + 권고 7건 (수동)

---

## 1. 파일 개요 (Overview)

본 폴더 `validation/`은 sgggg123이 검증자 역할로 fbghkdrb 본분석 3종(이벤트 스터디·GARCH-X·분위수 회귀)을 `catalog v1.6` 학술 표준 기준으로 검증한 산출물 모음입니다.

`catalog.json`에 정의된 7개 방법론별 red_flag 자동 점검 + Baur & Lucey (2010) 3조건 통합 판정 + BH-FDR·Placebo·Wild Bootstrap 강건성 보강을 수행했습니다. 본 README는 검증 종합 보고서로, 이전 `VALIDATION_REPORT.md`와 폴더 안내 `README.md`를 통합한 단일 문서입니다.

---

## 2. 분석 목적 (Objective)

- **본분석 학술 표준 충족 자동 검증**: catalog v1.6의 33개 항목 PASS/WARN/FAIL 자동 판정 (verifier.py)
- **학술 권고 사항 식별**: 자동 검증이 잡지 못하는 사람 판단 영역 7건 별도 정리
- **Baur & Lucey (2010) 3조건 통합 판정**: C1(이벤트 스터디 CAR≥0) + C2(분위수회귀 β≤0) + C3(GARCH GPR γ≤0 또는 비유의)
- **강건성 보강**: BH-FDR 다중검정 보정 + Placebo 200회 시뮬 + Wild Bootstrap (호르무즈 소표본 한정)

---

## 3. 사용 데이터 (Dataset)

| 파일 | 용도 | 출처 |
|---|---|---|
| `master_data.csv` (1827행) | 통합 분석 데이터 | DataPipeline/processed_data/ |
| `returns.csv` (1843행) | 자산 수익률 | DataPipeline/processed_data/ |
| 본분석 결과 CSV 13종 | 검증 대상 | fbghkdrb 본분석 산출 |

**분석 대상 본분석 3종**

| 본분석 | 위치 | 검증 항목 수 | 자동 검증 결과 |
|---|---|:---:|:---:|
| 이벤트 스터디 | `fbghkdrb/EventStudy/` | 11 | 11/11 ✅ PASS |
| GARCH-X | `fbghkdrb/GARCH/` | 14 | 14/14 ✅ PASS |
| 분위수 회귀 | `fbghkdrb/Quantile/` | 9 (라벨 매핑 정정 후) | 9/9 ✅ PASS |
| **합계** | | **33** | **33/33 ✅ PASS** |

**분석 대상 이벤트 (6개)**: 호르무즈 위기, 솔레이마니 암살, 러시아-우크라이나, 이스라엘-하마스, 이스라엘-이란, 미-이스라엘-이란

---

## 4. 주요 변수 설명 (Features)

### 4-1. final_judgment.csv 컬럼

| 컬럼 | 설명 |
|---|---|
| `event_name` | 이벤트 키 (영문, 6개) |
| `event_label` | 이벤트 라벨 (한글) |
| `C1_event_study_pass` | **True/False** — BTC의 CAR ≥ 0 (부호 기준 통과 여부) |
| `C1_detail` | 채점 상세: `Strong` / `Weak non-neg` / `비유의 음수 → 안전자산 미달` / `유의 음수 → 위험자산` |
| `C1_statistical_strength` | `strong` / `weak` / `inconclusive` (통계 강도 표시) |
| `C2_quantile_reg_pass` | True/False — β_SP500 ≤ 0 (분위수 회귀 부호 기준) |
| `C2_detail` | β값 + p_BH + 채점 사유 |
| `C3_garch_pass` | True/False — GPR γ ≤ 0 또는 비유의 (변동성 비연동) |
| `C3_detail` | γ 검정 요약 |
| `score` | 0~3 (C1 + C2 + C3 합산) |
| `verdict` | `Safe Haven` / `Safe Haven*` / `Weak Haven` / `Diversifier` / `Risky Asset` |

### 4-2. 강건성 검정 컬럼 (event_study_car_bh.csv, placebo.csv, wild_bh.csv)

| 컬럼 | 설명 |
|---|---|
| `p_norm`, `p_boot` | 정규 근사·Stationary Bootstrap p값 |
| `p_norm_bh` | **BH-FDR 보정 후 p값** (Benjamini & Hochberg 1995) |
| `sig_bh` | BH 보정 후 유의 여부 (α=0.05) |
| `placebo_p` | **Placebo 200회 시뮬 p값** (호르무즈만 forward-only 자동) |
| `placebo_mode` | `bidirectional` / `forward_only` (호르무즈 데이터 한계 처리) |
| `wild_p` | **Wild Bootstrap p값** (Davidson & MacKinnon 1999, 호르무즈 한정) |

---

## 5. 분석 방법론 (Methodology)

### 5-1. catalog v1.6 학술 표준 (검증 기준)

`catalog.json`에 7개 방법론별 `red_flag` (절대 금지)와 `recommended_params` (권장 파라미터)를 정의:

| 방법론 | 핵심 인용 | 검증 항목 |
|---|---|---|
| Event Study | MacKinlay (1997) | 추정창, 이벤트창, BMP 검정, CMRM/Market Model |
| GARCH-X | Engle (1982) + Bollerslev (1986) + Han·Kristensen (2014) | GARCH(1,1), Student-t MLE, 외생변수 |
| 분위수 회귀 | Koenker & Bassett (1978), Bouri (2017) | τ=0.05/0.10, HAC Newey-West SE |
| BH-FDR | Benjamini & Hochberg (1995) | family 사전 정의, α=0.05 |
| Placebo | MacKinlay (1997) §6 | K=200, forward-only 자동 (소표본 시) |
| Wild Bootstrap | Davidson & MacKinnon (1999), Mammen (1993) | Rademacher 가중치, 소표본 robust |
| Ljung-Box | Ljung & Box (1978) | lag 5·10·20, 잔차² ARCH 잔존 |

### 5-2. _verifier/ 자동 검증 5 스크립트

```
catalog.json v1.6 (학술 표준 정의)
      ↓
_verifier/ 5 스크립트 자동 실행
  ├── verifier.py          → red_flag 자동 점검 (PASS/WARN/FAIL)
  ├── multiple_testing.py  → BH-FDR 보정
  ├── placebo_test.py      → Placebo 200회 (호르무즈 forward-only 자동)
  ├── wild_bootstrap.py    → Wild Bootstrap (catalog v1.6 신규)
  └── final_judgment.py    → Baur-Lucey 3조건 + C1_statistical_strength
      ↓
이 폴더의 10개 산출물 (catalog.json·README 포함)
```

본분석 노트북 자체는 **수정하지 않음** (마크다운 셀로 권고 명시만 추가). 결과 CSV를 입력으로 받아 자동 채점·보정.

### 5-3. red_flag vs 학술 권고 (두 차원)

| 차원 | 의미 | 검증 방식 | 결과 |
|---|---|---|---|
| **🟦 red_flag** | catalog 명시 절대 금지 항목 (실제로 학술적으로 잘못된 것) | `verifier.py` 자동 정규식 점검 | **PASS 33 / WARN 0 / FAIL 0** |
| **🟥 학술 권고** | 일반적 주의사항 (사람이 판단해야 하는 영역) | 수동 정리 (§6-5) | **권고 7건** (즉시 2 / 권장 2 / 선택 3) |

→ 두 차원 별도. 자동 검증 통과해도 학술 권고는 별도로 본분석 측 반영 필요.

### 5-4. 정정 사항 (2026-05-28~29 적용 완료)

| # | 정정 내용 | 영향 |
|---|---|---|
| 1 | **Ljung-Box 잔차 진단 실제 실행** | 표준화 잔차 3/3 lag 자기상관 없음 ✅ / 잔차² lag 5 ARCH 잔존 ⚠ (EGARCH 보완) |
| 2 | **final_judgment 엄격 채점 (Baur-Lucey 부호 기준)** | 음수 CAR → C1 미달. 이스라엘-하마스·이스라엘-이란 Weak → **Diversifier 강등** |
| 3 | **us_israel_iran 라벨 별칭 매핑** | '이란 전쟁' 별칭 추가 → C2 정상 채점 |
| 4 | **C3 채점 운영 정의 명시** | 지정학 변수 한정 채점, F&G·VIX 별도 보고 |

---

## 6. 주요 결과 (Key Findings)

### 6-1. 자동 검증 매트릭스 합계

```
PASS  33 / 33  (red_flag 위반 0건)
WARN   0
FAIL   0
권고   7건 (수동, 학술 해석 영역)
```

### 6-2. Baur & Lucey (2010) 3조건 통합 판정

| 이벤트 | C1 (CAR≥0) | C2 (β≤0) | C3 (γ≤0 or 비유의) | 점수 | 판정 |
|---|:---:|:---:|:---:|:---:|---|
| 호르무즈 위기 | ✅ (CAR=+0.081) | ✅ (β=-0.012) | ✅ | 3/3 | **Safe Haven\*** (강도 약함) |
| 솔레이마니 암살 | ✅ (CAR=+0.142) | ❌ (β=+0.014 유의) | ✅ | 2/3 | Weak Haven |
| 러-우 전쟁 | ✅ (CAR=+0.113) | ❌ (β=+0.032 유의) | ✅ | 2/3 | Weak Haven |
| **이스라엘-하마스** | ❌ **(CAR=-0.029 음수)** | ❌ (β=+0.013 유의) | ✅ | **1/3** | **Diversifier** |
| **이스라엘-이란 충돌** | ❌ **(CAR=-0.063 음수)** | ❌ (β=+0.024 유의) | ✅ | **1/3** | **Diversifier** |
| 미-이스라엘-이란 | ✅ (CAR=+0.132) | ❌ (β=+0.015 유의) | ✅ | 2/3 | Weak Haven |

**최종 분포 (catalog v1.6 — 2026-05-29 엄격 채점 적용)**

- **Safe Haven (3/3 강도 강함)**: 0건
- **Safe Haven\* (3/3 강도 약함)**: 1건 (호르무즈 — `C1_statistical_strength=weak`)
- **Weak Haven (2/3 통과)**: **3건** (솔레이마니·러-우·미-이스라엘-이란)
- **Diversifier (1/3 통과)**: **2건** (이스라엘-하마스·이스라엘-이란 — 음수 CAR로 C1 미달)
- **Risky Asset**: 0건

> ⚠ **별표(\*)** 의미: Baur-Lucey 부호 기준 (CAR≥0, β≤0) 통과이나, BH-FDR 보정 후 비유의 + Placebo 비유의 → 통계 강도 약함. `_verifier/final_judgment.py`가 `C1_statistical_strength` 컬럼 자동 산출.

### 6-3. C1 채점 해석 (팀원 FAQ)

#### Q1. `C1_event_study_pass`의 True가 뭘 의미하나요?

| 값 | 의미 |
|---|---|
| **True** | C1 조건 통과 = BTC의 CAR ≥ 0 (부호 기준 통과) |
| **False** | C1 조건 미달 = BTC의 CAR < 0 (음수 → 안전자산 증거 부족) |

→ True/False는 **"부호 기준 통과 여부"**만 표시. 유의성(p값)은 별도로 `C1_statistical_strength` 컬럼에 강도(Strong/Weak)로 표시됨.

#### Q2. CAR은 BTC의 값인가요?

**예, BTC의 CAR만 채점 대상입니다.**

- 본 가설: "BTC가 안전자산인가?"
- 따라서 `final_judgment.csv`의 C1 컬럼은 BTC의 CAR만 채점
- Gold·TLT·DXY 등 다른 자산의 이벤트 스터디 결과는 `EventStudy/result_csv_png/event_study_results.csv`에 별도 보관 (종합 판정 X)

#### Q3. 이벤트별로 방향성이 일치하지 않고 비유의한데 안전·위험 어떻게 처리했나요?

**Baur & Lucey (2010) 부호 기준 채점**: 유의성이 아니라 부호로 1차 판정, 유의성은 강도(strength) 정보로 사용.

**4가지 케이스 처리 표**

| CAR 부호 | p_BH (유의성) | C1_pass | C1_detail 표기 | 의미 |
|---|---|---|---|---|
| ≥ 0 | < 0.05 (유의) | **True** | `Strong` | 진짜 안전자산 (강도 강함) |
| ≥ 0 | ≥ 0.05 (비유의) | **True** | `Weak non-neg` | C1 통과, 통계 강도 약함 → 별표(\*) 표기 |
| < 0 | ≥ 0.05 (비유의) | **False** | `비유의 음수 → 안전자산 미달` | 부호 위반, 안전자산 증거 부족 |
| < 0 | < 0.05 (유의) | **False** | `유의 음수 → 위험자산` | 유의한 음수, Risky Asset |

**핵심 원칙**
1. **부호가 1순위**: Baur-Lucey 원래 정의는 CAR ≥ 0 부호 기준
2. **유의성은 강도 정보**: p값은 안전자산 "판정"이 아니라 "강도"를 표시 (Strong vs Weak)
3. **비유의여도 판정 가능**: 비유의여도 양수면 C1 통과 (별표\*로 강도 약함 명시), 비유의여도 음수면 C1 미달
4. **단정 회피**: "안전자산 증거 부족"이 정확한 표현 — "위험자산"이라 단정하지 않음

**우리 결과 적용 예시**

| 이벤트 | CAR | p_BH | 케이스 | C1_pass | 종합 판정 |
|---|---|---|---|---|---|
| 호르무즈 위기 | +0.081 | 0.849 | 양수 + 비유의 | **True** | Safe Haven\* (강도 약함) |
| 솔레이마니 암살 | +0.142 | 0.849 | 양수 + 비유의 | **True** | Weak Haven |
| 러-우 전쟁 | +0.113 | 0.849 | 양수 + 비유의 | **True** | Weak Haven |
| **이스라엘-하마스** | **-0.029** | 0.849 | **음수 + 비유의** | **False** | **Diversifier** |
| **이스라엘-이란 충돌** | **-0.063** | 0.849 | **음수 + 비유의** | **False** | **Diversifier** |
| 미-이스라엘-이란 | +0.132 | 0.849 | 양수 + 비유의 | **True** | Weak Haven |

→ 방향성 불일치(양수 4건 + 음수 2건)와 전 이벤트 비유의를 부호 기준으로 일관 처리.
→ 음수 2건(이스라엘-하마스·이스라엘-이란)은 부호 위반으로 C1 미달 → Diversifier 강등.
→ 양수 4건은 C1 통과하나 비유의라 강도 약함 — Safe Haven\* / Weak Haven 표기.

> **2026-05-29 정정 이력**: 이전 final_judgment 로직이 "음수 CAR도 비유의면 C1 통과"로 처리하던 분기를 제거. Baur-Lucey 부호 기준에 일관 적용.

### 6-4. 강건성 검정 (BH-FDR / Placebo / Wild Bootstrap)

- **BH-FDR 보정** (30 p값 family): 전 30건 비유의. Gold Israel-Iran 원본 p=0.040 → p_BH=0.849
- **Placebo (K=200)**: 6 이벤트 모두 placebo p > 0.05. 호르무즈만 forward-only (추정창 86일 데이터 한계)
- **Wild Bootstrap (호르무즈 한정)**: BTC CAR p<0.001 (양 윈도우). Stationary Bootstrap p=0.236과 큰 차이 — 소표본 과대자신감 가능성

### 6-5. 학술 권고 7건 (수동 정리, 본분석 측에 전달)

| # | 문제 | 본분석 위치 | 수정 방향 | 우선순위 |
|---|---|---|---|:---:|
| 1 | 이벤트창 ±17 → ±3 사후 변경 | EventStudy 노트북 | 정당화 마크다운 셀 삽입 | 🔴 즉시 |
| 2 | 호르무즈 추정창 86일 (표준 95일 -9일) | EventStudy 노트북 | "Wild Bootstrap 보강 적용" 명시 | 🔴 즉시 |
| 3 | EGARCH AIC 9559 < GARCH 9578이나 부록 | GARCH 셀 종합 결론 | 본문 통합 또는 명시 | 🟡 권장 |
| 4 | 분위수 회귀 BH family 정의 사전 등록 | Quantile BH 보정 셀 | 마크다운 셀 추가 | 🟡 권장 |
| 5 | GARCH-X 외생성 검증 부재 | GARCH 신규 부록 | Granger·Hausman 추가 | 🟢 선택 |
| 6 | ADF 구조변화 미반영 | GARCH 부록 | Zivot-Andrews 검정 추가 | 🟢 선택 |
| 7 | 분위수 회귀 호르무즈 표본 부족 | Quantile ⚠ 표시 셀 | 표본 수 명시 + 해석 보류 | 🟢 선택 |

→ Ljung-Box 미실시(이전 권고 #8)는 2026-05-28 사용자 측 실제 실행 완료 ✅

### 6-6. 가설 검증 최종 결론

> **비트코인은 강한 안전자산(Strong Safe Haven)이 아니다.** 6 지정학 이벤트 중 Strong Safe Haven 0건, Safe Haven\* 1건(호르무즈, 강도 약함), Weak Haven 3건, **Diversifier 2건**(이스라엘-하마스·이스라엘-이란 — 음수 CAR로 C1 미달), Risky Asset 0건. Wild Bootstrap·Placebo·BH-FDR 3중 검정 + Baur-Lucey 엄격 부호 기준 정정으로 **일부 위기에서 BTC가 시장과 함께 떨어졌다는 사실 직접 드러남**.

**핵심 발견**
- **위기 시 동조화 강화**: SP500-BTC 동조화가 극단 하락(τ=0.01)에서 평상시(τ=0.50) 대비 2.2배 증가
- **GPR 상승이 동조화를 강화**: 상호작용항 δ=+0.005 (p=0.037), Safe Haven 조건과 정반대
- **GPR은 변동성에 유의하지 않음**: GARCH·EGARCH 전 모델에서 GPR γ 비유의 (p=0.58~0.96)
- **시장 심리(Fear&Greed)가 BTC 변동성 설명**: fear_greed_lag1 γ=+0.157 (p=0.038)
- **Ljung-Box 잔차 진단**: 표준화 잔차 3/3 lag 통과 / 잔차² lag 5에서 ARCH 잔존 (EGARCH가 보완)

---

## 7. 결과 파일 (Output)

| # | 파일 | 유형 | 무엇 | 핵심 결과 |
|---|---|---|---|---|
| 1 | `README.md` | MD | 본 통합 문서 (Complete Document) | 검증 종합 보고서 |
| 2 | `catalog.json` | JSON | 학술 표준 정의 v1.6 (검증 도구) | 7개 방법론 red_flag·recommended_params |
| 3 | `final_judgment.csv` | CSV | Baur-Lucey 3조건 자동 판정 (대시보드 통합판정용) | **Safe\* 1 / Weak 3 / Diversifier 2** |
| 4 | `final_report.md` | MD | 학술 1장 요약 | 발표·논문 첫 페이지 사용 가능 |
| 5 | `event_study_car_bh.csv` | CSV | 이벤트 스터디 CAR + BH-FDR 보정 (대시보드용) | 30행 (이벤트 6 × 자산 5), `p_norm_bh` 컬럼 |
| 6 | `event_study_placebo.csv` | CSV | 이벤트 스터디 Placebo 검정 (대시보드용) | 6행, `placebo_p` 컬럼 200회 시뮬 |
| 7 | `event_study_car_wild_bh.csv` | CSV | Wild Bootstrap 호르무즈 보강 | Davidson & MacKinnon (1999) |
| 8 | `multiple_testing_adjusted.csv` | CSV | BH-FDR 다중비교 156건 종합 | 이벤트 스터디 + 분위수 회귀 통합 |
| 9 | `garch_ljung_box.csv` | CSV | GARCH 잔차 진단 (Ljung-Box) | 표준화 잔차 3/3 lag 통과 + 잔차² lag 5 ARCH 잔존 |

---

## 8. 참고문헌 (References)

**안전자산 판정 기준**
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229.

**이벤트 스터디**
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13–39.
- Brown, S. J., & Warner, J. B. (1985). Using Daily Stock Returns: The Case of Event Studies. *Journal of Financial Economics*, 14(1), 3–31.
- Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-Study Methodology under Conditions of Event-Induced Variance. *Journal of Financial Economics*, 30(2), 253–272.

**분위수 회귀**
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33–50.
- Newey, W. K., & West, K. D. (1987). A Simple, Positive Semidefinite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix. *Econometrica*, 55, 703–708.
- Bouri, E. et al. (2017). On the hedge and safe haven properties of Bitcoin. *Finance Research Letters*, 23, 87–95.

**GARCH 모형**
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*, 50(4), 987–1007.
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.
- Nelson, D. B. (1991). Conditional Heteroskedasticity in Asset Returns: A New Approach. *Econometrica*, 59(2), 347–370.
- Han, H., & Kristensen, D. (2014). Asymptotic Theory for GARCH-X Models. *Journal of Business & Economic Statistics*, 32(3), 416–429.
- Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297–303.

**강건성·다중검정**
- Politis, D. N., & Romano, J. P. (1994). The Stationary Bootstrap. *JASA*, 89(428), 1303–1313.
- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361–376.
- Mammen, E. (1993). Bootstrap and wild bootstrap for high dimensional linear models. *Annals of Statistics*, 21(1), 255–285.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.

**지정학 리스크 지수**
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.

---

**작성 완료**: 2026-05-25 / **통합본 정정** 2026-05-31 / sgggg123 / cycle_8 PASS 33 / WARN 0 / FAIL 0 (자동) + 학술 권고 7건 (수동) + 정정 4건 적용
