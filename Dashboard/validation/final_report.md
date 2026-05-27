# 비트코인 안전자산 가설 최종 검증 보고

- 일자: 2026-05-26 (catalog v1.6 — Wild Bootstrap·Forward Placebo 통합)
- 데이터: `Edit_mj/GPR_custom_analysis/master_data_generated/master_data.csv` (1827행, 2019-01-02 ~ 2026-04-30)
- 검증 기준: Baur & Lucey (2010) — 위기 시 비음수 + 음의 시장 의존성 + 변동성 비증가
- 분석 3종: 이벤트 스터디(MacKinlay 1997), 분위수 회귀(Koenker & Bassett 1978), GARCH-X(Engle 1982 + Bollerslev 1986 + 외생변수)
- 보강: BH-FDR 다중비교 보정, Placebo 검정 (forward-only 자동 분기), Wild Bootstrap (Davidson & MacKinnon 1999, Rademacher), ADF 정상성 검증, multi-init MLE

## 6개 지정학 이벤트별 통합 판정

| 이벤트 | C1 이벤트스터디 | C2 분위수회귀 | C3 GARCH | 점수 | C1 강도 | 판정 |
|---|---|---|---|---:|---|---|
| 호르무즈 위기 | ✅ | ✅ | ✅ | 3/3 | weak | **Safe Haven*** |
| 솔레이마니 암살 | ✅ | ❌ | ✅ | 2/3 | weak | **Weak Haven** |
| 러-우 전쟁 | ✅ | ❌ | ✅ | 2/3 | weak | **Weak Haven** |
| 이스라엘-하마스 | ✅ | ❌ | ✅ | 2/3 | weak | **Weak Haven** |
| 이스라엘-이란 충돌 | ✅ | ❌ | ✅ | 2/3 | weak | **Weak Haven** |
| 미-이스라엘-이란 | ✅ | ❌ | ✅ | 2/3 | weak | **Weak Haven** |

> ⚠ **별표(\*)**: Safe Haven 판정이나 C1 통계 강도가 약함 (BH-FDR 비유의 + Placebo 비유의). 부호 기준 채점 통과이나 통계적 유의성은 검정 방법에 따라 분산.

## 핵심 결론

- **Safe Haven 0건 / Safe Haven* (강도 약함) 1건 / Weak Haven 5건 / Diversifier 0건 / Risky 0건**
- BH-FDR 다중비교 보정 후 이벤트 스터디에서 6이벤트 모두 BTC 비정상수익률 통계적 비유의
- 분위수 회귀 전체 합산 τ=0.05에서 SP500 β=+0.0162 (p<0.001) → 극단 하락 시 BTC는 시장과 동조 (위험자산 특성)
- 단 호르무즈 위기 단독에서는 β=-0.0116 (p=0.254 비유의) → C2 부호 기준 통과, 통계 강도 약함
- GARCH 5모델 모두 정상성·수렴 통과. 지정학 변수(GPR) γ 모두 비유의, 시장심리(F&G)만 유의 양수. EGARCH AIC 9559 < GARCH 9578 (비대칭 우월, GPR γ 결론 동일)
- Placebo 검정 (K=200, forward-only 자동): 6개 이벤트 모두 placebo p>0.05 → 실제 이벤트가 가짜 일자와 통계적으로 구분되지 않음
- Wild Bootstrap (Rademacher, 호르무즈 보강): ±3 p<0.001 / ±17 p<0.001 — 단 소표본(n=86) 과대자신감 가능. Placebo·BH와 결과 분산 → 호르무즈 Safe Haven 판정의 통계 강도 약함 (Safe Haven*)

## 인용 (자동 생성)

- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic Literature*, 35(1), 13-39.
- Koenker, R., & Bassett, G. (1978). Regression Quantiles. *Econometrica*, 46(1), 33-50.
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*, 50(4), 987-1007. (GARCH-X ARCH 원형)
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*, 31(3), 307-327. (GARCH 일반화)
- Nelson, D. B. (1991). Conditional Heteroskedasticity in Asset Returns: A New Approach. *Econometrica*, 59(2), 347-370. (EGARCH 비대칭)
- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217-229.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS B*, 57(1), 289-300.
- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361-376. (Wild Bootstrap 소표본 robust)
- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194-1225.