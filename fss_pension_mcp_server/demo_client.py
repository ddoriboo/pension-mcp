#!/usr/bin/env python3
"""
금융감독원 연금 정보 MCP 서버 데모 클라이언트

이 클라이언트는 MCP 서버의 기능을 시연하고 실제 사용 예시를 보여줍니다.
"""

import asyncio
import json
from datetime import datetime

# 데모용 샘플 데이터 (실제 API 응답 형태)
SAMPLE_COMPANY_PERFORMANCE = {
    "response": {
        "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE"},
        "body": {
            "items": [
                {
                    "companyName": "삼성생명",
                    "totalAssets": "15000000",
                    "returnRate1Y": "5.2",
                    "returnRate3Y": "4.8",
                    "returnRate5Y": "5.1",
                    "feeRate": "1.5",
                    "longTermFeeRate3Y": "1.4"
                },
                {
                    "companyName": "한화생명",
                    "totalAssets": "8500000",
                    "returnRate1Y": "4.8",
                    "returnRate3Y": "4.5",
                    "returnRate5Y": "4.7",
                    "feeRate": "1.3",
                    "longTermFeeRate3Y": "1.2"
                },
                {
                    "companyName": "KB국민은행",
                    "totalAssets": "12000000",
                    "returnRate1Y": "4.5",
                    "returnRate3Y": "4.2",
                    "returnRate5Y": "4.4",
                    "feeRate": "1.2",
                    "longTermFeeRate3Y": "1.1"
                }
            ],
            "totalCount": 3
        }
    }
}

SAMPLE_PRODUCT_PERFORMANCE = {
    "response": {
        "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE"},
        "body": {
            "items": [
                {
                    "companyName": "삼성생명",
                    "productName": "삼성연금저축펀드",
                    "productType": "주식형",
                    "principalGuarantee": "N",
                    "returnRate1Y": "6.8",
                    "returnRate3Y": "5.5",
                    "feeRate": "1.8",
                    "totalAssets": "2500000"
                },
                {
                    "companyName": "한화생명",
                    "productName": "한화안정연금저축",
                    "productType": "채권형",
                    "principalGuarantee": "Y",
                    "returnRate1Y": "3.2",
                    "returnRate3Y": "3.5",
                    "feeRate": "0.8",
                    "totalAssets": "1800000"
                }
            ],
            "totalCount": 2
        }
    }
}

class PensionAnalysisDemo:
    """연금 분석 데모 클래스"""
    
    def __init__(self):
        self.sample_data = {
            "company_performance": SAMPLE_COMPANY_PERFORMANCE,
            "product_performance": SAMPLE_PRODUCT_PERFORMANCE
        }
    
    def analyze_company_performance(self, data):
        """회사별 성과 분석"""
        items = data["response"]["body"]["items"]
        
        # 수익률 기준 정렬
        sorted_by_return = sorted(items, key=lambda x: float(x["returnRate1Y"]), reverse=True)
        
        # 수수료 기준 정렬
        sorted_by_fee = sorted(items, key=lambda x: float(x["feeRate"]))
        
        analysis = {
            "총_회사수": len(items),
            "최고_수익률": {
                "회사명": sorted_by_return[0]["companyName"],
                "수익률": f"{sorted_by_return[0]['returnRate1Y']}%"
            },
            "최저_수수료": {
                "회사명": sorted_by_fee[0]["companyName"],
                "수수료율": f"{sorted_by_fee[0]['feeRate']}%"
            },
            "평균_수익률": f"{sum(float(item['returnRate1Y']) for item in items) / len(items):.2f}%",
            "평균_수수료": f"{sum(float(item['feeRate']) for item in items) / len(items):.2f}%"
        }
        
        return analysis
    
    def analyze_product_performance(self, data):
        """상품별 성과 분석"""
        items = data["response"]["body"]["items"]
        
        # 위험도별 분류
        risk_categories = {"주식형": [], "채권형": [], "혼합형": [], "기타": []}
        
        for item in items:
            product_type = item["productType"]
            if product_type in risk_categories:
                risk_categories[product_type].append(item)
            else:
                risk_categories["기타"].append(item)
        
        analysis = {
            "총_상품수": len(items),
            "위험도별_분포": {k: len(v) for k, v in risk_categories.items() if v},
            "원리금보장_상품수": len([item for item in items if item["principalGuarantee"] == "Y"]),
            "최고_수익률_상품": max(items, key=lambda x: float(x["returnRate1Y"])),
            "최저_수수료_상품": min(items, key=lambda x: float(x["feeRate"]))
        }
        
        return analysis
    
    def generate_user_recommendation(self, user_profile):
        """사용자 맞춤형 추천 생성"""
        age = user_profile["age"]
        income = user_profile["monthly_income"]
        risk_preference = user_profile["risk_preference"]
        
        # 나이에 따른 투자 전략
        if age < 35:
            strategy = "적극적 성장 전략"
            stock_ratio = 70
        elif age < 50:
            strategy = "균형 성장 전략"
            stock_ratio = 50
        else:
            strategy = "안정성 중심 전략"
            stock_ratio = 30
        
        # 위험 선호도 조정
        if risk_preference == "conservative":
            stock_ratio = max(20, stock_ratio - 20)
        elif risk_preference == "aggressive":
            stock_ratio = min(80, stock_ratio + 20)
        
        # 세액공제 계산
        max_deduction = min(income * 12 * 0.15, 7000000)
        
        recommendation = {
            "투자_전략": strategy,
            "권장_자산배분": {
                "주식형": f"{stock_ratio}%",
                "채권형": f"{100-stock_ratio}%"
            },
            "연간_세액공제_한도": f"{max_deduction:,}원",
            "월_권장_납입액": f"{max_deduction // 12:,}원",
            "예상_절세액": f"{max_deduction * 0.15:,}원"
        }
        
        return recommendation

def demo_basic_analysis():
    """기본 분석 기능 데모"""
    print("🔍 기본 분석 기능 데모")
    print("=" * 50)
    
    demo = PensionAnalysisDemo()
    
    # 회사별 성과 분석
    print("📊 회사별 성과 분석:")
    company_analysis = demo.analyze_company_performance(demo.sample_data["company_performance"])
    for key, value in company_analysis.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    print("\n📈 상품별 성과 분석:")
    product_analysis = demo.analyze_product_performance(demo.sample_data["product_performance"])
    for key, value in product_analysis.items():
        if key in ["최고_수익률_상품", "최저_수수료_상품"]:
            print(f"  {key}: {value['productName']} ({value['companyName']})")
        else:
            print(f"  {key}: {value}")

def demo_user_recommendations():
    """사용자 맞춤형 추천 데모"""
    print("\n👤 사용자 맞춤형 추천 데모")
    print("=" * 50)
    
    demo = PensionAnalysisDemo()
    
    # 다양한 사용자 프로필
    user_profiles = [
        {
            "name": "김영수 (30세, 보수적)",
            "age": 30,
            "monthly_income": 400,
            "risk_preference": "conservative"
        },
        {
            "name": "이미영 (40세, 적극적)",
            "age": 40,
            "monthly_income": 600,
            "risk_preference": "aggressive"
        },
        {
            "name": "박준호 (55세, 균형)",
            "age": 55,
            "monthly_income": 800,
            "risk_preference": "moderate"
        }
    ]
    
    for profile in user_profiles:
        print(f"\n🎯 {profile['name']} 추천:")
        recommendation = demo.generate_user_recommendation(profile)
        for key, value in recommendation.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")

def demo_market_insights():
    """시장 인사이트 데모"""
    print("\n💡 시장 인사이트 데모")
    print("=" * 50)
    
    insights = [
        "📈 수익률 트렌드: 주식형 연금저축펀드의 평균 수익률이 전년 대비 1.2%p 상승",
        "💰 수수료 경쟁: 대형 금융사들의 수수료 인하 경쟁으로 평균 수수료율 0.3%p 하락",
        "🏦 시장 점유율: 은행권 연금저축 상품의 시장 점유율이 보험사 대비 증가 추세",
        "⚖️ 규제 변화: 연금저축 세액공제 한도 확대로 가입자 증가 예상",
        "🎯 투자 전략: 저금리 환경에서 장기 투자 관점의 주식형 상품 선호도 증가"
    ]
    
    for insight in insights:
        print(f"  {insight}")

def demo_action_items():
    """액션 아이템 데모"""
    print("\n✅ 추천 액션 아이템")
    print("=" * 50)
    
    action_items = [
        {
            "우선순위": "높음",
            "항목": "세액공제 한도 최대 활용",
            "설명": "현재 납입액이 세액공제 한도 대비 부족합니다. 월 20만원 추가 납입으로 연간 36만원 절세 가능"
        },
        {
            "우선순위": "중간",
            "항목": "수수료 최적화",
            "설명": "현재 가입 상품의 수수료율이 시장 평균보다 0.5%p 높습니다. 유사 상품으로 이동 시 연간 15만원 절약"
        },
        {
            "우선순위": "중간",
            "항목": "포트폴리오 리밸런싱",
            "설명": "현재 자산배분이 목표 배분과 10%p 이상 차이납니다. 분기별 리밸런싱 권장"
        },
        {
            "우선순위": "낮음",
            "항목": "연금 교육 수강",
            "설명": "연금 관련 기초 지식 향상을 위한 온라인 교육 프로그램 수강 권장"
        }
    ]
    
    for item in action_items:
        print(f"  🎯 [{item['우선순위']}] {item['항목']}")
        print(f"     {item['설명']}")
        print()

def demo_mcp_integration():
    """MCP 통합 데모"""
    print("\n🤖 AI MCP 서버 통합 데모")
    print("=" * 50)
    
    print("📡 MCP 서버 기능:")
    print("  • 금융감독원 12종 OpenAPI 실시간 연동")
    print("  • 연금 데이터 자동 수집 및 분석")
    print("  • AI 모델과의 원활한 데이터 교환")
    print("  • 개인화된 연금 상담 지원")
    
    print("\n🔧 사용 가능한 MCP 도구:")
    tools = [
        "get_pension_savings_company_performance - 회사별 연금저축 성과 조회",
        "get_pension_savings_product_performance - 상품별 연금저축 성과 조회",
        "analyze_pension_performance - 종합 성과 분석",
        "generate_pension_recommendation - 맞춤형 상품 추천"
    ]
    
    for tool in tools:
        print(f"  • {tool}")
    
    print("\n💬 AI 상담 시나리오 예시:")
    print("  사용자: '30대 직장인인데 연금저축 어떤 상품이 좋을까요?'")
    print("  AI: MCP 서버를 통해 최신 상품 데이터 조회...")
    print("      → 사용자 프로필 분석")
    print("      → 시장 데이터 비교")
    print("      → 맞춤형 추천 생성")
    print("      → '귀하의 나이와 소득을 고려할 때 주식형 60%, 채권형 40% 배분을 권장합니다.'")

def main():
    """메인 데모 실행"""
    print("🎉 금융감독원 연금 정보 MCP 서버 데모")
    print(f"⏰ 데모 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 각 데모 실행
    demo_basic_analysis()
    demo_user_recommendations()
    demo_market_insights()
    demo_action_items()
    demo_mcp_integration()
    
    print("\n" + "=" * 70)
    print("🎊 데모 완료!")
    print("💡 실제 서비스에서는 금융감독원 OpenAPI를 통해 실시간 데이터를 제공합니다.")
    print("🔑 서비스키 발급 후 즉시 사용 가능합니다.")

if __name__ == "__main__":
    main()

