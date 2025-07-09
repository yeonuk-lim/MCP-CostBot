"""AI Assistant for AWS Cost Analysis using MCP Server functions directly."""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
import boto3
from datetime import datetime, timedelta
import re

from config import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)

class CostAnalysisAssistant:
    """AI Assistant for AWS Cost Analysis using MCP server functions."""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize the assistant."""
        logger.info("Cost Analysis Assistant initialized")
        
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        # Keep only last 10 messages to avoid token limits
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    async def call_mcp_function(self, function_name: str, **kwargs) -> str:
        """Call MCP server function directly."""
        try:
            # Import MCP server functions
            from standard_mcp_server import (
                get_current_month_cost, get_service_costs, get_regional_costs,
                get_cost_forecast, get_cost_and_usage, get_cost_comparisons,
                get_cost_drivers, get_dimension_values, get_today_date
            )
            
            # Map function names to actual functions
            function_map = {
                "get_current_month_cost": get_current_month_cost,
                "get_service_costs": get_service_costs,
                "get_regional_costs": get_regional_costs,
                "get_cost_forecast": get_cost_forecast,
                "get_cost_and_usage": get_cost_and_usage,
                "get_cost_comparisons": get_cost_comparisons,
                "get_cost_drivers": get_cost_drivers,
                "get_dimension_values": get_dimension_values,
                "get_today_date": get_today_date
            }
            
            if function_name in function_map:
                func = function_map[function_name]
                result = await func(**kwargs)
                return result
            else:
                return f"알 수 없는 함수: {function_name}"
                
        except Exception as e:
            logger.error(f"Error calling MCP function {function_name}: {e}")
            return f"MCP 함수 호출 중 오류가 발생했습니다: {str(e)}"
    
    def extract_intent_and_parameters(self, user_query: str) -> Dict[str, Any]:
        """Extract intent and parameters from user query."""
        query_lower = user_query.lower()
        
        intent = {
            "function": "get_current_month_cost",
            "arguments": {}
        }
        
        # Determine which MCP function to use based on query
        if "현재" in query_lower or "이번 달" in query_lower:
            intent["function"] = "get_current_month_cost"
            
        elif "서비스" in query_lower and ("비교" in query_lower or "변화" in query_lower):
            intent["function"] = "get_cost_comparisons"
            # Extract dates if possible
            today = datetime.now()
            current_month_start = today.replace(day=1).strftime('%Y-%m-%d')
            if today.month == 1:
                last_month_start = today.replace(year=today.year-1, month=12, day=1).strftime('%Y-%m-%d')
                last_month_end = today.replace(day=1).strftime('%Y-%m-%d')
            else:
                last_month_start = today.replace(month=today.month-1, day=1).strftime('%Y-%m-%d')
                last_month_end = current_month_start
            
            if today.month == 12:
                current_month_end = today.replace(year=today.year+1, month=1, day=1).strftime('%Y-%m-%d')
            else:
                current_month_end = today.replace(month=today.month+1, day=1).strftime('%Y-%m-%d')
            
            intent["arguments"] = {
                "baseline_start": last_month_start,
                "baseline_end": last_month_end,
                "comparison_start": current_month_start,
                "comparison_end": current_month_end
            }
            
        elif "원인" in query_lower or "왜" in query_lower or ("변화" in query_lower and "분석" in query_lower):
            intent["function"] = "get_cost_drivers"
            # Same date logic as comparison
            today = datetime.now()
            current_month_start = today.replace(day=1).strftime('%Y-%m-%d')
            if today.month == 1:
                last_month_start = today.replace(year=today.year-1, month=12, day=1).strftime('%Y-%m-%d')
                last_month_end = today.replace(day=1).strftime('%Y-%m-%d')
            else:
                last_month_start = today.replace(month=today.month-1, day=1).strftime('%Y-%m-%d')
                last_month_end = current_month_start
            
            if today.month == 12:
                current_month_end = today.replace(year=today.year+1, month=1, day=1).strftime('%Y-%m-%d')
            else:
                current_month_end = today.replace(month=today.month+1, day=1).strftime('%Y-%m-%d')
            
            intent["arguments"] = {
                "baseline_start": last_month_start,
                "baseline_end": last_month_end,
                "comparison_start": current_month_start,
                "comparison_end": current_month_end
            }
            
        elif "서비스" in query_lower:
            if "어떤" in query_lower or "목록" in query_lower:
                intent["function"] = "get_dimension_values"
                intent["arguments"] = {"dimension": "SERVICE"}
            else:
                intent["function"] = "get_service_costs"
                # Extract months if specified
                month_numbers = re.findall(r'(\d+)개?월', query_lower)
                if month_numbers:
                    intent["arguments"]["months_back"] = int(month_numbers[0])
                    
        elif "리전" in query_lower:
            if "어떤" in query_lower or "목록" in query_lower:
                intent["function"] = "get_dimension_values"
                intent["arguments"] = {"dimension": "REGION"}
            else:
                intent["function"] = "get_regional_costs"
                
        elif "예측" in query_lower or "전망" in query_lower:
            intent["function"] = "get_cost_forecast"
            
        elif "상세" in query_lower or "자세" in query_lower:
            intent["function"] = "get_cost_and_usage"
            # Try to extract date ranges
            if "6월" in query_lower and "7월" in query_lower:
                intent["arguments"] = {
                    "start_date": "2025-06-01",
                    "end_date": "2025-08-01"
                }
            elif "일별" in query_lower:
                intent["arguments"]["granularity"] = "DAILY"
                
        elif "날짜" in query_lower or "현재" in query_lower:
            intent["function"] = "get_today_date"
            
        return intent
    
    async def generate_response(self, user_query: str) -> str:
        """Generate response using MCP server functions and Claude."""
        try:
            # Extract intent and call appropriate MCP function
            intent = self.extract_intent_and_parameters(user_query)
            function_name = intent["function"]
            arguments = intent.get("arguments", {})
            
            logger.info(f"Calling MCP function: {function_name} with args: {arguments}")
            
            # Call MCP server function
            mcp_result = await self.call_mcp_function(function_name, **arguments)
            
            # Add to conversation history
            self.add_to_history("user", user_query)
            
            # Prepare system prompt
            system_prompt = """당신은 AWS 비용 분석 전문가입니다. 사용자의 AWS 비용 관련 질문에 대해 정확하고 유용한 답변을 제공해야 합니다.

다음 규칙을 따라주세요:
1. 한국어로 친근하고 전문적인 톤으로 답변하세요
2. 제공된 실제 비용 데이터를 바탕으로 구체적으로 설명하세요
3. 필요시 비용 절약 방안을 제안하세요
4. 숫자는 쉽게 읽을 수 있도록 포맷팅하세요 (예: $1,234.56)
5. 절대로 AWS 콘솔이나 다른 페이지로 유도하지 마세요 - 제공된 데이터로만 답변하세요
6. 데이터가 없거나 오류가 있는 경우에만 그 사실을 명확히 설명하세요
7. "AWS Management Console에서 확인하세요" 같은 안내는 절대 하지 마세요"""

            # Prepare user message with MCP data
            user_message = f"""사용자 질문: {user_query}

실제 AWS 비용 데이터 (MCP 서버에서 실시간 조회):
{mcp_result}

위 실제 데이터를 바탕으로 사용자의 질문에 답변해주세요. 다른 페이지나 콘솔을 안내하지 말고, 제공된 데이터로 직접 분석하고 답변해주세요."""

            # Prepare messages for Claude
            messages = []
            for msg in self.conversation_history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Bedrock
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.1
            }
            
            response = self.bedrock.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            assistant_response = response_body['content'][0]['text']
            
            # Add to conversation history
            self.add_to_history("assistant", assistant_response)
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    async def close(self):
        """Close the assistant."""
        logger.info("Cost Analysis Assistant closed")
