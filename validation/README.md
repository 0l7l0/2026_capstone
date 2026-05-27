# validation/ — 검증의 검증 산출물

> 작성: sgggg123 (검증자 역할) / catalog v1.6 / cycle_8 PASS 33/0/0

본 폴더는 fbghkdrb 본분석 3종 (이벤트 스터디 · GARCH-X · 분위수 회귀)을 학술 표준 catalog v1.6 기준으로 검증한 결과 모음입니다.

## 5개 파일 — 각각 무엇

| # | 파일 | 무엇 | 핵심 결과 |
|---|---|---|---|
| 1 | `VALIDATION_REPORT.md` | 검증 종합 보고서 (345줄) | 본분석 3종 × catalog 7방법론 매트릭스 33행 + 수정 권고 7건 |
| 2 | `final_judgment.csv` | Baur-Lucey 3조건 자동 판정 | Strong Safe 0 / Safe Haven\* (강도 약함) 1 / Weak 5 |
| 3 | `final_report.md` | 학술 1장 요약 | 발표·논문 첫 페이지 그대로 사용 가능 |
| 4 | `event_study_car_wild_bh.csv` | Wild Bootstrap 호르무즈 보강 | Davidson & MacKinnon (1999) 소표본 robust 검정 |
| 5 | `multiple_testing_adjusted.csv` | BH-FDR 다중비교 156건 종합 | 이벤트 스터디 + 분위수 회귀 통합 |

## 어떻게 만들었나

```
catalog.json v1.6 (학술 표준 정의)
      ↓
_verifier/ 5 스크립트 자동 실행
  ├── verifier.py          → cycle_8 PASS 33/0/0
  ├── multiple_testing.py  → BH-FDR 보정
  ├── placebo_test.py      → Placebo 200회 (호르무즈 forward-only 자동)
  ├── wild_bootstrap.py    → Wild Bootstrap (catalog v1.6 신규)
  └── final_judgment.py    → Baur-Lucey 3조건 + C1_statistical_strength
      ↓
이 폴더의 5개 산출물
```

결과 CSV를 입력으로 받아 자동 채점·보정.

## 핵심 결론

> **비트코인은 강한 안전자산이 아니다.**
> - Strong Safe Haven: 0건
> - Safe Haven\* (강도 약함): 1건 (호르무즈 — 부호 기준 통과이나 BH·Placebo 비유의)
> - Weak Haven: 5건
>
> Wild Bootstrap·Placebo·BH-FDR 3중 강건성 검정으로 호르무즈 판정의 한계를 직접 명시.

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
