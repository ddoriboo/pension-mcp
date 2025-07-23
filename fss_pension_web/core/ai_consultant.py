#!/usr/bin/env python3
"""
AI 연금 상담사 - OpenAI GPT를 활용한 연금 전문 상담 서비스
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from openai import AsyncOpenAI
from .fss_client import FSSPensionClient

logger = logging.getLogger(__name__)

class PensionAIConsultant:
    """AI 연금 상담사"""
    
    def __init__(self, openai_api_key: str, fss_service_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.fss_client = FSSPensionClient(fss_service_key)
        self.conversation_history = {}  # 사용자별 대화 히스토리
        
    async def close(self):
        """리소스 정리"""
        await self.fss_client.close()
    
    def _get_system_prompt(self) -> str:
        """연금 전문 시스템 프롬프트"""
        return """
        당신은 대한민국의 연금 전문가입니다. 금융감독원(FSS) 데이터를 기반으로 정확하고 유용한 연금 상담을 제공합니다.

        ## 전문 분야
        - 연금저축, 퇴직연금(DB/DC/IRP) 상품 분석
        - 수수료율 및 수익률 비교 분석  
        - 개인 맞춤형 연금 포트폴리오 설계
        - 연금 세제 혜택 최적화
        - 은퇴 계획 및 노후 자금 계산

        ## 상담 원칙
        1. **정확한 정보**: FSS 공식 데이터만 활용
        2. **개인 맞춤형**: 나이, 소득, 위험성향 고려
        3. **쉬운 설명**: 복잡한 금융 용어를 알기 쉽게 설명
        4. **실용적 조언**: 구체적이고 실행 가능한 방안 제시
        5. **투명성**: 추천 근거와 장단점 명시

        ## 응답 형식
        - 친근하고 전문적인 톤 유지
        - 복잡한 내용은 단계별로 설명
        - 필요시 구체적인 상품명과 수수료율 제시
        - 위험 요소나 주의사항도 함께 안내

        현재 시간: {current_time}
        데이터 기준: 2023년 4분기 FSS 최신 데이터
        """
    
    async def get_market_context(self) -> str:
        """현재 연금 시장 컨텍스트 생성"""
        try:
            # 최신 시장 데이터 조회
            market_summary = await self.fss_client.get_market_summary()
            low_fee_products = await self.fss_client.analyze_low_fee_products(limit=5)
            company_ranking = await self.fss_client.analyze_company_ranking()
            
            context = f"""
            ## 현재 연금 시장 현황 (2023년 4분기 기준)
            
            **전체 현황:**
            - 총 상품 수: {market_summary.get('totalProducts', 'N/A')}개
            - 평균 수수료율: {market_summary.get('averageFeeRate', 'N/A')}%
            - 평균 수익률: {market_summary.get('averageEarnRate', 'N/A')}%
            - 최저 수수료율: {market_summary.get('lowestFeeRate', 'N/A')}%
            
            **수수료율 최저가 상품 TOP 5:**
            """
            
            for i, product in enumerate(low_fee_products[:5], 1):
                context += f"""
            {i}. {product['company']} - {product['product'][:50]}...
               수수료율: {product['avgFeeRate3']}% | 수익률: {product['avgEarnRate3']}%"""
            
            context += f"""
            
            **회사별 수수료율 순위 (상위 3개):**
            """
            
            for i, company in enumerate(company_ranking[:3], 1):
                context += f"""
            {i}. {company['company']}: {company['avgFeeRate3']}%"""
            
            return context
            
        except Exception as e:
            logger.error(f"시장 컨텍스트 생성 실패: {e}")
            return "현재 시장 데이터를 불러오는 중 오류가 발생했습니다."
    
    async def chat(self, user_id: str, message: str, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """AI 상담 채팅"""
        try:
            # 사용자별 대화 히스토리 초기화
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # 시장 컨텍스트 가져오기 (FSS API 호출 실패 시 기본값 사용)
            try:
                market_context = await self.get_market_context()
            except Exception as market_error:
                logger.warning(f"FSS 시장 데이터 로드 실패: {market_error}")
                market_context = """
                ## 현재 연금 시장 현황
                시장 데이터를 불러오는 중 오류가 발생했습니다. 
                일반적인 연금 상담을 진행하겠습니다.
                """
            
            # 사용자 프로필 컨텍스트
            profile_context = ""
            if user_profile:
                profile_context = f"""
                
                ## 상담자 정보
                - 나이: {user_profile.get('age', 'N/A')}세
                - 월소득: {user_profile.get('monthly_income', 'N/A')}만원
                - 위험성향: {user_profile.get('risk_preference', 'N/A')}
                - 목표 은퇴나이: {user_profile.get('target_retirement_age', 'N/A')}세
                - 현재 연금 적립액: {user_profile.get('current_pension_amount', 'N/A')}만원
                """
            
            # 시스템 프롬프트 구성
            system_prompt = self._get_system_prompt().format(
                current_time=datetime.now().strftime("%Y년 %m월 %d일")
            ) + market_context + profile_context
            
            # 메시지 구성
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 대화 히스토리 추가 (최근 10개만)
            for hist in self.conversation_history[user_id][-10:]:
                messages.append(hist)
            
            # 현재 질문 추가
            messages.append({"role": "user", "content": message})
            
            # OpenAI API 호출 (모델 fallback 포함)
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",  # 요청한 모델
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.7,
                    top_p=0.9
                )
            except Exception as model_error:
                if "model" in str(model_error).lower() or "invalid" in str(model_error).lower():
                    # 모델이 없을 경우 대체 모델 사용
                    logger.warning(f"Primary model failed, trying fallback: {model_error}")
                    try:
                        response = await self.openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",  # 첫 번째 대체 모델
                            messages=messages,
                            max_tokens=1500,
                            temperature=0.7,
                            top_p=0.9
                        )
                    except:
                        # 마지막 대체 모델
                        response = await self.openai_client.chat.completions.create(
                            model="gpt-3.5-turbo-0125",  # 가장 최신 3.5 모델
                            messages=messages,
                            max_tokens=1500,
                            temperature=0.7,
                            top_p=0.9
                        )
                else:
                    raise model_error
            
            ai_response = response.choices[0].message.content
            
            # 대화 히스토리 저장
            self.conversation_history[user_id].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": ai_response}
            ])
            
            # 히스토리 크기 제한 (최대 20개 메시지)
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return {
                "success": True,
                "response": ai_response,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"AI 상담 실패 (user_id: {user_id}): {error_details}")
            print(f"AI Consultant Error: {error_details}")  # Railway 로그에 출력
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_personalized_recommendation(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """개인 맞춤형 연금 추천 생성"""
        try:
            # FSS 데이터 기반 분석
            low_fee_products = await self.fss_client.analyze_low_fee_products(limit=10)
            market_summary = await self.fss_client.get_market_summary()
            
            # AI 추천 요청
            recommendation_prompt = f"""
            다음 고객에게 최적의 연금 상품을 추천해주세요:
            
            **고객 프로필:**
            - 나이: {user_profile.get('age')}세
            - 월소득: {user_profile.get('monthly_income')}만원
            - 위험성향: {user_profile.get('risk_preference')}
            - 목표 은퇴나이: {user_profile.get('target_retirement_age', 65)}세
            - 현재 연금 적립액: {user_profile.get('current_pension_amount', 0)}만원
            
            **추천 형식:**
            1. 추천 상품 3개 (구체적 상품명, 회사명, 수수료율)
            2. 추천 근거
            3. 예상 은퇴 자금
            4. 주의사항
            
            현재 수수료율이 가장 낮은 상품들을 우선 고려하되, 고객의 위험성향과 나이를 종합적으로 고려해주세요.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                messages=[
                    {"role": "system", "content": self._get_system_prompt().format(
                        current_time=datetime.now().strftime("%Y년 %m월 %d일")
                    )},
                    {"role": "user", "content": recommendation_prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            return {
                "success": True,
                "recommendation": response.choices[0].message.content,
                "based_on_products": low_fee_products[:5],  # 참고한 상품들
                "market_summary": market_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"개인화 추천 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_retirement_scenario(self, user_profile: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """은퇴 시나리오 분석"""
        try:
            analysis_prompt = f"""
            다음 고객의 은퇴 시나리오를 분석해주세요:
            
            **기본 정보:**
            - 현재 나이: {user_profile.get('age')}세
            - 월소득: {user_profile.get('monthly_income')}만원
            - 목표 은퇴나이: {user_profile.get('target_retirement_age', 65)}세
            - 현재 연금 적립액: {user_profile.get('current_pension_amount', 0)}만원
            
            **시나리오:**
            - 희망 은퇴 후 월생활비: {scenario.get('monthly_living_cost', 300)}만원
            - 연금 외 추가 저축: {scenario.get('additional_savings', 0)}만원/월
            - 예상 수명: {scenario.get('life_expectancy', 85)}세
            
            **분석 요청:**
            1. 현재 계획으로 목표 달성 가능성
            2. 부족한 금액과 추가 저축 필요액
            3. 구체적인 실행 방안
            4. 위험 요소 및 대안책
            
            수치적 계산과 함께 실현 가능한 조언을 제공해주세요.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1-mini-2025-04-14",
                messages=[
                    {"role": "system", "content": self._get_system_prompt().format(
                        current_time=datetime.now().strftime("%Y년 %m월 %d일")
                    )},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.3  # 더 정확한 계산을 위해 낮은 temperature
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "scenario": scenario,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"은퇴 시나리오 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def clear_conversation_history(self, user_id: str):
        """대화 히스토리 초기화"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]