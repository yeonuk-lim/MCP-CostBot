"""MCP Client for AWS Cost Explorer integration."""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import boto3
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class CostExplorerMCPClient:
    """MCP Client for AWS Cost Explorer operations."""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.cost_explorer = boto3.client('ce', region_name=region)
        self.session = None
        
    async def initialize(self):
        """Initialize the MCP client session."""
        try:
            # For now, we'll use direct AWS SDK calls instead of MCP server
            # This can be extended to use actual MCP server later
            logger.info("MCP Client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
    async def get_cost_and_usage(self, 
                                start_date: str, 
                                end_date: str, 
                                granularity: str = "MONTHLY",
                                metrics: List[str] = None,
                                group_by: List[Dict] = None) -> Dict[str, Any]:
        """Get cost and usage data from AWS Cost Explorer."""
        try:
            if metrics is None:
                metrics = ["BlendedCost"]
            
            params = {
                'TimePeriod': {
                    'Start': start_date,
                    'End': end_date
                },
                'Granularity': granularity,
                'Metrics': metrics
            }
            
            if group_by:
                params['GroupBy'] = group_by
            
            response = self.cost_explorer.get_cost_and_usage(**params)
            return response
            
        except Exception as e:
            logger.error(f"Error getting cost and usage data: {e}")
            return {"error": str(e)}
    
    async def get_dimension_values(self, 
                                  dimension: str, 
                                  start_date: str, 
                                  end_date: str) -> Dict[str, Any]:
        """Get dimension values from AWS Cost Explorer."""
        try:
            response = self.cost_explorer.get_dimension_values(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Dimension=dimension
            )
            return response
            
        except Exception as e:
            logger.error(f"Error getting dimension values: {e}")
            return {"error": str(e)}
    
    async def get_cost_forecast(self, 
                               start_date: str, 
                               end_date: str, 
                               metric: str = "BLENDED_COST") -> Dict[str, Any]:
        """Get cost forecast from AWS Cost Explorer."""
        try:
            response = self.cost_explorer.get_cost_forecast(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Metric=metric,
                Granularity='MONTHLY'
            )
            return response
            
        except Exception as e:
            logger.error(f"Error getting cost forecast: {e}")
            return {"error": str(e)}
    
    def get_last_n_months_dates(self, n: int = 3) -> tuple:
        """Get start and end dates for the last N months."""
        today = datetime.now()
        # Get the first day of current month
        current_month_start = today.replace(day=1)
        # Get the first day of N months ago
        start_date = (current_month_start - timedelta(days=32*n)).replace(day=1)
        
        return start_date.strftime('%Y-%m-%d'), current_month_start.strftime('%Y-%m-%d')
    
    def get_current_month_dates(self) -> tuple:
        """Get start and end dates for the current month."""
        today = datetime.now()
        start_date = today.replace(day=1)
        # Next month's first day
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    async def close(self):
        """Close the MCP client session."""
        if self.session:
            await self.session.close()
            logger.info("MCP Client session closed")
