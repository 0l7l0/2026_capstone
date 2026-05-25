# DataPipeline - 데이터 파이프라인

## 1. 개요 (Overview)

Custom GPR 생성 및 금융시장 데이터 처리를 위한 데이터 파이프라인 디렉토리이다.  
GDELT 기반 지정학 이벤트 데이터 추출부터 Custom GPR 생성, 금융시장 데이터 병합 및 최종 master dataset 생성까지의 과정을 포함한다.

---

## 2. 디렉토리 구조 (Directory Structure)

```text
DataPipeline/
├── SQL_GKG/
├── raw_data/
├── processed_data/
├── GPR_custom_analysis.ipynb
├── GPR_custom_analysis_README.md
├── master_data_generated.ipynb
├── master_data_generated_README.md
└── README.md
```

---

## 3. 주요 노트북 (Notebooks)

- `GPR_custom_analysis.ipynb`  
  > Custom GPR 생성 및 공식 GPR 상관관계 분석

- `master_data_generated.ipynb`  
  > 금융시장 데이터 병합 및 최종 master dataset 생성

---

## 4. 주요 구성 요소 (Components)

| 구성 요소 | 설명 |
|---|---|
| `SQL_GKG/` | GDELT GKG 기반 지정학 이벤트 데이터 추출 SQL |
| `raw_data/` | 이벤트별 원시 뉴스 데이터 샘플 |
| `processed_data/` | Custom GPR 및 가공 데이터 |
| `GPR_custom_analysis.ipynb` | Custom GPR 생성 및 검증 |
| `master_data_generated.ipynb` | 금융시장 데이터 통합 및 master dataset 생성 |
