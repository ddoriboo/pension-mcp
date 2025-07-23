#!/usr/bin/env python3
"""
간단한 웹 애플리케이션 (Railway 배포용)
"""

import os
import sys
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.fss_client import FSSPensionClient
from core.ai_consultant import PensionAIConsultant

app = FastAPI(title="FSS 연금 대시보드", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 (절대 경로로 설정)
import pathlib
BASE_DIR = pathlib.Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API 키 설정 (개행문자 및 공백 제거)
FSS_SERVICE_KEY = os.getenv("FSS_SERVICE_KEY")
if FSS_SERVICE_KEY:
    FSS_SERVICE_KEY = FSS_SERVICE_KEY.strip().replace('\n', '').replace('\r', '').replace(' ', '')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip().replace('\n', '').replace('\r', '').replace(' ', '')
    # API 키 형식 검증
    if not OPENAI_API_KEY.startswith('sk-'):
        print(f"Warning: OpenAI API key does not start with 'sk-': {OPENAI_API_KEY[:20]}...")
        OPENAI_API_KEY = None

# 클라이언트는 lazy initialization으로 변경
fss_client = None
ai_consultant = None

def get_fss_client():
    global fss_client
    if fss_client is None:
        if not FSS_SERVICE_KEY:
            raise HTTPException(status_code=500, detail="FSS_SERVICE_KEY environment variable is required")
        fss_client = FSSPensionClient(FSS_SERVICE_KEY)
    return fss_client

def get_ai_consultant():
    global ai_consultant
    if ai_consultant is None:
        if not FSS_SERVICE_KEY or not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="FSS_SERVICE_KEY and OPENAI_API_KEY environment variables are required")
        ai_consultant = PensionAIConsultant(OPENAI_API_KEY, FSS_SERVICE_KEY)
    return ai_consultant

# Pydantic 모델 정의
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class UserProfile(BaseModel):
    age: Optional[int] = None
    monthly_income: Optional[int] = None
    risk_preference: Optional[str] = None
    target_retirement_age: Optional[int] = None
    current_pension_amount: Optional[int] = None

class ChatWithProfile(BaseModel):
    message: str
    user_id: Optional[str] = None
    user_profile: Optional[UserProfile] = None

class RecommendationRequest(BaseModel):
    user_profile: UserProfile

class RetirementScenario(BaseModel):
    monthly_living_cost: Optional[int] = 300
    additional_savings: Optional[int] = 0
    life_expectancy: Optional[int] = 85

class ScenarioAnalysisRequest(BaseModel):
    user_profile: UserProfile
    scenario: RetirementScenario

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지 - AI 연금 진단 및 상담"""
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """대시보드 페이지 - 연금상품 데이터"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "FSS Pension Dashboard"}

@app.get("/api/market-summary")
async def market_summary():
    try:
        client = get_fss_client()
        summary = await client.get_market_summary()
        return {"success": True, "data": summary}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/low-fee-products")
async def low_fee_products(limit: int = 10):
    try:
        client = get_fss_client()
        products = await client.analyze_low_fee_products(limit=limit)
        return {"success": True, "data": products, "total": len(products)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/company-ranking")
async def company_ranking():
    try:
        client = get_fss_client()
        companies = await client.analyze_company_ranking()
        return {"success": True, "data": companies, "total": len(companies)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/pension-statistics")
async def pension_statistics():
    try:
        client = get_fss_client()
        stats = await client.get_pension_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}

# === AI 상담 API 엔드포인트 ===

@app.post("/api/ai-chat")
async def ai_chat(chat_request: ChatMessage):
    """기본 AI 채팅 (프로필 없이)"""
    try:
        user_id = chat_request.user_id or str(uuid.uuid4())
        consultant = get_ai_consultant()
        result = await consultant.chat(user_id, chat_request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-chat-with-profile")
async def ai_chat_with_profile(chat_request: ChatWithProfile):
    """프로필 기반 AI 채팅"""
    try:
        user_id = chat_request.user_id or str(uuid.uuid4())
        user_profile = chat_request.user_profile.dict() if chat_request.user_profile else None
        
        # 환경변수 확인
        if not FSS_SERVICE_KEY:
            return {"success": False, "error": "FSS_SERVICE_KEY environment variable is not configured"}
        if not OPENAI_API_KEY:
            return {"success": False, "error": "OPENAI_API_KEY environment variable is not configured"}
        
        consultant = get_ai_consultant()
        result = await consultant.chat(user_id, chat_request.message, user_profile)
        return result
    except Exception as e:
        # 더 자세한 오류 로깅
        import traceback
        error_details = traceback.format_exc()
        print(f"AI Chat Error: {error_details}")  # Railway 로그에 출력
        return {"success": False, "error": f"Internal server error: {str(e)}"}

@app.post("/api/ai-recommendation")
async def ai_recommendation(rec_request: RecommendationRequest):
    """개인 맞춤형 연금 추천"""
    try:
        user_profile = rec_request.user_profile.dict()
        consultant = get_ai_consultant()
        result = await consultant.generate_personalized_recommendation(user_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/retirement-scenario")
async def retirement_scenario_analysis(scenario_request: ScenarioAnalysisRequest):
    """은퇴 시나리오 분석"""
    try:
        user_profile = scenario_request.user_profile.dict()
        scenario = scenario_request.scenario.dict()
        consultant = get_ai_consultant()
        result = await consultant.analyze_retirement_scenario(user_profile, scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat-history/{user_id}")
async def clear_chat_history(user_id: str):
    """채팅 히스토리 삭제"""
    try:
        consultant = get_ai_consultant()
        consultant.clear_conversation_history(user_id)
        return {"success": True, "message": "채팅 히스토리가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai-status")
async def ai_status():
    """AI 서비스 상태 확인"""
    status = {
        "ai_service": "active",
        "openai_configured": bool(OPENAI_API_KEY and len(OPENAI_API_KEY) > 10),
        "fss_configured": bool(FSS_SERVICE_KEY),
        "environment_variables": {
            "FSS_SERVICE_KEY": "Set" if FSS_SERVICE_KEY else "Missing",
            "OPENAI_API_KEY": "Set" if OPENAI_API_KEY else "Missing"
        },
        "api_key_details": {
            "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
            "openai_key_starts_with_sk": OPENAI_API_KEY.startswith('sk-') if OPENAI_API_KEY else False,
            "openai_key_preview": OPENAI_API_KEY[:20] + "..." if OPENAI_API_KEY and len(OPENAI_API_KEY) > 20 else OPENAI_API_KEY,
            "fss_key_length": len(FSS_SERVICE_KEY) if FSS_SERVICE_KEY else 0
        },
        "timestamp": "2025-07-23"
    }
    
    # OpenAI API 연결 테스트
    if OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            # 간단한 API 호출로 연결 테스트 (fallback 포함)
            try:
                test_response = await client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                status["openai_test"] = "Success (gpt-4.1-mini-2025-04-14)"
            except Exception as primary_error:
                # 모델이 없을 경우 대체 모델로 시도
                try:
                    test_response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    status["openai_test"] = "Success (fallback to gpt-3.5-turbo)"
                    status["model_fallback"] = f"Primary model error: {str(primary_error)}"
                except Exception as fallback_error:
                    raise fallback_error
        except Exception as e:
            status["openai_test"] = f"Failed: {str(e)}"
    else:
        status["openai_test"] = "API Key not set"
    
    return status

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)