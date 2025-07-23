#!/usr/bin/env python3
"""
금융감독원 OpenAPI를 활용한 연금 정보/콘텐츠 생성 MCP 서버

이 서버는 금융감독원 통합연금포털의 12종 OpenAPI를 활용하여
연금 관련 정보를 수집하고 분석하여 AI가 활용할 수 있는 형태로 제공합니다.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
import pandas as pd
import xmltodict
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 금융감독원 OpenAPI 기본 설정
FSS_API_BASE_URL = "https://www.fss.or.kr/openapi/api"
DEFAULT_SERVICE_KEY = "49d25d57b112aa90ad14183172a3c668"  # 실제 사용시 서비스키 필요

class FSSPensionServer:
    """금융감독원 연금 정보 MCP 서버"""
    
    def __init__(self, service_key: str = DEFAULT_SERVICE_KEY):
        self.service_key = service_key
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.aclose()
    
    def _build_api_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        """API URL 생성"""
        base_params = {
            "key": self.service_key
        }
        base_params.update(params)
        
        url = f"{FSS_API_BASE_URL}/{endpoint}"
        query_string = urlencode(base_params)
        return f"{url}?{query_string}"
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """API 요청 실행"""
        try:
            url = self._build_api_url(endpoint, params)
            logger.info(f"API 요청: {url}")
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                return response.json()
            elif "application/xml" in content_type or "text/xml" in content_type:
                return xmltodict.parse(response.text)
            else:
                # 기본적으로 JSON으로 파싱 시도
                try:
                    return response.json()
                except:
                    return {"raw_response": response.text}
                    
        except Exception as e:
            logger.error(f"API 요청 실패: {e}")
            return {"error": str(e)}
    
    async def get_pension_savings_company_performance(self, 
                                                    year: str = None,
                                                    quarter: str = None,
                                                    area_code: str = None) -> Dict[str, Any]:
        """연금저축 회사별 수익률·수수료율 조회 (API 1)"""
        params = {}
        if year:
            params["year"] = year
        if quarter:
            params["quarter"] = quarter
        if area_code:
            params["areaCode"] = area_code
            
        return await self._make_api_request("psCorpList.json", params)
    
    async def get_pension_savings_product_performance(self,
                                                    year: str = None,
                                                    quarter: str = None,
                                                    area_code: str = None) -> Dict[str, Any]:
        """연금저축 상품별 수익률·수수료율 조회 (API 2)"""
        params = {}
        if year:
            params["year"] = year
        if quarter:
            params["quarter"] = quarter
        if area_code:
            params["areaCode"] = area_code
            
        return await self._make_api_request("psProdList.json", params)
    
    async def get_pension_savings_insurance(self,
                                          area_code: str = None,
                                          channel_code: str = None) -> Dict[str, Any]:
        """원리금보장 연금저축보험 조회 (API 3)"""
        params = {}
        if area_code:
            params["areaCode"] = area_code
        if channel_code:
            params["channelCode"] = channel_code
            
        return await self._make_api_request("psGuaranteedProdList.json", params)
    
    async def get_retirement_pension_performance(self,
                                               year: str = None,
                                               quarter: str = None,
                                               sys_type: str = None) -> Dict[str, Any]:
        """퇴직연금 수익률 조회 (API 4)"""
        params = {}
        if year:
            params["year"] = year
        if quarter:
            params["quarter"] = quarter
        if sys_type:
            params["sysType"] = sys_type
            
        return await self._make_api_request("rpCorpResultList.json", params)
    
    async def get_retirement_pension_cost(self,
                                        year: str = None) -> Dict[str, Any]:
        """퇴직연금 총비용 부담률 조회 (API 5)"""
        params = {}
        if year:
            params["year"] = year
            
        return await self._make_api_request("rpCorpBurdenRatioList.json", params)
    
    async def get_retirement_pension_custom_fee(self,
                                              sys_type: str = None,
                                              term: str = None,
                                              reserve: str = None) -> Dict[str, Any]:
        """퇴직연금 맞춤형 수수료 비교 조회 (API 6)"""
        params = {}
        if sys_type:
            params["sysType"] = sys_type
        if term:
            params["term"] = term
        if reserve:
            params["reserve"] = reserve
            
        return await self._make_api_request("rpCorpCustomFeeList.json", params)
    
    async def get_principal_guaranteed_product_status(self,
                                                    area_code: str = None) -> Dict[str, Any]:
        """원리금보장상품 제공현황 조회 (API 7)"""
        params = {}
        if area_code:
            params["areaCode"] = area_code
            
        return await self._make_api_request("rpGuaranteedProdSupplyList.json", params)
    
    async def get_principal_guaranteed_product(self,
                                             area_code: str,
                                             sys_type: str,
                                             report_date: str,
                                             product_type: str = None) -> Dict[str, Any]:
        """원리금보장 상품 조회 (API 8)"""
        params = {
            "areaCode": area_code,
            "sysType": sys_type,
            "reportDate": report_date
        }
        if product_type:
            params["productType"] = product_type
            
        return await self._make_api_request("rpGuaranteedProdList.json", params)
    
    async def get_pension_statistics(self) -> Dict[str, Any]:
        """연금 통계 조회 (API 9)"""
        params = {}
        return await self._make_api_request("pensionStat.json", params)
    
    async def get_public_pension_statistics(self) -> Dict[str, Any]:
        """공적연금 통계 조회 (API 10)"""
        params = {}
        return await self._make_api_request("publicPensionStat.json", params)
    
    async def get_personal_pension_statistics(self,
                                            stat_type: str) -> Dict[str, Any]:
        """개인연금 통계 조회 (API 11)"""
        params = {
            "statType": stat_type
        }
        return await self._make_api_request("personalPensionStat.json", params)
    
    async def get_retirement_pension_statistics(self,
                                              stat_type: str) -> Dict[str, Any]:
        """퇴직연금 통계 조회 (API 12)"""
        params = {
            "statType": stat_type
        }
        return await self._make_api_request("retirementPensionStat.json", params)

# MCP 서버 인스턴스 생성
app = Server("fss-pension-server")
fss_server = FSSPensionServer()

@app.list_tools()
async def list_tools() -> ListToolsResult:
    """사용 가능한 도구 목록 반환"""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_pension_savings_company_performance",
                description="연금저축 회사별 수익률·수수료율 정보를 조회합니다. 특정 연도와 분기를 지정할 수 있습니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        },
                        "search_quarter": {
                            "type": "string",
                            "description": "조회할 분기 (예: '1', '2', '3', '4')"
                        }
                    }
                }
            ),
            Tool(
                name="get_pension_savings_product_performance",
                description="연금저축 상품별 수익률·수수료율 정보를 조회합니다. 회사명으로 필터링할 수 있습니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        },
                        "search_quarter": {
                            "type": "string",
                            "description": "조회할 분기 (예: '1', '2', '3', '4')"
                        },
                        "company_name": {
                            "type": "string",
                            "description": "금융회사명 (예: '삼성생명', 'KB국민은행')"
                        }
                    }
                }
            ),
            Tool(
                name="get_pension_savings_insurance",
                description="원리금보장 연금저축보험 상품 정보를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "보험회사명 (예: '삼성생명', '한화생명')"
                        }
                    }
                }
            ),
            Tool(
                name="get_retirement_pension_performance",
                description="퇴직연금 사업자별 수익률 정보를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        },
                        "search_quarter": {
                            "type": "string",
                            "description": "조회할 분기 (예: '1', '2', '3', '4')"
                        },
                        "company_name": {
                            "type": "string",
                            "description": "퇴직연금 사업자명"
                        }
                    }
                }
            ),
            Tool(
                name="get_retirement_pension_cost",
                description="퇴직연금 총비용 부담률 및 수수료 정보를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        },
                        "search_quarter": {
                            "type": "string",
                            "description": "조회할 분기 (예: '1', '2', '3', '4')"
                        },
                        "company_name": {
                            "type": "string",
                            "description": "퇴직연금 사업자명"
                        }
                    }
                }
            ),
            Tool(
                name="get_retirement_pension_custom_fee",
                description="적립금액에 따른 퇴직연금 맞춤형 수수료 정보를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deposit_amount": {
                            "type": "string",
                            "description": "적립금액 (예: '1000000', '5000000')"
                        },
                        "contract_period": {
                            "type": "string",
                            "description": "계약기간 (예: '1', '3', '5')"
                        },
                        "system_type": {
                            "type": "string",
                            "description": "제도유형 (예: 'DB', 'DC', 'IRP')"
                        }
                    }
                }
            ),
            Tool(
                name="get_principal_guaranteed_product_status",
                description="원리금보장상품의 사업자별 제공현황 정보를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "사업자명"
                        }
                    }
                }
            ),
            Tool(
                name="get_principal_guaranteed_product",
                description="퇴직연금 원리금보장 상품 정보를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "사업자명"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "상품명"
                        }
                    }
                }
            ),
            Tool(
                name="get_pension_statistics",
                description="개인연금, 퇴직연금, 국민연금 등 전체 연금 적립금 통계를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        }
                    }
                }
            ),
            Tool(
                name="get_public_pension_statistics",
                description="국민연금, 공무원연금 등 공적연금 적립금 통계를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        }
                    }
                }
            ),
            Tool(
                name="get_personal_pension_statistics",
                description="세제적격여부 및 업권별 개인연금 적립금 통계를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        }
                    }
                }
            ),
            Tool(
                name="get_retirement_pension_statistics",
                description="제도별 퇴직연금 적립금 통계를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_year": {
                            "type": "string",
                            "description": "조회할 연도 (예: '2023')"
                        }
                    }
                }
            ),
            Tool(
                name="analyze_pension_performance",
                description="연금 상품의 성과를 분석하고 인사이트를 제공합니다. 여러 API 데이터를 조합하여 종합적인 분석을 수행합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "description": "분석 유형 ('company_comparison', 'product_ranking', 'cost_analysis', 'trend_analysis')",
                            "enum": ["company_comparison", "product_ranking", "cost_analysis", "trend_analysis"]
                        },
                        "search_year": {
                            "type": "string",
                            "description": "분석 대상 연도 (예: '2023')"
                        },
                        "search_quarter": {
                            "type": "string",
                            "description": "분석 대상 분기 (예: '4')"
                        }
                    },
                    "required": ["analysis_type"]
                }
            ),
            Tool(
                name="generate_pension_recommendation",
                description="사용자의 조건에 맞는 연금 상품 추천을 생성합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_age": {
                            "type": "integer",
                            "description": "사용자 나이"
                        },
                        "monthly_income": {
                            "type": "integer",
                            "description": "월 소득 (만원 단위)"
                        },
                        "risk_preference": {
                            "type": "string",
                            "description": "위험 선호도 ('conservative', 'moderate', 'aggressive')",
                            "enum": ["conservative", "moderate", "aggressive"]
                        },
                        "target_retirement_age": {
                            "type": "integer",
                            "description": "목표 은퇴 나이"
                        },
                        "current_pension_amount": {
                            "type": "integer",
                            "description": "현재 연금 적립액 (만원 단위)"
                        }
                    },
                    "required": ["user_age", "monthly_income", "risk_preference"]
                }
            )
        ]
    )

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """도구 호출 처리"""
    try:
        if name == "get_pension_savings_company_performance":
            result = await fss_server.get_pension_savings_company_performance(
                search_year=arguments.get("search_year"),
                search_quarter=arguments.get("search_quarter")
            )
        elif name == "get_pension_savings_product_performance":
            result = await fss_server.get_pension_savings_product_performance(
                search_year=arguments.get("search_year"),
                search_quarter=arguments.get("search_quarter"),
                company_name=arguments.get("company_name")
            )
        elif name == "get_pension_savings_insurance":
            result = await fss_server.get_pension_savings_insurance(
                company_name=arguments.get("company_name")
            )
        elif name == "get_retirement_pension_performance":
            result = await fss_server.get_retirement_pension_performance(
                search_year=arguments.get("search_year"),
                search_quarter=arguments.get("search_quarter"),
                company_name=arguments.get("company_name")
            )
        elif name == "get_retirement_pension_cost":
            result = await fss_server.get_retirement_pension_cost(
                search_year=arguments.get("search_year"),
                search_quarter=arguments.get("search_quarter"),
                company_name=arguments.get("company_name")
            )
        elif name == "get_retirement_pension_custom_fee":
            result = await fss_server.get_retirement_pension_custom_fee(
                deposit_amount=arguments.get("deposit_amount"),
                contract_period=arguments.get("contract_period"),
                system_type=arguments.get("system_type")
            )
        elif name == "get_principal_guaranteed_product_status":
            result = await fss_server.get_principal_guaranteed_product_status(
                company_name=arguments.get("company_name")
            )
        elif name == "get_principal_guaranteed_product":
            result = await fss_server.get_principal_guaranteed_product(
                company_name=arguments.get("company_name"),
                product_name=arguments.get("product_name")
            )
        elif name == "get_pension_statistics":
            result = await fss_server.get_pension_statistics(
                search_year=arguments.get("search_year")
            )
        elif name == "get_public_pension_statistics":
            result = await fss_server.get_public_pension_statistics(
                search_year=arguments.get("search_year")
            )
        elif name == "get_personal_pension_statistics":
            result = await fss_server.get_personal_pension_statistics(
                search_year=arguments.get("search_year")
            )
        elif name == "get_retirement_pension_statistics":
            result = await fss_server.get_retirement_pension_statistics(
                search_year=arguments.get("search_year")
            )
        elif name == "analyze_pension_performance":
            result = await analyze_pension_performance(
                analysis_type=arguments.get("analysis_type"),
                search_year=arguments.get("search_year"),
                search_quarter=arguments.get("search_quarter")
            )
        elif name == "generate_pension_recommendation":
            result = await generate_pension_recommendation(
                user_age=arguments.get("user_age"),
                monthly_income=arguments.get("monthly_income"),
                risk_preference=arguments.get("risk_preference"),
                target_retirement_age=arguments.get("target_retirement_age"),
                current_pension_amount=arguments.get("current_pension_amount")
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"알 수 없는 도구: {name}")]
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        )
        
    except Exception as e:
        logger.error(f"도구 호출 오류 ({name}): {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"오류 발생: {str(e)}")]
        )

async def analyze_pension_performance(analysis_type: str, search_year: str = None, search_quarter: str = None) -> Dict[str, Any]:
    """연금 성과 분석"""
    try:
        if analysis_type == "company_comparison":
            # 회사별 성과 비교 분석
            company_data = await fss_server.get_pension_savings_company_performance(search_year, search_quarter)
            product_data = await fss_server.get_pension_savings_product_performance(search_year, search_quarter)
            
            analysis = {
                "analysis_type": "회사별 성과 비교",
                "period": f"{search_year}년 {search_quarter}분기" if search_year and search_quarter else "최신 데이터",
                "company_performance": company_data,
                "product_details": product_data,
                "insights": [
                    "수익률 상위 회사와 하위 회사 간의 격차 분석",
                    "수수료율 대비 수익률 효율성 평가",
                    "장기 성과 추이 분석"
                ]
            }
            
        elif analysis_type == "product_ranking":
            # 상품별 순위 분석
            product_data = await fss_server.get_pension_savings_product_performance(search_year, search_quarter)
            
            analysis = {
                "analysis_type": "상품별 순위 분석",
                "period": f"{search_year}년 {search_quarter}분기" if search_year and search_quarter else "최신 데이터",
                "product_ranking": product_data,
                "insights": [
                    "수익률 기준 상위 상품 분석",
                    "수수료율 기준 최저비용 상품 분석",
                    "위험 대비 수익률 분석"
                ]
            }
            
        elif analysis_type == "cost_analysis":
            # 비용 분석
            cost_data = await fss_server.get_retirement_pension_cost(search_year, search_quarter)
            custom_fee_data = await fss_server.get_retirement_pension_custom_fee()
            
            analysis = {
                "analysis_type": "비용 구조 분석",
                "period": f"{search_year}년 {search_quarter}분기" if search_year and search_quarter else "최신 데이터",
                "cost_breakdown": cost_data,
                "custom_fee_comparison": custom_fee_data,
                "insights": [
                    "총비용 부담률 업체별 비교",
                    "적립금액별 수수료 차이 분석",
                    "비용 절감 방안 제시"
                ]
            }
            
        elif analysis_type == "trend_analysis":
            # 트렌드 분석
            current_year = search_year or str(datetime.now().year)
            prev_year = str(int(current_year) - 1)
            
            current_stats = await fss_server.get_pension_statistics(current_year)
            prev_stats = await fss_server.get_pension_statistics(prev_year)
            
            analysis = {
                "analysis_type": "연금 시장 트렌드 분석",
                "period": f"{prev_year}년 대비 {current_year}년",
                "current_statistics": current_stats,
                "previous_statistics": prev_stats,
                "insights": [
                    "연금 적립금 증가율 분석",
                    "제도별 성장 패턴 분석",
                    "시장 전망 및 예측"
                ]
            }
        
        else:
            analysis = {"error": f"지원하지 않는 분석 유형: {analysis_type}"}
        
        return analysis
        
    except Exception as e:
        return {"error": f"분석 중 오류 발생: {str(e)}"}

async def generate_pension_recommendation(user_age: int, monthly_income: int, risk_preference: str,
                                        target_retirement_age: int = None, current_pension_amount: int = None) -> Dict[str, Any]:
    """개인 맞춤형 연금 상품 추천"""
    try:
        # 기본 설정
        target_retirement_age = target_retirement_age or 65
        current_pension_amount = current_pension_amount or 0
        years_to_retirement = target_retirement_age - user_age
        
        # 최신 상품 데이터 조회
        current_year = str(datetime.now().year)
        product_data = await fss_server.get_pension_savings_product_performance(current_year)
        insurance_data = await fss_server.get_pension_savings_insurance()
        
        # 위험 선호도에 따른 상품 필터링
        risk_mapping = {
            "conservative": {"min_return": 0, "max_return": 5, "product_types": ["원리금보장", "안정형"]},
            "moderate": {"min_return": 3, "max_return": 8, "product_types": ["혼합형", "균형형"]},
            "aggressive": {"min_return": 5, "max_return": 15, "product_types": ["주식형", "성장형"]}
        }
        
        risk_profile = risk_mapping.get(risk_preference, risk_mapping["moderate"])
        
        # 추천 로직
        recommendations = {
            "user_profile": {
                "age": user_age,
                "monthly_income": monthly_income,
                "risk_preference": risk_preference,
                "years_to_retirement": years_to_retirement,
                "current_pension_amount": current_pension_amount
            },
            "recommended_products": [],
            "investment_strategy": {},
            "tax_benefits": {},
            "action_items": []
        }
        
        # 투자 전략 수립
        if years_to_retirement > 20:
            strategy = "장기 성장 중심 전략"
            allocation = {"주식형": 60, "혼합형": 30, "안정형": 10}
        elif years_to_retirement > 10:
            strategy = "균형 성장 전략"
            allocation = {"주식형": 40, "혼합형": 40, "안정형": 20}
        else:
            strategy = "안정성 중심 전략"
            allocation = {"주식형": 20, "혼합형": 30, "안정형": 50}
        
        recommendations["investment_strategy"] = {
            "strategy_name": strategy,
            "asset_allocation": allocation,
            "expected_return": f"{risk_profile['min_return']}-{risk_profile['max_return']}%"
        }
        
        # 세제 혜택 계산
        max_deduction = min(monthly_income * 12 * 0.15, 7000000)  # 연간 소득의 15%, 최대 700만원
        current_deduction = current_pension_amount * 0.15 if current_pension_amount else 0
        additional_deduction_available = max_deduction - current_deduction
        
        recommendations["tax_benefits"] = {
            "max_annual_deduction": max_deduction,
            "current_deduction": current_deduction,
            "additional_available": additional_deduction_available,
            "tax_saving_rate": "15% (소득세 + 지방소득세)"
        }
        
        # 액션 아이템 생성
        action_items = []
        
        if additional_deduction_available > 0:
            action_items.append(f"세액공제 한도 {additional_deduction_available:,}원 추가 활용 가능")
        
        if years_to_retirement > 10 and risk_preference == "conservative":
            action_items.append("은퇴까지 충분한 시간이 있으므로 적극적 투자 고려")
        
        if current_pension_amount < monthly_income * 12 * 10:  # 연소득의 10배 미만
            action_items.append("연금 적립액 증액 필요 - 목표: 연소득의 10-15배")
        
        action_items.append("연 1회 포트폴리오 리밸런싱 실시")
        action_items.append("수수료 0.5% 이하 상품 우선 선택")
        
        recommendations["action_items"] = action_items
        
        # 상품 데이터가 있다면 구체적인 상품 추천 추가
        if product_data and not product_data.get("error"):
            recommendations["data_source"] = "금융감독원 최신 데이터 기반"
            recommendations["recommended_products"] = product_data
        
        return recommendations
        
    except Exception as e:
        return {"error": f"추천 생성 중 오류 발생: {str(e)}"}

async def main():
    """MCP 서버 실행"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="fss-pension-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={}
                    ),
                ),
            )
    finally:
        await fss_server.close()

if __name__ == "__main__":
    asyncio.run(main())

