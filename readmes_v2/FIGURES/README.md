# FIGURES — GPR 검증 시각화 카탈로그

## 1. 파일 개요 (Overview)

본 폴더는 `DataPipeline/GPR_custom_analysis.ipynb`에서 자체 지정학 리스크 지수(GPR_custom)를 생성하고 공식 GPR(Caldara & Iacoviello 2022)과 비교 검증하는 과정에서 산출된 7개의 핵심 시각화 PNG를 모은 카탈로그입니다.

GDELT GKG 원시 뉴스 데이터의 전처리 단계부터 F1~F5 후보 공식의 비교, 공식 GPR과의 상관관계 검증, 이벤트 윈도우 반응 패턴까지 시각적으로 추적할 수 있도록 구성되어 있습니다.

---

## 2. 분석 목적 (Objective)

- **GPR_custom 생성 과정의 시각적 추적**: 원시 데이터 → 전처리 → 5종 후보 공식 → 최종 채택(F3) 단계별 검증
- **공식 GPR과의 비교 검증**: 자체 지수가 학술 표준(Caldara & Iacoviello 2022)과 일관되는지 시각화
- **이벤트 반응 패턴 시각화**: 6개 지정학 이벤트 전후 ±26일 GPR 변화 확인
- **본분석 입력 데이터의 신뢰성 근거 제공**: master_data.csv의 `GPR_custom` 컬럼이 어떻게 만들어졌는지 시각적 문서화

---

## 3. 사용 데이터 (Dataset)

| 데이터 | 출처 | 비고 |
|---|---|---|
| GDELT GKG 원시 뉴스 톤·기사 수 | BigQuery | `DataPipeline/raw_data/` |
| 공식 GPR Z-score | Caldara & Iacoviello (2022) | FRED |
| GPR_custom F1~F5 | 자체 산출 | `DataPipeline/processed_data/` |

**분석 대상 이벤트 (6개)**: 호르무즈 위기, 솔레이마니 암살, 러시아-우크라이나 전쟁, 이스라엘-하마스 전쟁, 이스라엘-이란 충돌, 미-이스라엘-이란 전쟁

---

## 4. 주요 변수 설명 (Features)

| 변수 | 설명 |
|---|---|
| `tone` | 일별 평균 뉴스 톤 (음수 = 부정적, 양수 = 긍정적) |
| `article_count (N)` | 일별 지정학 관련 기사 수 |
| `F1` | 평균 톤 (단순) |
| `F2` | 기사 수 (단순) |
| `F3` | tone × log(N) — **본분석 채택** |
| `F4` | tone × √N |
| `F5` | tone × N |
| `GPR_zscore` | 공식 GPR (Caldara & Iacoviello 2022) Z-score |
| `event_date` | 이벤트 기준일 (붉은 점선으로 시각화) |

---

## 5. 분석 방법론 (Methodology)

### 시각화 도구

- `matplotlib`, `seaborn` (Python)
- 모든 PNG는 `DataPipeline/GPR_custom_analysis.ipynb` 실행으로 자동 생성

### Figure별 검증 단계

| 단계 | Figure | 목적 |
|---|---|---|
| 원시 데이터 확인 | 01 | 이벤트별 일별 기사 수 분포 |
| 전처리 검증 | 02 | 지정학 필터링·최소 기사 수 조건 적용 후 변화 |
| 후보 공식 비교 | 03, 04 | F1~F5 간 상관관계 + 변수 관계 |
| 시계열 비교 | 05, 06 | F1~F5 시계열, 공식 GPR vs 최고 상관 Custom GPR |
| 이벤트 반응 | 07 | 이벤트 전후 ±26일 GPR_custom 변화 |

---

## 6. 주요 결과 (Key Findings)

### Figure 01 — 원시 데이터 분포

`이벤트별 원시 뉴스 데이터의 일별 기사 수 분포` — 6개 이벤트마다 별도 패널. 붉은 점선이 이벤트 발생일을 표시. 이벤트 직후 기사 수 급등 패턴 일관 관찰.

### Figure 02 — 전처리 결과

`전처리 이후 tone score 분포 및 기사 수 변화` — 지정학 키워드 필터링과 최소 기사 수 조건 적용. 노이즈 제거 후 톤 분포가 안정화됨.

### Figure 03 — 상관관계 히트맵

`공식 GPR과 Custom GPR (F1~F5) 간 상관관계` — F3 (tone × log(N))이 공식 GPR과 최고 상관관계 (r ≈ 0.7+). F2 (단순 기사 수)는 가장 낮은 상관관계.

### Figure 04 — 산점도 매트릭스

`Custom GPR 및 공식 GPR 간 변수 관계` — F3와 공식 GPR의 산점도가 가장 선형. 다른 후보는 분산이 크거나 비선형.

### Figure 05 — 시계열 비교

`이벤트별 Custom GPR (F1~F5) 시계열 비교` — 0~1 범위 정규화 적용. F3이 공식 GPR과 가장 유사한 시간 패턴.

### Figure 06 — 공식 GPR vs 최고 상관 Custom GPR

`공식 GPR과 최고 상관 Custom GPR 비교` — F3 (채택 변형)과 공식 GPR의 직접 비교. 6개 이벤트 모두에서 동시 급등 관찰.

### Figure 07 — 이벤트 윈도우 반응

`이벤트 전후 ±26일 구간의 Custom GPR 변화` — 모든 이벤트에서 이벤트 직후 평균 1~2σ 급등, 약 10거래일 후 점진적 하강 패턴.

> **종합**: F3 (tone × log(N))이 공식 GPR과 가장 일관된 패턴을 보여 본분석 채택. 7개 Figure가 GPR_custom 생성 과정의 학술적 정당성을 시각적으로 문서화.

---

## 7. 결과 파일 (Output)

| 파일 | 설명 |
|---|---|
| `Figure_01_*_article_count.png` | 이벤트별 원시 일별 기사 수 분포 (붉은 점선 = 이벤트 발생일) |
| `Figure_02_*_preprocessed.png` | 전처리 후 톤 분포 + 기사 수 변화 |
| `Figure_03_correlation_heatmap.png` | 공식 GPR vs F1~F5 상관관계 히트맵 |
| `Figure_04_scatter_matrix.png` | Custom GPR + 공식 GPR 변수 관계 산점도 |
| `Figure_05_gpr_timeseries.png` | 이벤트별 Custom GPR (F1~F5) 시계열 (0~1 정규화) |
| `Figure_06_official_vs_ours.png` | 공식 GPR vs 최고 상관 Custom GPR (F3) 비교 |
| `Figure_07_event_window.png` | 이벤트 전후 ±26일 Custom GPR 변화 |

---

## 8. 참고문헌 (References)

- Caldara, D., & Iacoviello, M. (2022). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
- Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global data on events, location, and tone, 1979–2012. *ISA Annual Convention*, 2(4), 1–49.
- GDELT Project — gdeltproject.org/data.html#rawdatafiles (GKG schema documentation)
