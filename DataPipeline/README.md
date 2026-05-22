/DataPipeline
안에서 디렉토리 라인 정리 예정

├── SQL_GKG/  
│   ├── hormuz_crisis.sql  
│   ├── soleimani_assassination.sql  
│   ├── russia_ukraine_war.sql  
│   ├── israel_hamas_war.sql  
│   ├── israel_iran.sql  
│   ├── us_israel_iran.sql  
│   └── README.md   
    
├── raw_data/  
│   ├── hormuz_raw.csv  
│   ├── solaimani_raw.csv  
│   ├── ukraine_raw.csv  
│   └── ...  
   
├── processed_data/    
│
│    ├── intermediate/.  
│    │   ├── gpr_hormuz_soleimani.csv.  
│    │   ├── gpr_russia_ukraine.csv   
│    │   ├── gpr_israel_hamas_iran.csv   
│    │   └── gpr_us_israel_iran.csv    
│    │
│    ├── event_level/    
│    │   ├── gpr_custom_hormuz_crisis.csv   
│    │   ├── gpr_custom_soleimani_assassination.csv   
│    │   ├── gpr_custom_russia_ukraine_war.csv   
│    │   ├── gpr_custom_israel_hamas_war.csv  
│    │   ├── gpr_custom_israel_iran.csv   
│    │   └── gpr_custom_us_israel_iran.csv  
│    │
│    ├── final/  
│    │   ├── custom_gpr_daily.csv   
│    │   ├── gpr_combined.csv   
│    │   ├── merged_market_data.csv  
│    │   ├── final_master_data.csv  
│    │   └── gpr_correlation_summary.csv  
│    │   ├── merged_market_data.csv      
│    │   └── final_master_data.csv   
│  
├── GPR_custom_analysis.ipynb  
├── master_data.ipynb  
└── README.md  

processed_data/intermediate:
대용량 이벤트 데이터를 그룹 단위로 분할 처리한 중간 산출물

processed_data/event_level:
이벤트별 Custom GPR 시계열 데이터

processed_data/final:
최종 병합 데이터 및 분석 결과 요약


------ ---
GPR_custom_analysis.ipynb  
- step중에서, 2번만 png 한국어 -> 영어 변경, 주석, 다운 파일 정리하면 됨. (현재 파일 말고 주피터랩 연동된 파일로 대체 예정) + 그리고 전체 readme 작성

## Step 2 - 1. CSV 로드 + 데이터 이해

| 컬럼 | 설명 | 비고 |
|---|---|---|
| `event_timestamp` | 기사 수집 시각 (UTC) | GDELT 15분 단위 |
| `date` | YYYYMMDD 날짜 | 일별 집계 키 |
| `url` | 기사 URL | 중복 제거 기준 |
| `tone_score` | 전체 어조 | 음수=부정, 양수=긍정 |
| `positive_score` | 긍정 단어 비율 | V2Tone[1] |
| `negative_score` | 부정 단어 비율 | V2Tone[2] |
| `polarity` | 감정 강도 (pos+neg) | V2Tone[3] |
| `themes` | GDELT 자동 분류 태그 | `;`로 구분 |

### Step 2 - 2  데이터 전처리

1. **중복 제거** — URL 기준
2. **결측치 처리** — tone 컬럼 NA 제거, 텍스트 컬럼 빈 문자열 대체
3. **이상값 처리** — |tone_score| > 20 제거
4. **지정학 테마 필터** — GEO_THEMES 태그 포함 기사만 유지
5. **`_date` 파생 컬럼** — timezone-naive datetime
6. **최소 기사 수 필터** — 하루 5건 미만 날짜 제거

### Step 2 - 3  GPR 대체 지수 5종 산출

| 공식 | 이름 | 수식 | 참고 문헌 |
|---|---|---|---|
| F1 | 단순 일평균 tone 역전 | `−mean(tone)` | Caldara & Iacoviello 2022 |
| F2 | 극성 가중 tone | `−Σ(tone×polarity)/Σ(polarity)` | BBVA Research 2025 |
| F3 | 보도량×tone 복합 | `−mean(tone) × log(1+N)` | BNP Paribas AM 2022 |
| F4 | 부정 비율 기반 | `neg/(pos+neg)` | Caldara 원본 정신 |
| F5 | 28일 지수가중 이동평균 | F2에 기하 가중 MA 적용 | BBVA Monitor |



-----------
master_data.ipynb도 코드는 완료 상태(주피터랩), 주석 제거 + readme 작성 필요
