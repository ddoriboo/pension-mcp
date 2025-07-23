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

# API 키 설정
FSS_SERVICE_KEY = os.getenv("FSS_SERVICE_KEY")  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check required environment variables
if not FSS_SERVICE_KEY:
    raise ValueError("FSS_SERVICE_KEY environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# 클라이언트 초기화
fss_client = FSSPensionClient(FSS_SERVICE_KEY)
ai_consultant = PensionAIConsultant(OPENAI_API_KEY, FSS_SERVICE_KEY)

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
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "FSS Pension Dashboard"}

@app.get("/api/market-summary")
async def market_summary():
    try:
        summary = await fss_client.get_market_summary()
        return {"success": True, "data": summary}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/low-fee-products")
async def low_fee_products(limit: int = 10):
    try:
        products = await fss_client.analyze_low_fee_products(limit=limit)
        return {"success": True, "data": products, "total": len(products)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/company-ranking")
async def company_ranking():
    try:
        companies = await fss_client.analyze_company_ranking()
        return {"success": True, "data": companies, "total": len(companies)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/pension-statistics")
async def pension_statistics():
    try:
        stats = await fss_client.get_pension_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}

# === AI 상담 API 엔드포인트 ===

@app.post("/api/ai-chat")
async def ai_chat(chat_request: ChatMessage):
    """기본 AI 채팅 (프로필 없이)"""
    try:
        user_id = chat_request.user_id or str(uuid.uuid4())
        result = await ai_consultant.chat(user_id, chat_request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-chat-with-profile")
async def ai_chat_with_profile(chat_request: ChatWithProfile):
    """프로필 기반 AI 채팅"""
    try:
        user_id = chat_request.user_id or str(uuid.uuid4())
        user_profile = chat_request.user_profile.dict() if chat_request.user_profile else None
        result = await ai_consultant.chat(user_id, chat_request.message, user_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-recommendation")
async def ai_recommendation(rec_request: RecommendationRequest):
    """개인 맞춤형 연금 추천"""
    try:
        user_profile = rec_request.user_profile.dict()
        result = await ai_consultant.generate_personalized_recommendation(user_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/retirement-scenario")
async def retirement_scenario_analysis(scenario_request: ScenarioAnalysisRequest):
    """은퇴 시나리오 분석"""
    try:
        user_profile = scenario_request.user_profile.dict()
        scenario = scenario_request.scenario.dict()
        result = await ai_consultant.analyze_retirement_scenario(user_profile, scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat-history/{user_id}")
async def clear_chat_history(user_id: str):
    """채팅 히스토리 삭제"""
    try:
        ai_consultant.clear_conversation_history(user_id)
        return {"success": True, "message": "채팅 히스토리가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai-status")
async def ai_status():
    """AI 서비스 상태 확인"""
    return {
        "ai_service": "active",
        "openai_configured": bool(OPENAI_API_KEY and len(OPENAI_API_KEY) > 10),
        "fss_configured": bool(FSS_SERVICE_KEY),
        "timestamp": "2025-07-22"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)