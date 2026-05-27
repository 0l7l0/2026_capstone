수정된 dashboard_ui.py의 변경 필요 부분 
1) eda장에서 글자수 겹치는 부분 수정 필요(png). 
2) 이벤트스터디에서 강건성.csv 호르무즈 값 누락. 
3) 분위수 회귀 파트는 코드 돌려보면서 png 다시 다운로드 받고, 추가로 시각화 개선 필요해서, 분위수 코드 재작업 후에 수정 예정. 
4) 내일 위 작성된 파트 수정 후 GARCH까지 마무리 예정 / 원 데이터 탐색란에서 삭제. 
5) 시각화 개선만 한거라서 작성된 내용들 팩트 파악 필요. 
 
## 2. 현재 가장 부족한 영역

현재 부족한 영역은 대부분:

```text
금융시장 반응 시각화
```

이다.

특히:

- Safe-Haven 여부
- BTC vs Gold 비교
- 시장 반응 흐름
- 변동성 비교

를 직관적으로 보여주는 Figure가 부족하다.

---

# 3. 추가 생성 추천 자료 (High Priority)

## 3-1. BTC vs Gold Cumulative Return

### 목적

Main Hero Visualization

### 필요 이유

현재 대시보드는:

- Heatmap
- Scatter
- Correlation

중심이므로,

```text
“BTC가 실제로 Gold처럼 움직였는가?”
```

를 직관적으로 보여주는 대표 Figure가 부족하다.

---

### 추천 파일명

```text
FIGURES/main_btc_gold_compare.png
```

---

### 추천 구성

- BTC cumulative return
- Gold cumulative return
- Event vertical line
- Event annotation

---

## 3-2. CAR Comparison Figure

### 목적

Event Study 결과 시각화

### 현재 문제

현재 Event Study는:

```text
table 중심
```

이라 대시보드 느낌이 약하다.

---

### 추천 파일명

```text
event_study/result_csv_png/car_comparison.png
```

---

### 추천 구성

- Event별 CAR
- BTC vs Gold vs SP500 비교
- Barplot 형태

---

## 3-3. Rolling Correlation

### 목적

BTC-SP500 동조화 시각화

### 추천 파일명

```text
eda/result_csv_png/rolling_corr.png
```

---

### 추천 구성

- BTC-SP500 rolling correlation
- BTC-Gold rolling correlation
- 이벤트 vertical line

---

## 3-4. Event Price Flow

### 목적

이벤트 전후 시장 흐름 설명

### 추천 파일명

```text
eda/result_csv_png/event_price_flow.png
```

---

### 추천 구성

- Event window cumulative return
- BTC / Gold / SP500 비교

---

## 3-5. Tail Dependence Heatmap

### 목적

Quantile Regression 결과 시각화

### 추천 파일명

```text
quantile/result_csv_png/quantreg_heatmap.png
```

---

### 추천 구성

- 분위수별 β 값 heatmap
- 자산별 비교

---

## 3-6. Gamma Coefficient Comparison

### 목적

GARCH-X 외생변수 영향 비교

### 추천 파일명

```text
garch/result_csv_png/garch_gamma_coefficients.png
```

---

### 추천 구성

- GPR
- VIX
- Fear & Greed

γ coefficient barplot

---

# 4. 추가 추천 CSV

## 4-1. Model Comparison Summary

### 목적

교수님 선호형 Research Dashboard 강화

---

### 추천 파일명

```text
garch/result_csv_png/model_comparison_summary.csv
```

---

### 추천 컬럼

| Model | AIC | BIC | LogLik | Significant Variables |
|---|---|---|---|---|

---

## 4-2. Safe Haven Verdict Summary

### 목적

최종 결과 요약 카드

---

### 추천 파일명

```text
safe_haven_summary.csv
```

---

### 추천 컬럼

| Event | BTC Verdict | Gold Verdict | Significant |
|---|---|---|---|

---

# 5. 현재 기준 우선순위

## 반드시 추천

```text
1. main_btc_gold_compare.png
2. car_comparison.png
3. rolling_corr.png
```

---

## 있으면 좋은 수준

```text
4. quantreg_heatmap.png
5. garch_gamma_coefficients.png
6. model_comparison_summary.csv
```

---

# 6. 현재 구조 기준 최종 판단

현재 프로젝트는:

```text
GPR 생성 및 검증
```

쪽은 이미 충분히 강하다.

반면 부족한 건:

```text
금융시장 반응을 직관적으로 보여주는 대표 Figure
```

이다.

따라서:

```text
BTC vs Gold
BTC vs SP500
Event Window Return
```

등 금융시장 반응 중심 Figure를 보강하는 것이  
현재 단계에서 가장 효과적인 개선 방향이다.
