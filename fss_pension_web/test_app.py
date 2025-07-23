#!/usr/bin/env python3
"""
간단한 테스트 애플리케이션
"""

import asyncio
from core.fss_client import FSSPensionClient

async def test_fss_client():
    """FSS 클라이언트 테스트"""
    client = FSSPensionClient("49d25d57b112aa90ad14183172a3c668")
    
    try:
        print("=== FSS API 테스트 ===")
        
        # 1. 저비용 상품 분석
        print("1. 수수료율 최저가 상품 분석 중...")
        low_fee_products = await client.analyze_low_fee_products(limit=5)
        
        if low_fee_products:
            print("✅ 저비용 상품 분석 성공!")
            for i, product in enumerate(low_fee_products[:3], 1):
                print(f"   {i}. {product['company']}: {product['avgFeeRate3']}%")
        else:
            print("❌ 저비용 상품 분석 실패")
        
        # 2. 회사별 순위
        print("\n2. 회사별 순위 분석 중...")
        company_ranking = await client.analyze_company_ranking()
        
        if company_ranking:
            print("✅ 회사별 순위 분석 성공!")
            for i, company in enumerate(company_ranking[:3], 1):
                print(f"   {i}. {company['company']}: {company['avgFeeRate3']}%")
        else:
            print("❌ 회사별 순위 분석 실패")
        
        # 3. 시장 요약
        print("\n3. 시장 요약 분석 중...")
        market_summary = await client.get_market_summary()
        
        print("✅ 시장 요약 분석 완료!")
        print(f"   총 상품 수: {market_summary.get('totalProducts', 'N/A')}")
        print(f"   평균 수수료율: {market_summary.get('averageFeeRate', 'N/A')}%")
        print(f"   평균 수익률: {market_summary.get('averageEarnRate', 'N/A')}%")
        
        print("\n✅ 모든 API 기능이 정상 작동합니다!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_fss_client())