"""
Test script for the MCP Cost Chatbot
"""

import asyncio
import logging
from ai_assistant import CostAnalysisAssistant
from mcp_client import CostExplorerMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_client():
    """Test MCP client functionality."""
    print("🧪 Testing MCP Client...")
    
    client = CostExplorerMCPClient()
    await client.initialize()
    
    try:
        # Test current month dates
        start_date, end_date = client.get_current_month_dates()
        print(f"✅ Current month dates: {start_date} to {end_date}")
        
        # Test last 3 months dates
        start_date, end_date = client.get_last_n_months_dates(3)
        print(f"✅ Last 3 months dates: {start_date} to {end_date}")
        
        # Test cost and usage data
        print("📊 Testing cost and usage data retrieval...")
        cost_data = await client.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity="MONTHLY"
        )
        
        if "error" in cost_data:
            print(f"❌ Error getting cost data: {cost_data['error']}")
        else:
            print("✅ Cost data retrieved successfully")
            if "ResultsByTime" in cost_data:
                print(f"   - Found {len(cost_data['ResultsByTime'])} time periods")
        
    except Exception as e:
        print(f"❌ MCP Client test failed: {e}")
    
    await client.close()

async def test_ai_assistant():
    """Test AI assistant functionality."""
    print("\n🤖 Testing AI Assistant...")
    
    assistant = CostAnalysisAssistant()
    await assistant.initialize()
    
    try:
        # Test intent extraction
        test_queries = [
            "이번 달 AWS 비용이 얼마나 나왔나요?",
            "지난 3개월간 EC2 서비스 비용을 보여주세요",
            "리전별 비용 분석을 해주세요",
            "비용이 가장 많이 나온 서비스 TOP 5는?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Testing query: {query}")
            intent = assistant.extract_intent_and_parameters(query)
            print(f"   Intent: {intent}")
        
        # Test full response generation (commented out to avoid API calls during testing)
        # print("\n💬 Testing response generation...")
        # response = await assistant.generate_response("이번 달 AWS 비용이 얼마나 나왔나요?")
        # print(f"Response: {response[:200]}...")
        
        print("✅ AI Assistant tests completed")
        
    except Exception as e:
        print(f"❌ AI Assistant test failed: {e}")
    
    await assistant.close()

async def test_configuration():
    """Test configuration and environment setup."""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from config import (
            AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_REGION,
            MCP_SERVER_URL, MCP_SERVER_PORT
        )
        
        print(f"✅ AWS Region: {AWS_REGION}")
        print(f"✅ Bedrock Model: {BEDROCK_MODEL_ID}")
        print(f"✅ Bedrock Region: {BEDROCK_REGION}")
        print(f"✅ MCP Server: {MCP_SERVER_URL}:{MCP_SERVER_PORT}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting MCP Cost Chatbot Tests\n")
    
    await test_configuration()
    await test_mcp_client()
    await test_ai_assistant()
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
