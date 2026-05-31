# \_verifier — 검증 도구 5종

`validationv2/` 폴더의 산출물을 자동 생성하는 검증 도구 모음입니다. `catalog.json`(학술 표준 정의)을 기준으로 본분석 결과를 점검·보정·통합 판정합니다.

---

## 1. 스크립트 5종

| 파일 | 역할 | 입력 | 출력 |
|---|---|---|---|
| `verifier.py` | catalog v1.6 red_flag 자동 점검 (PASS/WARN/FAIL) | 본분석 노트북 + 결과 CSV | `.claude/verification_reports/cycle_N.md` |
| `multiple_testing.py` | BH-FDR 다중검정 보정 | `event_study_car.csv`, `quantile_results.csv` | `multiple_testing_adjusted.csv` |
| `placebo_test.py` | Placebo 200회 시뮬레이션 (호르무즈 forward-only 자동) | `master_data.csv`, `returns.csv` | `event_study_placebo.csv` |
| `wild_bootstrap.py` | Wild Bootstrap (호르무즈 소표본 보강, Davidson & MacKinnon 1999) | 추정창 데이터 | `event_study_car_wild_bh.csv` |
| `final_judgment.py` | Baur & Lucey (2010) 3조건 자동 채점 + `C1_statistical_strength` | 위 4개 산출 CSV | `final_judgment.csv`, `final_report.md` |

---

## 2. 의존 데이터 경로 (중요)

각 스크립트는 다음 경로에서 입력을 읽습니다:

```python
RESULTS = ROOT / 'Edit_mj' / 'results'   # 본분석 결과 CSV 모음
MASTER  = ROOT / 'Edit_mj' / 'GPR_custom_analysis' / 'master_data_generated' / 'master_data.csv'
```

→ 본진 구조(`Dashboard/result_csv_png/`, `EventStudy/result_csv_png/`, `GARCH/result_csv_png/`, `Quantile/result_csv_png/`)에서 돌리려면 두 가지 방법:

### 방법 A: 본진에서 그대로 사용 — 환경변수 또는 심볼릭 링크
```bash
# 본진 루트에서 Edit_mj 디렉토리를 가상으로 만들어 본진 result_csv_png들을 모아 둠
mkdir -p Edit_mj/results
cp DataPipeline/processed_data/master_data.csv Edit_mj/GPR_custom_analysis/master_data_generated/
cp EventStudy/result_csv_png/*.csv Edit_mj/results/
cp GARCH/result_csv_png/*.csv Edit_mj/results/
cp Quantile/result_csv_png/*.csv Edit_mj/results/
```

### 방법 B: 스크립트 상단의 `RESULTS = ` 라인을 본진 구조로 수정
```python
# 예시 (final_judgment.py L19)
RESULTS = ROOT / 'GARCH' / 'result_csv_png'   # 또는 본진 구조에 맞게
```

→ 본 폴더의 코드는 사용자(sgggg123) 로컬 환경 기준입니다. 본진에서 재실행 시 위 두 방법 중 하나 적용.

---

## 3. 실행 순서

검증 산출물을 처음부터 다시 만들고 싶다면:

```bash
# 1. 자동 검증 (catalog red_flag 점검)
python3 _verifier/verifier.py

# 2. 다중검정 보정
python3 _verifier/multiple_testing.py

# 3. Placebo 검정 (시간 소요: 약 2분, K=200)
python3 _verifier/placebo_test.py

# 4. Wild Bootstrap (호르무즈 한정)
python3 _verifier/wild_bootstrap.py

# 5. Baur & Lucey 3조건 통합 판정 (위 4개 결과 모두 필요)
python3 _verifier/final_judgment.py
```

→ 최종 결과는 `Edit_mj/results/final_judgment.csv`에 저장되며, `validationv2/final_judgment.csv`와 동일.

---

## 4. 핵심 결정 사항 (2026-05-31 기준)

`final_judgment.py`의 주요 결정 사항이 검증 결과에 직접 영향을 줍니다.

### C1 채점 — Baur & Lucey 부호 기준

```python
# L62-72: CAR ≥ 0이면 통과(True), 음수면 미달(False)
# 유의성은 별도 C1_statistical_strength 컬럼에 strong/weak/inconclusive로 표시
if car >= 0 and p_bh < ALPHA:
    c1_pass = True; c1_strength = 'strong'   # Strong Safe Haven
elif car >= 0:
    c1_pass = True; c1_strength = 'weak'     # Pass (Weak*) → 별표 표기
else:
    c1_pass = False
    c1_strength = 'inconclusive' if p_bh >= ALPHA else 'strong'  # Fail (inconclusive/Risky)
```

### C3 채점 — `garch_model_params.csv`를 source of truth로 사용 (2026-05-31)

```python
# L48-58: garch_gamma_results.csv (가공본) → garch_model_params.csv (직접 산출본)으로 변경
gmp = safe_read('garch_model_params.csv')
gamma_rows = gmp[gmp['param'].astype(str).str.startswith('gamma(')].copy()
gamma_rows['variable'] = gamma_rows['param'].astype(str).str.extract(r'gamma\(([^)]+)\)')
gamma_rows['gamma'] = gamma_rows['estimate'].astype(float)
ggp = gamma_rows[['model', 'model_label', 'variable', 'gamma', 'p_value']]
```

### C3 detail — min p / max p 둘 다 표시 (버그 수정 2026-05-31)

```python
# L160-165: 기존 라벨은 "max p"였으나 .min() 호출 버그 → 둘 다 명시
pmin = gpr_rows["p_value"].astype(float).min()
pmax = gpr_rows["p_value"].astype(float).max()
c3_detail = f'GPR γ 모두 비유의 (n={len(gpr_rows)}, min p={pmin:.3f}, max p={pmax:.3f})'
```

---

## 5. 인용

- Baur, D. G., & Lucey, B. M. (2010). Is Gold a Hedge or a Safe Haven? *Financial Review*, 45(2), 217–229. (3조건 통합 판정)
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery Rate. *JRSS B*, 57(1), 289–300. (BH-FDR)
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *JEL*, 35(1), 13–39. (Placebo 검정)
- Davidson, R., & MacKinnon, J. G. (1999). The size distortion of bootstrap tests. *Econometric Theory*, 15(3), 361–376. (Wild Bootstrap)
- Engle, R. F. (1982); Bollerslev, T. (1986); Han & Kristensen (2014). (GARCH-X C3 채점)

전체 학술 표준 정의는 `validationv2/catalog.json` (v1.6) 참조.

---

**작성**: sgggg123 (검증자) / 2026-05-31
