# FSS 연금 AI 상담 대시보드

금융감독원(FSS) 연금 데이터를 활용한 AI 기반 연금 상담 웹 서비스입니다.

## 🚀 주요 기능

### 📊 실시간 데이터 대시보드
- **수수료율 최저가 상품 TOP 10**: 실제 FSS 데이터 기반 순위
- **회사별 성과 비교**: 은행, 자산운용, 보험사별 수수료율 순위
- **시장 통계**: 연금 시장 전체 현황 및 추이

### 🤖 AI 연금 상담
- **OpenAI GPT-4 기반**: 전문 연금 상담사 역할
- **개인 맞춤형 상담**: 나이, 소득, 위험성향, 은퇴계획 고려
- **실시간 FSS 데이터**: 최신 연금 상품 정보 기반 추천
- **은퇴 시나리오 분석**: 구체적인 은퇴 계획 수립 지원

### 📈 시각화 & 인터페이스
- Chart.js를 활용한 연금 통계 차트
- 직관적인 채팅 UI 및 빠른 질문 버튼
- 반응형 대시보드 (모바일 지원)

## 🛠 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **OpenAI GPT-4**: AI 연금 상담 엔진
- **httpx**: 비동기 HTTP 클라이언트
- **Pandas**: 데이터 분석 및 처리

### Frontend
- **Bootstrap 5**: 반응형 UI 프레임워크
- **Chart.js**: 데이터 시각화
- **Vanilla JavaScript**: 채팅 UI 및 클라이언트 로직

### 배포
- **Railway**: 자동 배포 플랫폼
- **uvicorn**: ASGI 서버

## 🔧 로컬 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
export FSS_SERVICE_KEY="your_fss_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. 서버 실행
```bash
python3 simple_app.py
```

브라우저에서 `http://localhost:8000` 접속

## 🚀 Railway 배포

### 1. GitHub 연결
- Railway에서 GitHub 저장소 연결
- `fss_pension_web` 디렉토리 선택

### 2. 환경변수 설정
Railway 대시보드에서 다음 환경변수 설정:
```
FSS_SERVICE_KEY=your_actual_fss_api_key
OPENAI_API_KEY=your_actual_openai_api_key
ENVIRONMENT=production
```

### 3. 자동 배포
- GitHub에 push하면 자동으로 배포
- 헬스체크: `/api/health`

## 📡 API 엔드포인트

### 기본 정보
- `GET /`: 메인 대시보드 페이지
- `GET /api/health`: 헬스 체크

### 데이터 API
- `GET /api/market-summary`: 시장 전체 요약
- `GET /api/low-fee-products`: 수수료율 최저가 상품
- `GET /api/company-ranking`: 회사별 순위
- `GET /api/pension-statistics`: 연금 통계

### AI 상담 API
- `POST /api/ai-chat-with-profile`: 프로필 기반 AI 상담
- `POST /api/ai-recommendation`: 개인화 연금 추천
- `POST /api/retirement-scenario`: 은퇴 시나리오 분석
- `DELETE /api/chat-history/{user_id}`: 채팅 기록 삭제

## 📊 데이터 소스

- **금융감독원 통합연금포털 OpenAPI**
- 실시간 데이터 업데이트
- 2023년 4분기 기준 최신 데이터

## 🔐 보안 고려사항

- API 키는 환경변수로 관리
- CORS 정책 적용
- 입력값 검증 및 SQL 인젝션 방지

## 📱 반응형 지원

- 데스크톱, 태블릿, 모바일 지원
- Bootstrap 5 기반 반응형 레이아웃
- 터치 친화적 UI

## 🤝 기여하기

1. 이 저장소를 Fork
2. 새 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- 데이터 출처: 금융감독원 통합연금포털
- API 문의: FSS OpenAPI 지원팀