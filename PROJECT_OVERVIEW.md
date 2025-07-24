# FSS AI 연금 상담 서비스 프로젝트 개요

## 📋 목차
1. [프로젝트 소개](#프로젝트-소개)
2. [파일 구조](#파일-구조)
3. [서비스 아키텍처](#서비스-아키텍처)
4. [주요 기능](#주요-기능)
5. [기술 스택](#기술-스택)
6. [API 및 환경변수](#api-및-환경변수)
7. [작동 방식](#작동-방식)
8. [배포 정보](#배포-정보)
9. [개선 이력](#개선-이력)
10. [향후 개선 방향](#향후-개선-방향)

---

## 🎯 프로젝트 소개

FSS AI 연금 상담 서비스는 금융감독원(FSS)의 연금 데이터와 OpenAI GPT-4를 결합하여 사용자에게 맞춤형 연금 상담을 제공하는 웹 애플리케이션입니다.

### 핵심 가치
- **데이터 기반**: 실시간 FSS 연금 데이터 활용
- **AI 상담**: GPT-4 기반 지능형 연금 컨설팅
- **사용자 중심**: 중장년층 친화적 UI/UX
- **접근성**: 키보드 입력 최소화, 버튼 클릭 중심 인터페이스

---

## 📁 파일 구조

```
fss_pension_mcp_server/
├── fss_pension_web/               # 웹 애플리케이션 디렉토리
│   ├── simple_app.py             # FastAPI 메인 애플리케이션
│   ├── core/                     # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── fss_client.py        # FSS API 클라이언트
│   │   └── ai_consultant.py     # AI 연금 컨설턴트
│   ├── static/                   # 정적 파일
│   │   ├── css/
│   │   │   └── dashboard.css
│   │   └── js/
│   │       └── dashboard.js
│   ├── templates/                # HTML 템플릿
│   │   ├── main.html            # AI 상담 메인 페이지
│   │   ├── dashboard.html       # 연금 데이터 대시보드
│   │   └── index.html           # (구) 통합 페이지
│   ├── requirements.txt          # Python 의존성
│   ├── Procfile                 # Railway 배포 설정
│   ├── runtime.txt              # Python 버전 지정
│   └── setup.py                 # 패키지 설정
├── fss_pension_mcp_server/       # (원본) MCP 서버 디렉토리
│   └── fss_pension_server.py    # MCP 서버 구현
└── PROJECT_OVERVIEW.md          # 프로젝트 문서 (현재 파일)
```

---

## 🏗️ 서비스 아키텍처

### 전체 구조
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   클라이언트     │────▶│   FastAPI 서버    │────▶│  외부 API들      │
│  (웹 브라우저)   │◀────│  (Railway 호스팅)  │◀────│  - FSS OpenAPI   │
└─────────────────┘     └──────────────────┘     │  - OpenAI API    │
                                                  └─────────────────┘
```

### 주요 컴포넌트

1. **FastAPI 애플리케이션** (`simple_app.py`)
   - 웹 라우팅 및 API 엔드포인트 관리
   - 환경변수 관리 및 검증
   - Lazy initialization 패턴 적용

2. **FSS 클라이언트** (`core/fss_client.py`)
   - FSS 통합연금포털 API 통신
   - 연금 상품 데이터 조회 및 분석
   - 비동기 처리로 성능 최적화

3. **AI 컨설턴트** (`core/ai_consultant.py`)
   - OpenAI GPT-4 통합
   - RAG (Retrieval-Augmented Generation) 방식
   - 대화 히스토리 관리
   - 개인화된 연금 추천 로직

4. **프론트엔드**
   - **main.html**: AI 상담 중심 인터페이스
   - **dashboard.html**: 데이터 시각화 대시보드
   - 반응형 디자인 및 접근성 고려

---

## 🚀 주요 기능

### 1. AI 연금 상담
- **진단 프로세스**: 사용자 정보 입력 → AI 분석 → 맞춤형 상담
- **대화형 인터페이스**: 자연어 질의응답
- **컨텍스트 유지**: 대화 히스토리 기반 연속 상담
- **후속 질문 자동 생성**: AI 응답 기반 관련 질문 제안

### 2. 연금 데이터 분석
- **실시간 데이터**: FSS API를 통한 최신 연금 상품 정보
- **수수료 분석**: 최저 수수료 상품 추천
- **회사별 순위**: 운용사별 통계 및 비교
- **시장 요약**: 전체 연금 시장 현황 파악

### 3. 사용자 경험 (UX)
- **카테고리 기반 질문**: 6개 주제별 구조화된 질문
- **원클릭 상호작용**: 드롭다운과 버튼으로 입력 최소화
- **마크다운 렌더링**: 표, 리스트, 헤딩 등 완벽 지원
- **접근성**: 큰 버튼, 명확한 아이콘, 다크모드 지원

### 4. 개인화 기능
- **프로필 기반 추천**: 나이, 소득, 투자성향 고려
- **은퇴 시나리오 분석**: 목표 생활비 기반 계산
- **맞춤형 조언**: 개인 상황에 따른 전략 제시

---

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Async**: asyncio, httpx
- **AI Integration**: OpenAI Python SDK
- **Data Processing**: pandas, json

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS (ES6+)
- **Icons**: Font Awesome

### Infrastructure
- **Hosting**: Railway
- **Version Control**: GitHub
- **Environment**: Docker (Railway Nixpacks)

---

## 🔑 API 및 환경변수

### 필수 환경변수
```bash
FSS_SERVICE_KEY=49d25d57b112aa90ad14183172a3c668  # FSS OpenAPI 키
OPENAI_API_KEY=sk-proj-...                        # OpenAI API 키
PORT=8000                                          # 서버 포트 (Railway 자동 설정)
```

### FSS API 엔드포인트
- Base URL: `https://www.fss.or.kr/openapi/api`
- 주요 API:
  - `/getPensionSavingProductList.json` - 연금저축 상품 목록
  - `/getCompanyRetirePensionList.json` - 퇴직연금 상품 목록

### 내부 API 엔드포인트
- `GET /` - AI 상담 메인 페이지
- `GET /dashboard` - 데이터 대시보드
- `POST /api/ai-chat-with-profile` - AI 채팅 (프로필 포함)
- `GET /api/market-summary` - 시장 요약
- `GET /api/low-fee-products` - 저수수료 상품
- `GET /api/company-ranking` - 회사별 순위

---

## ⚙️ 작동 방식

### 1. 사용자 플로우
```
1. 메인 페이지 접속
   ↓
2. 연금 진단 정보 입력
   - 나이, 월소득, 투자성향, 목표 은퇴나이
   ↓
3. AI 진단 시작
   - 사용자 프로필 분석
   - 맞춤형 초기 분석 제공
   ↓
4. 대화형 상담
   - 카테고리 선택 또는 직접 질문
   - AI 응답 및 후속 질문 제안
   ↓
5. 상세 데이터 확인 (선택)
   - 대시보드에서 연금 상품 비교
```

### 2. 데이터 처리 흐름
```python
# FSS 데이터 조회
fss_client.get_pension_products()
  → API 호출
  → 데이터 정규화
  → 캐싱 (선택)

# AI 상담 프로세스
ai_consultant.chat(user_id, message, profile)
  → 컨텍스트 구성 (프로필 + FSS 데이터)
  → OpenAI API 호출
  → 응답 포맷팅
  → 후속 질문 생성
```

### 3. 실시간 데이터 통합
- FSS API에서 실시간으로 연금 상품 정보 조회
- AI가 최신 데이터를 바탕으로 답변 생성
- 데이터와 AI 조언의 시너지 효과

---

## 🚢 배포 정보

### Railway 배포
- **Repository**: https://github.com/ddoriboo/pension-mcp.git
- **자동 배포**: main 브랜치 push 시 자동 배포
- **환경 설정**: Railway 대시보드에서 환경변수 관리

### 배포 프로세스
```bash
# 1. 코드 변경
git add .
git commit -m "Update features"
git push origin main

# 2. Railway 자동 빌드 및 배포
# 3. 서비스 재시작 및 헬스체크
```

---

## 📈 개선 이력

### v1.0 - 초기 MCP 서버
- FSS API 연동 기본 구조
- 명령줄 기반 데이터 조회

### v2.0 - 웹 애플리케이션 전환
- FastAPI 기반 웹 서비스 구축
- 기본 대시보드 UI 구현
- Railway 배포 설정

### v3.0 - AI 통합
- OpenAI GPT-4 통합
- 대화형 상담 기능 추가
- 개인화 추천 시스템

### v4.0 - UI/UX 개선
- AI 중심 서비스로 재구성
- 중장년층 친화적 인터페이스
- 마크다운 렌더링 개선
- 카테고리 기반 질문 시스템

---

## 🔮 향후 개선 방향

### 단기 목표 (1-3개월)
1. **데이터 캐싱 시스템**
   - Redis 통합으로 API 호출 최적화
   - 데이터 갱신 주기 관리

2. **사용자 인증 시스템**
   - 회원가입/로그인 기능
   - 상담 히스토리 저장
   - 개인화된 대시보드

3. **고급 분석 기능**
   - 포트폴리오 시뮬레이션
   - 세금 계산기 통합
   - 동종업계 비교 분석

### 중기 목표 (3-6개월)
1. **멀티모달 AI 지원**
   - 음성 입력/출력 기능
   - 문서 업로드 분석
   - 차트/그래프 해석

2. **연금 상품 비교 엔진**
   - 실시간 수익률 추적
   - 리스크 평가 모델
   - 최적화 알고리즘

3. **모바일 앱 개발**
   - PWA 또는 네이티브 앱
   - 푸시 알림 기능
   - 오프라인 모드 지원

### 장기 목표 (6개월+)
1. **AI 모델 고도화**
   - Fine-tuning으로 연금 전문성 강화
   - 다국어 지원
   - 감정 분석 기반 상담

2. **생태계 확장**
   - 금융기관 API 연동
   - 실제 가입 프로세스 통합
   - 파트너사 협업

3. **데이터 인텔리전스**
   - 빅데이터 분석 플랫폼
   - 예측 모델링
   - 개인화 추천 고도화

---

## 🤝 기여 방법

1. 이슈 등록: GitHub Issues에 버그나 제안사항 등록
2. 브랜치 생성: `feature/기능명` 형식으로 브랜치 생성
3. 개발 및 테스트: 로컬 환경에서 충분한 테스트
4. PR 제출: main 브랜치로 Pull Request 제출

---

## 📞 연락처

- GitHub: https://github.com/ddoriboo/pension-mcp
- 이슈 트래커: https://github.com/ddoriboo/pension-mcp/issues

---

*이 문서는 프로젝트의 현재 상태를 반영하며, 지속적으로 업데이트됩니다.*

*최종 업데이트: 2024년 1월*