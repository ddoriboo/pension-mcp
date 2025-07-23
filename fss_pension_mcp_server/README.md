# 금융감독원 연금 정보 MCP 서버

금융감독원 통합연금포털의 12종 OpenAPI를 활용하여 연금 관련 정보를 수집하고 분석하는 MCP (Model Context Protocol) 서버입니다.

## 주요 기능

### 1. 기본 API 연동 기능
- **연금저축 비교공시**: 회사별/상품별 수익률·수수료율, 원리금보장 연금저축보험
- **퇴직연금 비교공시**: 수익률, 총비용 부담률, 맞춤형 수수료 비교, 원리금보장상품
- **연금 통계**: 전체 연금, 공적연금, 개인연금, 퇴직연금 통계

### 2. 고급 분석 기능
- **연금 성과 분석**: 회사별 비교, 상품 순위, 비용 분석, 트렌드 분석
- **개인 맞춤형 추천**: 사용자 프로필 기반 연금 상품 추천 및 투자 전략 제시

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서비스키 설정
금융감독원 OpenAPI 사용을 위해 [공공데이터포털](https://www.data.go.kr)에서 서비스키를 발급받아 설정해야 합니다.

```python
# fss_pension_server.py 파일에서 수정
DEFAULT_SERVICE_KEY = "YOUR_ACTUAL_SERVICE_KEY_HERE"
```

### 3. MCP 서버 실행
```bash
python fss_pension_server.py
```

## 사용 가능한 도구 (Tools)

### 기본 API 도구

1. **get_pension_savings_company_performance**
   - 연금저축 회사별 수익률·수수료율 조회
   - 매개변수: search_year, search_quarter

2. **get_pension_savings_product_performance**
   - 연금저축 상품별 수익률·수수료율 조회
   - 매개변수: search_year, search_quarter, company_name

3. **get_pension_savings_insurance**
   - 원리금보장 연금저축보험 조회
   - 매개변수: company_name

4. **get_retirement_pension_performance**
   - 퇴직연금 수익률 조회
   - 매개변수: search_year, search_quarter, company_name

5. **get_retirement_pension_cost**
   - 퇴직연금 총비용 부담률 조회
   - 매개변수: search_year, search_quarter, company_name

6. **get_retirement_pension_custom_fee**
   - 퇴직연금 맞춤형 수수료 비교
   - 매개변수: deposit_amount, contract_period, system_type

7. **get_principal_guaranteed_product_status**
   - 원리금보장상품 제공현황 조회
   - 매개변수: company_name

8. **get_principal_guaranteed_product**
   - 원리금보장 상품 조회
   - 매개변수: company_name, product_name

9. **get_pension_statistics**
   - 전체 연금 통계 조회
   - 매개변수: search_year

10. **get_public_pension_statistics**
    - 공적연금 통계 조회
    - 매개변수: search_year

11. **get_personal_pension_statistics**
    - 개인연금 통계 조회
    - 매개변수: search_year

12. **get_retirement_pension_statistics**
    - 퇴직연금 통계 조회
    - 매개변수: search_year

### 고급 분석 도구

13. **analyze_pension_performance**
    - 연금 성과 종합 분석
    - 매개변수: analysis_type (company_comparison, product_ranking, cost_analysis, trend_analysis)

14. **generate_pension_recommendation**
    - 개인 맞춤형 연금 상품 추천
    - 매개변수: user_age, monthly_income, risk_preference, target_retirement_age, current_pension_amount

## 사용 예시

### 1. 기본 API 호출
```json
{
  "tool": "get_pension_savings_company_performance",
  "arguments": {
    "search_year": "2023",
    "search_quarter": "4"
  }
}
```

### 2. 성과 분석
```json
{
  "tool": "analyze_pension_performance",
  "arguments": {
    "analysis_type": "company_comparison",
    "search_year": "2023",
    "search_quarter": "4"
  }
}
```

### 3. 개인 맞춤형 추천
```json
{
  "tool": "generate_pension_recommendation",
  "arguments": {
    "user_age": 35,
    "monthly_income": 500,
    "risk_preference": "moderate",
    "target_retirement_age": 65,
    "current_pension_amount": 5000
  }
}
```

## 활용 가능한 서비스 시나리오

### 1. 연금 현황 진단 서비스
- 사용자의 현재 연금 상품을 분석하여 동일 연령대/소득 수준 대비 상대적 위치 제시
- 미래 연금 수령액 시뮬레이션 및 목표 달성률 진단

### 2. 상품 최적화 서비스
- 수수료 최저가 상품 추천
- 수익률 우수 상품 추천
- 포트폴리오 리밸런싱 제안

### 3. 세제 혜택 최적화 서비스
- 세액공제 한도 활용 가이드
- 연금 제도 변화 알림 및 영향 분석

### 4. 연금 상품 연결 서비스
- 추천 상품 원클릭 가입/이체 지원
- 연금 포트폴리오 자동 리밸런싱

## 기술적 특징

- **비동기 처리**: httpx를 사용한 비동기 API 호출로 성능 최적화
- **에러 처리**: 견고한 예외 처리 및 로깅 시스템
- **데이터 변환**: XML/JSON 자동 파싱 및 변환
- **확장성**: 새로운 분석 기능 및 추천 알고리즘 쉽게 추가 가능

## 주의사항

1. **서비스키 필수**: 금융감독원 OpenAPI 사용을 위해 유효한 서비스키가 필요합니다.
2. **API 제한**: 공공데이터포털의 API 호출 제한을 준수해야 합니다.
3. **데이터 정확성**: API에서 제공하는 데이터의 정확성과 최신성을 확인하시기 바랍니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

