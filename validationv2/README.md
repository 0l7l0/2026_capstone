# validation/ — 검증의 검증 산출물

> 작성: sgggg123 (검증자 역할) / 2026-05-25 작성 / **2026-05-28 정정** / catalog v1.6 / cycle_8 PASS 33 / WARN 0 / FAIL 0 (자동) + 권고 7건 (수동)

본 폴더는 fbghkdrb 본분석 3종 (이벤트 스터디 · GARCH-X · 분위수 회귀)을 학술 표준 catalog v1.6 기준으로 검증한 결과 모음입니다.

## ⚠ 2026-05-28~29 정정 사항 4건 (학술 정직성)

1. **Ljung-Box 잔차 진단 실제 실행 완료**: ✅ 표준화 잔차 3/3 lag 자기상관 없음 / 잔차² lag 5에서 ARCH 잔존 ⚠ (EGARCH가 보완)
2. **final_judgment 정의 일관성 정정 (엄격 채점 적용)**: Baur-Lucey 부호 기준 — 음수 CAR → C1 미달. 이스라엘-하마스(CAR=-0.029)·이스라엘-이란(CAR=-0.063) Weak → **Diversifier 강등**
3. **us_israel_iran 라벨 매핑**: '이란 전쟁' 별칭 추가 → C2 정상 채점
4. **C3 채점 운영 정의 명시**: 지정학 변수 한정 채점, F&G·VIX 별도 보고 — VALIDATION_REPORT §4-2 row #13

## 결과 분포 (catalog v1.6)
- Safe Haven\* 1건 (호르무즈, 통계 강도 약함)
- Weak Haven 3건
- Diversifier 2건 (이스라엘-하마스·이스라엘-이란 — 음수 CAR로 C1 미달) / Risky 0건

## 9개 파일 — 각각 무엇

| # | 파일 | 무엇 | 핵심 결과 |
|---|---|---|---|
| 1 | `VALIDATION_REPORT.md` | 검증 종합 보고서 | 본분석 3종 × catalog 7방법론 매트릭스 33행 + 수정 권고 7건 + §5-1 C1 채점 FAQ |
| 2 | `final_judgment.csv` | Baur-Lucey 3조건 자동 판정 (대시보드 통합판정용) | **Safe\* 1 / Weak 3 / Diversifier 2 (Baur-Lucey 엄격 부호 기준)** |
| 3 | `final_report.md` | 학술 1장 요약 | 발표·논문 첫 페이지 그대로 사용 가능 |
| 4 | `event_study_car_bh.csv` | 이벤트 스터디 CAR + BH-FDR 보정 (대시보드 이벤트스터디용) | 30행 (이벤트 6 × 자산 5), `p_norm_bh` 컬럼이 BH 보정 후 p값 |
| 5 | `event_study_placebo.csv` | 이벤트 스터디 Placebo 검정 (대시보드 이벤트스터디용) | 6행 (이벤트별), `placebo_p` 컬럼 200회 시뮬, 호르무즈만 forward-only |
| 6 | `event_study_car_wild_bh.csv` | Wild Bootstrap 호르무즈 보강 | Davidson & MacKinnon (1999) 소표본 robust 검정 |
| 7 | `multiple_testing_adjusted.csv` | BH-FDR 다중비교 156건 종합 | 이벤트 스터디 + 분위수 회귀 통합 |
| 8 | `garch_ljung_box.csv` | GARCH 잔차 진단 (Ljung-Box) | 표준화 잔차 3/3 lag 통과 + 잔차² lag 5 ARCH 잔존 (EGARCH 보완) |
| 9 | `README.md` | 본 폴더 안내 | - |

## 어떻게 만들었나

```
catalog.json v1.6 (학술 표준 정의)
      ↓
_verifier/ 5 스크립트 자동 실행
  ├── verifier.py          → cycle_8 PASS 33 / WARN 0 / FAIL 0 (자동) + 권고 7건 (수동) (red_flag 위반 0건. 학술 권고는 §7 별도 명시)
  ├── multiple_testing.py  → BH-FDR 보정
  ├── placebo_test.py      → Placebo 200회 (호르무즈 forward-only 자동)
  ├── wild_bootstrap.py    → Wild Bootstrap (catalog v1.6 신규)
  └── final_judgment.py    → Baur-Lucey 3조건 + C1_statistical_strength
      ↓
이 폴더의 7개 산출물 (README 포함)
```

본분석 노트북 자체는 **수정하지 않음** (마크다운 셀로 권고 4건 명시만 추가). 결과 CSV를 입력으로 받아 자동 채점·보정.

## 핵심 결론

> **비트코인은 강한 안전자산이 아니다.**
> - Strong Safe Haven: 0건
> - Safe Haven\* (강도 약함): 1건 (호르무즈 — 부호 기준 통과이나 BH·Placebo 비유의)
> - Weak Haven: 3건 (솔레이마니·러-우·미-이스라엘-이란)
> - **Diversifier: 2건** (이스라엘-하마스·이스라엘-이란 충돌 — 음수 CAR로 C1 미달)
> - Risky Asset: 0건
>
> Wild Bootstrap·Placebo·BH-FDR 3중 강건성 검정 + Baur-Lucey 엄격 부호 기준 적용으로 일부 위기에서 BTC가 시장과 함께 떨어졌다는 사실 직접 드러남.

## 인용

- MacKinlay (1997, JEL 35:13-39), Engle (1982, Econometrica 50:987-1007),
  Bollerslev (1986, J Econometrics 31:307-327), Nelson (1991, Econometrica 59:347-370),
  Koenker & Bassett (1978, Econometrica 46:33-50), Bouri (2017, FRL 23:87-95),
  Politis & Romano (1994, JASA 89:1303-1313), Davidson & MacKinnon (1999, ET 15:361-376),
  Benjamini & Hochberg (1995, JRSS B 57:289-300), Baur & Lucey (2010, FR 45:217-229),
  Caldara & Iacoviello (2022, AER 112:1194-1225)

전체 BibTeX는 `VALIDATION_REPORT.md` 부록 B 참조.

## 검증 도구 (별도)

본 폴더는 산출물만 포함. 검증 도구 자체 (`catalog.json`, `_verifier/`, `dashboard.py` 등)는 sgggg123/main 레포에 있음. 필요 시 별도 요청.
