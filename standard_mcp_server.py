#!/usr/bin/env python3
"""
Complete MCP Server for AWS Cost Explorer with all tools
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import boto3
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS Cost Explorer client
cost_explorer = boto3.client('ce', region_name='us-east-1')

# Create MCP server
server = Server("aws-cost-explorer-complete")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_current_month_cost",
            description="현재 월의 AWS 비용을 조회합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_service_costs",
            description="지난 N개월간 서비스별 비용을 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "months_back": {"type": "integer", "description": "조회할 개월 수", "default": 3}
                },
                "required": []
            }
        ),
        Tool(
            name="get_regional_costs",
            description="지난 N개월간 리전별 비용을 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "months_back": {"type": "integer", "description": "조회할 개월 수", "default": 1}
                },
                "required": []
            }
        ),
        Tool(
            name="get_cost_forecast",
            description="향후 N개월간 비용 예측을 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "months_ahead": {"type": "integer", "description": "예측할 개월 수", "default": 3}
                },
                "required": []
            }
        ),
        Tool(
            name="get_cost_and_usage",
            description="상세한 AWS 비용 및 사용량 데이터를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "시작 날짜 (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "종료 날짜 (YYYY-MM-DD)"},
                    "granularity": {"type": "string", "description": "세분화 (DAILY, MONTHLY)", "default": "MONTHLY"},
                    "group_by": {"type": "string", "description": "그룹화 기준 (SERVICE, REGION 등)", "default": "SERVICE"},
                    "metric": {"type": "string", "description": "메트릭 (UnblendedCost, BlendedCost 등)", "default": "UnblendedCost"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_cost_comparisons",
            description="두 기간 간의 비용을 비교 분석합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "baseline_start": {"type": "string", "description": "기준 기간 시작일 (YYYY-MM-DD)"},
                    "baseline_end": {"type": "string", "description": "기준 기간 종료일 (YYYY-MM-DD)"},
                    "comparison_start": {"type": "string", "description": "비교 기간 시작일 (YYYY-MM-DD)"},
                    "comparison_end": {"type": "string", "description": "비교 기간 종료일 (YYYY-MM-DD)"},
                    "group_by": {"type": "string", "description": "그룹화 기준", "default": "SERVICE"}
                },
                "required": ["baseline_start", "baseline_end", "comparison_start", "comparison_end"]
            }
        ),
        Tool(
            name="get_cost_drivers",
            description="비용 변화의 주요 원인을 분석합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "baseline_start": {"type": "string", "description": "기준 기간 시작일 (YYYY-MM-DD)"},
                    "baseline_end": {"type": "string", "description": "기준 기간 종료일 (YYYY-MM-DD)"},
                    "comparison_start": {"type": "string", "description": "비교 기간 시작일 (YYYY-MM-DD)"},
                    "comparison_end": {"type": "string", "description": "비교 기간 종료일 (YYYY-MM-DD)"},
                    "group_by": {"type": "string", "description": "그룹화 기준", "default": "SERVICE"}
                },
                "required": ["baseline_start", "baseline_end", "comparison_start", "comparison_end"]
            }
        ),
        Tool(
            name="get_dimension_values",
            description="사용 가능한 차원 값들을 조회합니다 (서비스, 리전 등).",
            inputSchema={
                "type": "object",
                "properties": {
                    "dimension": {"type": "string", "description": "차원 (SERVICE, REGION, INSTANCE_TYPE 등)", "default": "SERVICE"},
                    "start_date": {"type": "string", "description": "시작 날짜 (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "종료 날짜 (YYYY-MM-DD)"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_today_date",
            description="현재 날짜 정보를 조회합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle all tool calls."""
    
    if name == "get_current_month_cost":
        result = await get_current_month_cost()
    elif name == "get_service_costs":
        months_back = arguments.get("months_back", 3)
        result = await get_service_costs(months_back)
    elif name == "get_regional_costs":
        months_back = arguments.get("months_back", 1)
        result = await get_regional_costs(months_back)
    elif name == "get_cost_forecast":
        months_ahead = arguments.get("months_ahead", 3)
        result = await get_cost_forecast(months_ahead)
    elif name == "get_cost_and_usage":
        result = await get_cost_and_usage(
            arguments.get("start_date", ""),
            arguments.get("end_date", ""),
            arguments.get("granularity", "MONTHLY"),
            arguments.get("group_by", "SERVICE"),
            arguments.get("metric", "UnblendedCost")
        )
    elif name == "get_cost_comparisons":
        result = await get_cost_comparisons(
            arguments.get("baseline_start"),
            arguments.get("baseline_end"),
            arguments.get("comparison_start"),
            arguments.get("comparison_end"),
            arguments.get("group_by", "SERVICE")
        )
    elif name == "get_cost_drivers":
        result = await get_cost_drivers(
            arguments.get("baseline_start"),
            arguments.get("baseline_end"),
            arguments.get("comparison_start"),
            arguments.get("comparison_end"),
            arguments.get("group_by", "SERVICE")
        )
    elif name == "get_dimension_values":
        result = await get_dimension_values(
            arguments.get("dimension", "SERVICE"),
            arguments.get("start_date", ""),
            arguments.get("end_date", "")
        )
    elif name == "get_today_date":
        result = await get_today_date()
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=result)]

# Tool implementations
async def get_current_month_cost() -> str:
    """Get current month cost."""
    try:
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1).strftime('%Y-%m-%d')
        else:
            end_date = today.replace(month=today.month + 1, day=1).strftime('%Y-%m-%d')
        
        response = cost_explorer.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['BlendedCost']
        )
        
        if response['ResultsByTime']:
            amount = response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
            unit = response['ResultsByTime'][0]['Total']['BlendedCost']['Unit']
            return f"현재 월({start_date} ~ {end_date}) 총 비용: ${float(amount):.2f} {unit}"
        else:
            return "현재 월 비용 데이터를 찾을 수 없습니다."
    except Exception as e:
        logger.error(f"Error getting current month cost: {e}")
        return f"비용 조회 중 오류가 발생했습니다: {str(e)}"

async def get_service_costs(months_back: int = 3) -> str:
    """Get service costs."""
    try:
        today = datetime.now()
        end_date = today.replace(day=1).strftime('%Y-%m-%d')
        start_date = (today.replace(day=1) - timedelta(days=32*months_back)).replace(day=1).strftime('%Y-%m-%d')
        
        response = cost_explorer.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        
        result = f"서비스별 비용 ({start_date} ~ {end_date}):\n\n"
        
        for time_period in response['ResultsByTime']:
            period_start = time_period['TimePeriod']['Start']
            period_end = time_period['TimePeriod']['End']
            result += f"📅 기간: {period_start} ~ {period_end}\n"
            
            services = []
            for group in time_period['Groups']:
                service_name = group['Keys'][0]
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                if amount > 0:
                    services.append((service_name, amount))
            
            services.sort(key=lambda x: x[1], reverse=True)
            
            for service_name, amount in services[:10]:
                result += f"  💰 {service_name}: ${amount:.2f}\n"
            result += "\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting service costs: {e}")
        return f"서비스별 비용 조회 중 오류가 발생했습니다: {str(e)}"

async def get_regional_costs(months_back: int = 1) -> str:
    """Get regional costs."""
    try:
        today = datetime.now()
        end_date = today.replace(day=1).strftime('%Y-%m-%d')
        start_date = (today.replace(day=1) - timedelta(days=32*months_back)).replace(day=1).strftime('%Y-%m-%d')
        
        response = cost_explorer.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'REGION'}]
        )
        
        result = f"리전별 비용 ({start_date} ~ {end_date}):\n\n"
        
        for time_period in response['ResultsByTime']:
            period_start = time_period['TimePeriod']['Start']
            period_end = time_period['TimePeriod']['End']
            result += f"📅 기간: {period_start} ~ {period_end}\n"
            
            regions = []
            for group in time_period['Groups']:
                region_name = group['Keys'][0]
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                if amount > 0:
                    regions.append((region_name, amount))
            
            regions.sort(key=lambda x: x[1], reverse=True)
            
            for region_name, amount in regions:
                result += f"  🌍 {region_name}: ${amount:.2f}\n"
            result += "\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting regional costs: {e}")
        return f"리전별 비용 조회 중 오류가 발생했습니다: {str(e)}"

async def get_cost_forecast(months_ahead: int = 3) -> str:
    """Get cost forecast."""
    try:
        today = datetime.now()
        start_date = today.strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=30*months_ahead)).strftime('%Y-%m-%d')
        
        response = cost_explorer.get_cost_forecast(
            TimePeriod={'Start': start_date, 'End': end_date},
            Metric='BLENDED_COST',
            Granularity='MONTHLY'
        )
        
        result = f"비용 예측 ({start_date} ~ {end_date}):\n\n"
        
        for forecast in response['ForecastResultsByTime']:
            period_start = forecast['TimePeriod']['Start']
            period_end = forecast['TimePeriod']['End']
            mean_value = float(forecast['MeanValue'])
            result += f"📈 {period_start} ~ {period_end}: ${mean_value:.2f} (예상)\n"
        
        total_forecast = sum(float(f['MeanValue']) for f in response['ForecastResultsByTime'])
        result += f"\n💡 총 예상 비용: ${total_forecast:.2f}"
        
        return result
    except Exception as e:
        logger.error(f"Error getting cost forecast: {e}")
        return f"비용 예측 조회 중 오류가 발생했습니다: {str(e)}"

async def get_cost_and_usage(start_date: str = "", end_date: str = "", granularity: str = "MONTHLY", group_by: str = "SERVICE", metric: str = "UnblendedCost") -> str:
    """Get detailed cost and usage data."""
    try:
        if not start_date or not end_date:
            today = datetime.now()
            if not end_date:
                end_date = today.replace(day=1).strftime('%Y-%m-%d')
            if not start_date:
                start_date = (today.replace(day=1) - timedelta(days=32*2)).replace(day=1).strftime('%Y-%m-%d')
        
        params = {
            'TimePeriod': {'Start': start_date, 'End': end_date},
            'Granularity': granularity.upper(),
            'Metrics': [metric]
        }
        
        if group_by and group_by.upper() != "NONE":
            params['GroupBy'] = [{'Type': 'DIMENSION', 'Key': group_by.upper()}]
        
        response = cost_explorer.get_cost_and_usage(**params)
        
        result = f"상세 비용 및 사용량 데이터 ({start_date} ~ {end_date}):\n"
        result += f"메트릭: {metric}, 그룹화: {group_by}, 세분화: {granularity}\n\n"
        
        for time_period in response['ResultsByTime']:
            period_start = time_period['TimePeriod']['Start']
            period_end = time_period['TimePeriod']['End']
            result += f"📅 기간: {period_start} ~ {period_end}\n"
            
            if 'Groups' in time_period and time_period['Groups']:
                groups = []
                for group in time_period['Groups']:
                    group_name = group['Keys'][0] if group['Keys'] else 'Unknown'
                    if metric in group['Metrics']:
                        amount = float(group['Metrics'][metric]['Amount'])
                        unit = group['Metrics'][metric]['Unit']
                        if amount > 0:
                            groups.append((group_name, amount, unit))
                
                groups.sort(key=lambda x: x[1], reverse=True)
                
                for group_name, amount, unit in groups[:15]:
                    if metric == "UsageQuantity":
                        result += f"  📊 {group_name}: {amount:.2f} {unit}\n"
                    else:
                        result += f"  💰 {group_name}: ${amount:.2f} {unit}\n"
            else:
                if metric in time_period['Total']:
                    amount = float(time_period['Total'][metric]['Amount'])
                    unit = time_period['Total'][metric]['Unit']
                    if metric == "UsageQuantity":
                        result += f"  📊 총 사용량: {amount:.2f} {unit}\n"
                    else:
                        result += f"  💰 총 비용: ${amount:.2f} {unit}\n"
            result += "\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting cost and usage data: {e}")
        return f"상세 비용 및 사용량 조회 중 오류가 발생했습니다: {str(e)}"

async def get_cost_comparisons(baseline_start: str, baseline_end: str, comparison_start: str, comparison_end: str, group_by: str = "SERVICE") -> str:
    """Compare costs between two periods."""
    try:
        # Get baseline period data
        baseline_response = cost_explorer.get_cost_and_usage(
            TimePeriod={'Start': baseline_start, 'End': baseline_end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': group_by.upper()}]
        )
        
        # Get comparison period data
        comparison_response = cost_explorer.get_cost_and_usage(
            TimePeriod={'Start': comparison_start, 'End': comparison_end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': group_by.upper()}]
        )
        
        result = f"비용 비교 분석:\n"
        result += f"기준 기간: {baseline_start} ~ {baseline_end}\n"
        result += f"비교 기간: {comparison_start} ~ {comparison_end}\n\n"
        
        # Process baseline data
        baseline_costs = {}
        if baseline_response['ResultsByTime']:
            for group in baseline_response['ResultsByTime'][0]['Groups']:
                name = group['Keys'][0]
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                baseline_costs[name] = amount
        
        # Process comparison data
        comparison_costs = {}
        if comparison_response['ResultsByTime']:
            for group in comparison_response['ResultsByTime'][0]['Groups']:
                name = group['Keys'][0]
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                comparison_costs[name] = amount
        
        # Calculate changes
        all_items = set(baseline_costs.keys()) | set(comparison_costs.keys())
        changes = []
        
        for item in all_items:
            baseline = baseline_costs.get(item, 0)
            comparison = comparison_costs.get(item, 0)
            change = comparison - baseline
            if baseline > 0:
                percent_change = (change / baseline) * 100
            else:
                percent_change = 100 if comparison > 0 else 0
            
            changes.append((item, baseline, comparison, change, percent_change))
        
        # Sort by absolute change
        changes.sort(key=lambda x: abs(x[3]), reverse=True)
        
        result += "📊 주요 변화 (절대값 기준):\n"
        for item, baseline, comparison, change, percent in changes[:10]:
            if abs(change) > 0.01:  # Only show significant changes
                result += f"  {item}:\n"
                result += f"    기준: ${baseline:.2f} → 비교: ${comparison:.2f}\n"
                result += f"    변화: ${change:+.2f} ({percent:+.1f}%)\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting cost comparisons: {e}")
        return f"비용 비교 분석 중 오류가 발생했습니다: {str(e)}"

async def get_cost_drivers(baseline_start: str, baseline_end: str, comparison_start: str, comparison_end: str, group_by: str = "SERVICE") -> str:
    """Analyze cost change drivers."""
    try:
        # This is a simplified version - AWS has a specific API for this
        # For now, we'll use the comparison logic to identify top drivers
        comparison_result = await get_cost_comparisons(baseline_start, baseline_end, comparison_start, comparison_end, group_by)
        
        result = f"비용 변화 주요 원인 분석:\n"
        result += f"기준 기간: {baseline_start} ~ {baseline_end}\n"
        result += f"비교 기간: {comparison_start} ~ {comparison_end}\n\n"
        result += "💡 주요 비용 변화 동인:\n"
        result += comparison_result.split("📊 주요 변화 (절대값 기준):\n")[1] if "📊 주요 변화 (절대값 기준):\n" in comparison_result else "데이터를 분석할 수 없습니다."
        
        return result
    except Exception as e:
        logger.error(f"Error getting cost drivers: {e}")
        return f"비용 변화 원인 분석 중 오류가 발생했습니다: {str(e)}"

async def get_dimension_values(dimension: str = "SERVICE", start_date: str = "", end_date: str = "") -> str:
    """Get available dimension values."""
    try:
        if not start_date or not end_date:
            today = datetime.now()
            end_date = today.strftime('%Y-%m-%d')
            start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        
        response = cost_explorer.get_dimension_values(
            TimePeriod={'Start': start_date, 'End': end_date},
            Dimension=dimension.upper()
        )
        
        result = f"사용 가능한 {dimension} 값들 ({start_date} ~ {end_date}):\n\n"
        
        if 'DimensionValues' in response:
            for i, dim_value in enumerate(response['DimensionValues'][:20], 1):  # Top 20
                value = dim_value.get('Value', 'Unknown')
                attributes = dim_value.get('Attributes', {})
                result += f"{i:2d}. {value}\n"
                if attributes:
                    for key, attr_value in attributes.items():
                        result += f"     {key}: {attr_value}\n"
            
            if len(response['DimensionValues']) > 20:
                result += f"\n... 총 {len(response['DimensionValues'])}개 중 상위 20개만 표시"
        else:
            result += "사용 가능한 값이 없습니다."
        
        return result
    except Exception as e:
        logger.error(f"Error getting dimension values: {e}")
        return f"차원 값 조회 중 오류가 발생했습니다: {str(e)}"

async def get_today_date() -> str:
    """Get today's date information."""
    try:
        today = datetime.now()
        result = f"현재 날짜 정보:\n"
        result += f"📅 날짜: {today.strftime('%Y-%m-%d')}\n"
        result += f"🕐 시간: {today.strftime('%H:%M:%S')}\n"
        result += f"📆 요일: {today.strftime('%A')}\n"
        result += f"📊 월: {today.month}월\n"
        result += f"📈 년도: {today.year}년\n"
        
        # Add useful date ranges for cost analysis
        current_month_start = today.replace(day=1).strftime('%Y-%m-%d')
        last_month_start = (today.replace(day=1) - timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
        last_month_end = today.replace(day=1).strftime('%Y-%m-%d')
        
        result += f"\n💡 비용 분석용 날짜 범위:\n"
        result += f"   현재 월 시작: {current_month_start}\n"
        result += f"   지난 월: {last_month_start} ~ {last_month_end}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting today's date: {e}")
        return f"날짜 조회 중 오류가 발생했습니다: {str(e)}"

async def main():
    """Run the complete MCP server."""
    logger.info("🚀 Starting Complete MCP Server for AWS Cost Explorer...")
    logger.info("Available tools: 9 tools including comparisons and drivers analysis")
    
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
