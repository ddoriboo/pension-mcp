# FSS Pension MCP Server & AI Consultation Service

한국 금융감독원(FSS) 연금 데이터를 활용한 MCP 서버와 AI 기반 연금 상담 웹 서비스

## 📋 프로젝트 구성

이 저장소는 두 개의 주요 컴포넌트로 구성되어 있습니다:

### 1. 🔌 MCP Server (`fss_pension_mcp_server/`)
- **Model Context Protocol** 기반 연금 데이터 서버
- Claude와 같은 AI 모델에 FSS 연금 데이터 제공
- 실시간 연금 상품 정보 및 통계 조회

### 2. 🌐 Web Service (`fss_pension_web/`)
- **AI 기반 연금 상담** 웹 애플리케이션
- OpenAI GPT-4를 활용한 개인 맞춤형 연금 추천
- Railway 배포 지원

## 🚀 주요 기능

### MCP Server
- ✅ FSS OpenAPI 실시간 데이터 연동
- ✅ 연금상품 검색 및 필터링
- ✅ 수수료율 최저가 상품 분석
- ✅ 회사별 성과 순위 제공
- ✅ 연금 통계 데이터 제공

### Web Service
- 🤖 **AI 연금 전문가**: GPT-4 기반 맞춤형 상담
- 📊 **실시간 대시보드**: FSS 데이터 기반 시장 현황
- 👤 **개인화 추천**: 나이, 소득, 위험성향 고려
- 📈 **은퇴 시나리오**: 구체적인 은퇴 계획 분석
- 💬 **직관적 채팅 UI**: 전문 상담사와 대화하는 경험

## 🛠 기술 스택

- **Backend**: Python 3.11, FastAPI, MCP Protocol
- **AI**: OpenAI GPT-4
- **Data**: FSS OpenAPI (금융감독원)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Deployment**: Railway, Docker
- **Charts**: Chart.js

## 📦 설치 및 실행

### MCP Server

```bash
cd fss_pension_mcp_server
pip install -r requirements.txt

# 환경변수 설정
export FSS_SERVICE_KEY="your_fss_api_key"

# 서버 실행
python fss_pension_server.py
```

### Web Service

```bash
cd fss_pension_web
pip install -r requirements.txt

# 환경변수 설정
export FSS_SERVICE_KEY="your_fss_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# 웹 서비스 실행
python3 simple_app.py
```

브라우저에서 `http://localhost:8000` 접속

## 🌐 Railway 배포

### 1. GitHub 연결
```bash
git clone https://github.com/ddoriboo/pension-mcp.git
cd pension-mcp/fss_pension_web
```

### 2. Railway 설정
- Railway 대시보드에서 GitHub 저장소 연결
- `fss_pension_web` 디렉토리를 루트로 설정

### 3. 환경변수 설정
```
FSS_SERVICE_KEY=your_actual_fss_api_key
OPENAI_API_KEY=your_actual_openai_api_key
```

### 4. 자동 배포
- GitHub push 시 자동 배포
- 헬스체크: `/api/health`

## 📡 API 문서

### MCP Server Tools
- `get_pension_products`: 연금상품 목록 조회
- `search_products`: 조건별 상품 검색
- `get_low_fee_products`: 저비용 상품 분석
- `get_company_ranking`: 회사별 순위
- `get_pension_statistics`: 연금 통계

### Web Service API
- `GET /api/market-summary`: 시장 요약
- `POST /api/ai-chat-with-profile`: AI 상담
- `POST /api/ai-recommendation`: 개인화 추천
- `POST /api/retirement-scenario`: 은퇴 시나리오 분석

## 📊 데이터 소스

- **금융감독원 통합연금포털 OpenAPI**
- 실시간 데이터 업데이트 (2023년 4분기 기준)
- 1,900+ 연금 상품 분석
- 은행, 자산운용, 보험사 전체 데이터

## 🔐 API 키 발급

### FSS API Key
1. [금융감독원 통합연금포털](https://www.fss.or.kr/openapi) 접속
2. 회원가입 후 API 키 신청
3. 승인 후 발급된 키 사용

### OpenAI API Key
1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. API 키 생성
3. GPT-4 액세스 권한 확인

## 🤝 기여하기

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

## 📞 문의

- **이슈**: [GitHub Issues](https://github.com/ddoriboo/pension-mcp/issues)
- **데이터 출처**: 금융감독원 통합연금포털
- **MCP 프로토콜**: [Anthropic MCP](https://github.com/anthropics/mcp)

---

**🎯 실제 FSS 데이터 기반 연금 전문가 서비스**  
정확하고 신뢰할 수 있는 연금 상담을 AI와 함께 경험해보세요!