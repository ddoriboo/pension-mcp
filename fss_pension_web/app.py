#!/usr/bin/env python3
"""
FSS 연금 정보 웹 애플리케이션
FastAPI를 사용한 연금 데이터 대시보드
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.fss_client import FSSPensionClient

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수에서 서비스키 가져오기 (Railway 배포용)
FSS_SERVICE_KEY = os.getenv("FSS_SERVICE_KEY", "49d25d57b112aa90ad14183172a3c668")

# FSS 클라이언트 전역 변수
fss_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global fss_client
    
    # 시작 시 FSS 클라이언트 초기화
    fss_client = FSSPensionClient(FSS_SERVICE_KEY)
    logger.info("FSS 연금 클라이언트 초기화 완료")
    
    yield
    
    # 종료 시 클라이언트 정리
    if fss_client:
        await fss_client.close()
        logger.info("FSS 연금 클라이언트 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="FSS 연금 정보 대시보드",
    description="금융감독원 연금 데이터를 활용한 연금상품 비교 서비스",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (프론트엔드에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 홈페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "FSS Pension Dashboard"}

@app.get("/api/market-summary")
async def get_market_summary() -> Dict[str, Any]:
    """시장 전체 요약 정보"""
    try:
        if not fss_client:
            raise HTTPException(status_code=500, detail="FSS 클라이언트가 초기화되지 않음")
        
        summary = await fss_client.get_market_summary()
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"시장 요약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/low-fee-products")
async def get_low_fee_products(limit: int = 10) -> Dict[str, Any]:
    """수수료율 최저가 상품 목록"""
    try:
        if not fss_client:
            raise HTTPException(status_code=500, detail="FSS 클라이언트가 초기화되지 않음")
        
        products = await fss_client.analyze_low_fee_products(limit=limit)
        return {
            "success": True,
            "data": products,
            "total": len(products)
        }
    except Exception as e:
        logger.error(f"저비용 상품 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/company-ranking")
async def get_company_ranking(area_code: str = None) -> Dict[str, Any]:
    """회사별 성과 순위"""
    try:
        if not fss_client:
            raise HTTPException(status_code=500, detail="FSS 클라이언트가 초기화되지 않음")
        
        companies = await fss_client.analyze_company_ranking(area_code=area_code)
        return {
            "success": True,
            "data": companies,
            "total": len(companies)
        }
    except Exception as e:
        logger.error(f"회사 순위 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pension-statistics")
async def get_pension_statistics() -> Dict[str, Any]:
    """연금 통계 데이터"""
    try:
        if not fss_client:
            raise HTTPException(status_code=500, detail="FSS 클라이언트가 초기화되지 않음")
        
        stats = await fss_client.get_pension_statistics()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"연금 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/custom-fee-comparison")
async def get_custom_fee_comparison(
    sys_type: str = "2",  # DC
    term: str = "5",      # 5년
    reserve: str = "50"   # 5천만원
) -> Dict[str, Any]:
    """맞춤형 수수료 비교"""
    try:
        if not fss_client:
            raise HTTPException(status_code=500, detail="FSS 클라이언트가 초기화되지 않음")
        
        fees = await fss_client.get_retirement_pension_custom_fee(
            sys_type=sys_type,
            term=term,
            reserve=reserve
        )
        return {
            "success": True,
            "data": fees
        }
    except Exception as e:
        logger.error(f"맞춤형 수수료 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/search")
async def search_products(
    company: str = None,
    product_type: str = None,
    max_fee_rate: float = None,
    min_earn_rate: float = None
) -> Dict[str, Any]:
    """상품 검색"""
    try:
        if not fss_client:
            raise HTTPException(status_code=500, detail="FSS 클라이언트가 초기화되지 않음")
        
        # 전체 상품 데이터 가져오기
        products_data = await fss_client.get_pension_savings_products()
        
        if products_data.get("code") != "000":
            raise HTTPException(status_code=500, detail="상품 데이터 조회 실패")
        
        products = products_data.get("list", [])
        
        # 판매 중인 상품만 필터링
        filtered_products = [p for p in products if p.get('sells') == 'Y']
        
        # 검색 필터 적용
        if company:
            filtered_products = [p for p in filtered_products 
                               if company.lower() in p.get('company', '').lower()]
        
        if product_type:
            filtered_products = [p for p in filtered_products 
                               if product_type.lower() in p.get('productType', '').lower()]
        
        if max_fee_rate is not None:
            filtered_products = [p for p in filtered_products 
                               if p.get('avgFeeRate3', 999) <= max_fee_rate]
        
        if min_earn_rate is not None:
            filtered_products = [p for p in filtered_products 
                               if p.get('avgEarnRate3', -999) >= min_earn_rate]
        
        # 결과 포맷팅
        result = []
        for product in filtered_products[:50]:  # 최대 50개 결과
            result.append({
                "company": product.get("company"),
                "product": product.get("product"),
                "productType": product.get("productType"),
                "avgFeeRate3": product.get("avgFeeRate3"),
                "avgEarnRate3": product.get("avgEarnRate3"),
                "guarantees": product.get("guarantees") == "Y",
                "balance": product.get("balance"),
                "reserve": product.get("reserve"),
                "launchDate": product.get("launchDate")
            })
        
        return {
            "success": True,
            "data": result,
            "total": len(result),
            "filters": {
                "company": company,
                "product_type": product_type,
                "max_fee_rate": max_fee_rate,
                "min_earn_rate": min_earn_rate
            }
        }
        
    except Exception as e:
        logger.error(f"상품 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 개발 서버 실행
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )