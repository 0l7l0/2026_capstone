## Directory Structure

```text
DataPipeline/
├── SQL_GKG/
├── raw_data/
├── processed_data/
│   ├── intermediate/
│   ├── event_level/
│   └── final/
├── GPR_custom_analysis.ipynb
├── master_data_generated.ipynb
└── README.md
```

------ ---
GPR_custom_analysis.ipynb  
-  readme 작성 필요 / 올린 ipynb 최종본
-  master_data.ipynb만 수정 필요

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
master_data.ipynb - readme 작성 필요

---
## Step 6. 결측치 처리

### 처리 원칙

| 대상 | 원인 | 처리 |
|---|---|---|
| BTC·SP500 결측 | 주말·공휴일 (NYSE 비거래일) | **제거** |
| VIX 결측 | 간헐적 API 누락 | **ffill** |
| fear_greed 결측 | 간헐적 누락 | **ffill** |


master.groupby('event_name')['fear_greed'].shift(1) 코드 수행 후   
이 작업은 각 이벤트 그룹 내에서 데이터를 한 칸씩 뒤로 밀어 '어제의 값'을 생성

따라서, 이벤트별 총 6개의 결측치 발생
