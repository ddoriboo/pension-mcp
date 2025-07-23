#!/usr/bin/env python3
"""
금융감독원 OpenAPI 클라이언트 (웹 애플리케이션용)
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

class FSSPensionClient:
    """금융감독원 연금 정보 API 클라이언트"""
    
    def __init__(self, service_key: str):
        self.service_key = service_key
        self.base_url = "https://www.fss.or.kr/openapi/api"
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.aclose()
    
    def _build_api_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        """API URL 생성"""
        base_params = {"key": self.service_key}
        base_params.update(params)
        
        url = f"{self.base_url}/{endpoint}"
        query_string = urlencode(base_params)
        return f"{url}?{query_string}"
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """API 요청 실행"""
        try:
            url = self._build_api_url(endpoint, params)
            logger.info(f"API 요청: {url}")
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"API 응답: {data.get('message', 'Unknown')}, 데이터 수: {data.get('count', 0)}")
            return data
                    
        except Exception as e:
            logger.error(f"API 요청 실패: {e}")
            return {"error": str(e), "code": "999", "message": "API 호출 실패"}
    
    async def get_pension_savings_companies(self, year: str = "2023", quarter: str = "4", area_code: str = None) -> Dict[str, Any]:
        """연금저축 회사별 수익률·수수료율 조회"""
        params = {"year": year, "quarter": quarter}
        if area_code:
            params["areaCode"] = area_code
        return await self._make_api_request("psCorpList.json", params)
    
    async def get_pension_savings_products(self, year: str = "2023", quarter: str = "4", area_code: str = None) -> Dict[str, Any]:
        """연금저축 상품별 수익률·수수료율 조회"""
        params = {"year": year, "quarter": quarter}
        if area_code:
            params["areaCode"] = area_code
        return await self._make_api_request("psProdList.json", params)
    
    async def get_retirement_pension_custom_fee(self, sys_type: str = "2", term: str = "5", reserve: str = "50") -> Dict[str, Any]:
        """퇴직연금 맞춤형 수수료 비교"""
        params = {"sysType": sys_type, "term": term, "reserve": reserve}
        return await self._make_api_request("rpCorpCustomFeeList.json", params)
    
    async def get_pension_statistics(self) -> Dict[str, Any]:
        """연금 통계 조회"""
        return await self._make_api_request("pensionStat.json", {})
    
    async def analyze_low_fee_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """수수료율 최저가 상품 분석"""
        try:
            # 모든 상품 데이터 조회
            products_data = await self.get_pension_savings_products()
            
            if products_data.get("code") != "000" or not products_data.get("list"):
                return []
            
            products = products_data["list"]
            
            # 판매 중인 상품만 필터링
            selling_products = [p for p in products if p.get('sells') == 'Y']
            
            # 수수료율 기준 정렬 (낮은 순)
            sorted_products = sorted(
                selling_products, 
                key=lambda x: x.get('avgFeeRate3', 999)
            )
            
            # 상위 제품들 포맷팅
            result = []
            for i, product in enumerate(sorted_products[:limit]):
                result.append({
                    "rank": i + 1,
                    "company": product.get("company", "N/A"),
                    "product": product.get("product", "N/A"),
                    "productType": product.get("productType", "N/A"),
                    "avgFeeRate3": product.get("avgFeeRate3", 0),
                    "avgEarnRate3": product.get("avgEarnRate3", 0),
                    "guarantees": product.get("guarantees") == "Y",
                    "balance": product.get("balance", 0),
                    "reserve": product.get("reserve", 0)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"수수료율 분석 실패: {e}")
            return []
    
    async def analyze_company_ranking(self, area_code: str = None) -> List[Dict[str, Any]]:
        """회사별 성과 순위 분석"""
        try:
            companies_data = await self.get_pension_savings_companies(area_code=area_code)
            
            if companies_data.get("code") != "000" or not companies_data.get("list"):
                return []
            
            companies = companies_data["list"]
            
            # 수수료율 기준 정렬 (낮은 순)
            sorted_companies = sorted(
                companies,
                key=lambda x: x.get('avgFeeRate3', 999)
            )
            
            result = []
            for i, company in enumerate(sorted_companies):
                result.append({
                    "rank": i + 1,
                    "area": company.get("area", "N/A"),
                    "company": company.get("company", "N/A"),
                    "avgFeeRate3": company.get("avgFeeRate3", 0),
                    "avgFeeRate5": company.get("avgFeeRate5", 0),
                    "avgEarnRate3": company.get("avgEarnRate3", 0),
                    "avgEarnRate5": company.get("avgEarnRate5", 0),
                    "reserve": company.get("reserve", 0)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"회사별 순위 분석 실패: {e}")
            return []
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """시장 요약 정보"""
        try:
            # 통계 데이터 조회
            stats_data = await self.get_pension_statistics()
            
            # 상품 데이터로부터 기본 통계 생성
            products_data = await self.get_pension_savings_products()
            companies_data = await self.get_pension_savings_companies()
            
            summary = {
                "totalProducts": 0,
                "totalCompanies": 0,
                "averageFeeRate": 0,
                "averageEarnRate": 0,
                "lowestFeeRate": 0,
                "highestEarnRate": 0,
                "statistics": []
            }
            
            if products_data.get("code") == "000" and products_data.get("list"):
                products = [p for p in products_data["list"] if p.get('sells') == 'Y']
                summary["totalProducts"] = len(products)
                
                if products:
                    fee_rates = [p.get('avgFeeRate3', 0) for p in products if p.get('avgFeeRate3')]
                    earn_rates = [p.get('avgEarnRate3', 0) for p in products if p.get('avgEarnRate3')]
                    
                    if fee_rates:
                        summary["averageFeeRate"] = round(sum(fee_rates) / len(fee_rates), 2)
                        summary["lowestFeeRate"] = min(fee_rates)
                    
                    if earn_rates:
                        summary["averageEarnRate"] = round(sum(earn_rates) / len(earn_rates), 2)
                        summary["highestEarnRate"] = max(earn_rates)
            
            if companies_data.get("code") == "000" and companies_data.get("list"):
                summary["totalCompanies"] = len(companies_data["list"])
            
            if stats_data.get("code") == "000" and stats_data.get("list"):
                # 최근 3년 통계 데이터만 포함
                recent_stats = [s for s in stats_data["list"] if int(s.get("year", "0")) >= 2021]
                summary["statistics"] = recent_stats[-6:]  # 최근 6개 데이터포인트
            
            return summary
            
        except Exception as e:
            logger.error(f"시장 요약 생성 실패: {e}")
            return {
                "totalProducts": 0,
                "totalCompanies": 0,
                "averageFeeRate": 0,
                "averageEarnRate": 0,
                "lowestFeeRate": 0,
                "highestEarnRate": 0,
                "statistics": []
            }