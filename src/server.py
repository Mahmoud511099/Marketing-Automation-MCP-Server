"""Marketing Automation MCP Server Implementation"""

import asyncio
import logging
from typing import Any, Dict, List
import json

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .models import (
    GenerateCampaignReportInput,
    OptimizeCampaignBudgetInput,
    CreateCampaignCopyInput,
    AnalyzeAudienceSegmentsInput
)
from .tools.marketing_tools import (
    generate_campaign_report,
    optimize_campaign_budget,
    create_campaign_copy,
    analyze_audience_segments
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketingAutomationServer:
    def __init__(self):
        self.server = Server("marketing-automation")
        self._setup_handlers()
        
    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available marketing automation tools"""
            return [
                Tool(
                    name="generate_campaign_report",
                    description="Generate comprehensive performance reports from campaign data with visualizations and insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of campaign IDs to include in report"
                            },
                            "date_range": {
                                "type": "object",
                                "properties": {
                                    "start": {"type": "string", "description": "Start date (ISO format)"},
                                    "end": {"type": "string", "description": "End date (ISO format)"}
                                },
                                "required": ["start", "end"],
                                "description": "Date range for the report"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["opens", "clicks", "conversions", "revenue", "ctr", "conversion_rate", "roi", "engagement_rate"]
                                },
                                "description": "Metrics to include in the report"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["pdf", "html", "json", "csv"],
                                "default": "json",
                                "description": "Output format for the report"
                            },
                            "include_charts": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include visual charts"
                            },
                            "group_by": {
                                "type": "string",
                                "enum": ["day", "week", "month", "campaign"],
                                "description": "Group results by time period or campaign"
                            }
                        },
                        "required": ["campaign_ids", "date_range", "metrics"]
                    }
                ),
                Tool(
                    name="optimize_campaign_budget",
                    description="Use AI to analyze campaign performance and suggest optimal budget reallocations to maximize ROI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Campaign IDs to optimize"
                            },
                            "total_budget": {
                                "type": "number",
                                "minimum": 0,
                                "description": "Total budget to allocate across campaigns"
                            },
                            "optimization_goal": {
                                "type": "string",
                                "enum": ["maximize_conversions", "maximize_roi", "maximize_reach"],
                                "description": "Primary optimization objective"
                            },
                            "constraints": {
                                "type": "object",
                                "description": "Min/max budget constraints per campaign"
                            },
                            "historical_days": {
                                "type": "integer",
                                "minimum": 7,
                                "default": 30,
                                "description": "Days of historical data to analyze"
                            },
                            "include_projections": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include performance projections"
                            }
                        },
                        "required": ["campaign_ids", "total_budget", "optimization_goal"]
                    }
                ),
                Tool(
                    name="create_campaign_copy",
                    description="Generate multiple marketing copy variants using AI, optimized for different channels and audiences",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "Name of the product or service"
                            },
                            "product_description": {
                                "type": "string",
                                "description": "Description of the product or service"
                            },
                            "target_audience": {
                                "type": "string",
                                "description": "Target audience description"
                            },
                            "tone": {
                                "type": "string",
                                "enum": ["professional", "casual", "friendly", "urgent", "informative", "persuasive"],
                                "description": "Desired tone of voice"
                            },
                            "copy_type": {
                                "type": "string",
                                "enum": ["email_subject", "email_body", "ad_headline", "ad_copy", "social_post"],
                                "description": "Type of marketing copy to generate"
                            },
                            "variants_count": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                                "default": 3,
                                "description": "Number of copy variants to generate"
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords to include in the copy"
                            },
                            "max_length": {
                                "type": "integer",
                                "description": "Maximum character or word count"
                            },
                            "call_to_action": {
                                "type": "string",
                                "description": "Specific call-to-action to include"
                            }
                        },
                        "required": ["product_name", "product_description", "target_audience", "tone", "copy_type"]
                    }
                ),
                Tool(
                    name="analyze_audience_segments",
                    description="Analyze contact data to identify high-value audience segments and provide targeting recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contact_list_id": {
                                "type": "string",
                                "description": "ID of the contact list to analyze"
                            },
                            "criteria": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["demographics", "behavior", "engagement", "purchase_history", "interests", "location"]
                                },
                                "description": "Criteria to use for segmentation"
                            },
                            "min_segment_size": {
                                "type": "integer",
                                "minimum": 10,
                                "default": 100,
                                "description": "Minimum contacts per segment"
                            },
                            "max_segments": {
                                "type": "integer",
                                "minimum": 2,
                                "maximum": 20,
                                "default": 10,
                                "description": "Maximum number of segments to create"
                            },
                            "include_recommendations": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include targeting recommendations"
                            },
                            "analyze_overlap": {
                                "type": "boolean",
                                "default": True,
                                "description": "Analyze overlap between segments"
                            }
                        },
                        "required": ["contact_list_id", "criteria"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a marketing automation tool"""
            try:
                if name == "generate_campaign_report":
                    # Validate input
                    input_data = GenerateCampaignReportInput(**arguments)
                    result = await generate_campaign_report(input_data)
                    
                elif name == "optimize_campaign_budget":
                    # Validate input
                    input_data = OptimizeCampaignBudgetInput(**arguments)
                    result = await optimize_campaign_budget(input_data)
                    
                elif name == "create_campaign_copy":
                    # Validate input
                    input_data = CreateCampaignCopyInput(**arguments)
                    result = await create_campaign_copy(input_data)
                    
                elif name == "analyze_audience_segments":
                    # Validate input
                    input_data = AnalyzeAudienceSegmentsInput(**arguments)
                    result = await analyze_audience_segments(input_data)
                    
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Convert result to JSON string for MCP response
                result_str = json.dumps(result.dict() if hasattr(result, 'dict') else result, default=str, indent=2)
                return [TextContent(type="text", text=result_str)]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                error_response = {"error": str(e), "tool": name}
                return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="marketing-automation",
                    server_version="1.0.0"
                )
            )


async def main():
    """Main entry point"""
    server = MarketingAutomationServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())