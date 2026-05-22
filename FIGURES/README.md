Figure 1-1. Hormuz Crisis / Soleimani Assassination  
Figure 1-2. Russia–Ukraine War  
Figure 1-3. Israel–Hamas War / Israel–Iran  
Figure 1-4. US–Israel–Iran   

원시 뉴스 데이터의 일별 기사 수 분포를 시각화하였다.  
붉은 점선은 실제 지정학 이벤트 발발일(Event Date)을 의미한다.  

---
Figure 2-1. Hormuz Crisis / Soleimani Assassination  
Figure 2-2. Russia–Ukraine War  
Figure 2-3. Israel–Hamas War / Israel–Iran  
Figure 2-4. US–Israel–Iran   

전처리 이후 tone score 분포와 일별 기사 수 변화를 시각화하였다.  
지정학 필터링 및 최소 기사 수 조건 적용 후의 데이터 특성을 보여준다.  
  
---

Figure 03_correlation_heatmap.png. Custom GPR 상관관계 히트맵  
: 공식 GPR과 Custom GPR(F1~F5) 간의 Pearson 및 Spearman 상관관계를 히트맵 형태로 시각화하였다.  

Figure 04_scatter_matrix.png. Custom GPR 산점도 행렬  
: Custom GPR(F1~F5) 및 공식 GPR 간의 분포와 변수 간 관계를 산점도 행렬 형태로 시각화하였다.  

Figure 05_gpr_timeseries.png. 이벤트별 Custom GPR 시계열 비교   
: 주요 지정학 이벤트별 Custom GPR(F1 ~ F5)와 공식 GPR 지수의 시계열 변화를 비교하였다.  
모든 지수는 시각적 비교를 위해 0~1 범위로 정규화하였다.  
  
Figure 06_official_vs_ours.png. 공식 GPR과 최고 상관 Custom GPR 비교  
: 각 이벤트별로 공식 GPR과 가장 높은 상관계수를 보인 Custom GPR 공식을 비교하였다.  
붉은 점선은 이벤트 발생일(Event Date)을 의미한다.   

Figure 07_event_window.png. 이벤트 전후 Custom GPR 변화  

이벤트 발생일 기준 ±26일 구간에서 Custom GPR 지수의 변화를 시각화하였다.  
붉은 점선은 이벤트 발생일(Event Date)을 의미한다.  
