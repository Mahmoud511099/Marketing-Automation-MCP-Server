# Marketing Automation MCP API Reference

## Overview

The Marketing Automation MCP server provides AI-powered tools for automating marketing workflows. This API reference covers all available MCP tools, their input/output schemas, and integration points.

## Table of Contents

1. [MCP Tools](#mcp-tools)
2. [API Integrations](#api-integrations)
3. [AI Engine](#ai-engine)
4. [Database Models](#database-models)
5. [Reporting](#reporting)
6. [Error Handling](#error-handling)

## MCP Tools

### 1. generate_campaign_report

Generates comprehensive performance reports from campaign data with visualizations and insights.

#### Input Schema

```python
{
    "campaign_ids": List[str],      # Required: List of campaign IDs
    "date_range": {                  # Required: Date range for report
        "start": str,                # ISO format date (YYYY-MM-DD)
        "end": str                   # ISO format date (YYYY-MM-DD)
    },
    "metrics": List[MetricType],     # Required: Metrics to include
    "format": ReportFormat,          # Optional: "json", "html", "pdf", "csv"
    "include_charts": bool,          # Optional: Include visualizations
    "include_insights": bool,        # Optional: Include AI insights
    "group_by": str                  # Optional: "campaign", "date", "platform"
}
```

#### Output Schema

```python
{
    "report_id": str,
    "generated_at": datetime,
    "format": ReportFormat,
    "campaigns": List[CampaignMetrics],
    "summary": {
        "total_impressions": int,
        "total_clicks": int,
        "total_conversions": int,
        "total_cost": float,
        "total_revenue": float,
        "average_ctr": float,
        "average_conversion_rate": float,
        "average_roi": float
    },
    "charts": Optional[Dict[str, str]],  # Base64 encoded chart images
    "insights": Optional[List[str]],
    "download_url": Optional[str]
}
```

#### Example Usage

```python
from mcp import Client

async with Client("marketing-automation") as client:
    result = await client.call_tool(
        "generate_campaign_report",
        {
            "campaign_ids": ["camp_001", "camp_002"],
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            },
            "metrics": ["impressions", "clicks", "conversions", "roi"],
            "format": "pdf",
            "include_charts": True
        }
    )
```

### 2. optimize_campaign_budget

Uses AI to analyze campaign performance and suggest optimal budget allocations.

#### Input Schema

```python
{
    "campaign_ids": List[str],            # Required: Campaigns to optimize
    "total_budget": float,                # Required: Total budget to allocate
    "optimization_goal": str,             # Required: "maximize_roi", "maximize_conversions", etc.
    "constraints": Dict[str, Dict],       # Optional: Min/max per campaign
    "historical_days": int,               # Optional: Days of data to analyze
    "include_projections": bool,          # Optional: Include performance projections
    "seasonality_adjustment": bool        # Optional: Account for seasonal trends
}
```

#### Output Schema

```python
{
    "optimization_id": str,
    "total_budget": float,
    "allocations": List[BudgetAllocation],
    "projected_improvement": {
        "roi_change": float,
        "conversion_change": float,
        "revenue_change": float
    },
    "recommendations": List[str],
    "confidence_score": float,
    "explanation": str
}
```

### 3. create_campaign_copy

Generates AI-powered marketing copy variants optimized for different platforms and audiences.

#### Input Schema

```python
{
    "product_name": str,                  # Required: Product/service name
    "product_description": str,           # Required: Product description
    "target_audience": str,               # Required: Target audience description
    "tone": ToneOfVoice,                 # Required: "professional", "casual", etc.
    "copy_type": str,                    # Required: "ad_headline", "email_body", etc.
    "variants_count": int,               # Optional: Number of variants (default: 3)
    "keywords": List[str],               # Optional: Keywords to include
    "call_to_action": str,               # Optional: CTA text
    "max_length": int,                   # Optional: Character limit
    "platform": str                      # Optional: Target platform
}
```

#### Output Schema

```python
{
    "copy_generation_id": str,
    "generated_at": datetime,
    "copy_type": str,
    "tone": ToneOfVoice,
    "variants": List[AdCopyVariant],
    "a_b_test_recommendations": List[str],
    "best_performer_index": int
}
```

### 4. analyze_audience_segments

Analyzes contact lists to identify high-value audience segments with AI-powered insights.

#### Input Schema

```python
{
    "contact_list_id": str,              # Required: Contact list identifier
    "criteria": List[SegmentCriteria],   # Required: Segmentation criteria
    "min_segment_size": int,             # Optional: Minimum contacts per segment
    "max_segments": int,                 # Optional: Maximum segments to create
    "include_recommendations": bool,      # Optional: Include campaign recommendations
    "analyze_overlap": bool,             # Optional: Analyze segment overlaps
    "custom_attributes": List[str]       # Optional: Custom attributes to consider
}
```

#### Output Schema

```python
{
    "analysis_id": str,
    "analyzed_at": datetime,
    "total_contacts": int,
    "segments": List[AudienceSegment],
    "overlaps": Optional[List[SegmentOverlap]],
    "recommendations": List[str],
    "insights": List[str],
    "value_distribution": Dict[str, float]
}
```

## API Integrations

### Google Ads Client

```python
from src.integrations.google_ads import GoogleAdsClient

client = GoogleAdsClient()
await client.connect()

# Fetch campaign performance
data = await client.fetch_campaign_performance(
    campaign_ids=["123456"],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
    metrics=["impressions", "clicks", "conversions", "cost"]
)

# Update campaign budget
result = await client.update_campaign_budget(
    campaign_id="123456",
    new_budget=5000.0,
    budget_type="daily"
)

# Pause campaign
await client.pause_campaign("123456")

# Start campaign
await client.start_campaign("123456")

# Get audience insights
insights = await client.get_audience_insights(campaign_id="123456")
```

### Facebook Ads Client

```python
from src.integrations.facebook_ads import FacebookAdsClient

client = FacebookAdsClient()
await client.connect()

# Similar methods as Google Ads
# Supports: fetch_campaign_performance, update_campaign_budget, 
# pause_campaign, start_campaign, get_audience_insights
```

### Google Analytics Client

```python
from src.integrations.google_analytics import GoogleAnalyticsClient

client = GoogleAnalyticsClient()
await client.connect()

# Fetch campaign performance (read-only)
data = await client.fetch_campaign_performance(
    campaign_ids=["utm_campaign_001"],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
    metrics=["sessions", "users", "conversions", "revenue"]
)
```

### Unified Marketing Client

```python
from src.integrations.unified_client import UnifiedMarketingClient, Platform

client = UnifiedMarketingClient()
await client.connect_all()

# Fetch from multiple platforms
result = await client.fetch_campaign_performance(
    campaign_ids=["g_001", "f_001"],
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    metrics=["clicks", "conversions"],
    platforms=[Platform.GOOGLE_ADS, Platform.FACEBOOK_ADS]
)

# Update across platforms
await client.update_campaign_budget(
    campaign_id="camp_001",
    new_budget=5000.0,
    platforms=[Platform.ALL]
)
```

## AI Engine

### Creating Prompt Chains

```python
from src.ai_engine import MarketingAIEngine

engine = MarketingAIEngine()

# Budget reallocation chain
result = await engine.create_budget_reallocation_chain(
    campaigns=[
        {"campaign_id": "001", "metrics": {"roi": 3.5}},
        {"campaign_id": "002", "metrics": {"roi": 2.1}}
    ],
    total_budget=10000,
    business_goals={"primary_goal": "maximize_roi"}
)

# Campaign analysis
analysis = await engine.analyze_campaign_performance(
    campaigns=campaign_data,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
    benchmarks={"ctr": 2.0, "conversion_rate": 3.0}
)

# Ad copy generation
variants = await engine.create_personalized_ad_copy(
    product_name="Marketing AI",
    product_description="Automate your marketing",
    target_audience={"role": "marketing manager"},
    platform="google_ads",
    num_variants=3,
    tone="professional"
)
```

## Database Models

### Campaign

```python
from src.database import Campaign

# Create campaign
campaign = Campaign(
    campaign_id="camp_001",
    name="Summer Sale",
    platform="google_ads",
    status="active",
    budget=10000.00,
    start_date=datetime.now()
)
```

### AutomationTask

```python
from src.database import AutomationTask, TaskType

# Track automation
task = AutomationTask(
    task_type=TaskType.BUDGET_OPTIMIZATION,
    task_name="Q4 Budget Reallocation",
    manual_duration_minutes=120,
    automated_duration_seconds=30,
    hourly_rate=75.0,
    campaign_id=campaign.id
)
```

### PerformanceMetrics

```python
from src.database import PerformanceMetrics

# Record metrics
metrics = PerformanceMetrics(
    campaign_id=campaign.id,
    date_recorded=datetime.now(),
    impressions=10000,
    clicks=200,
    conversions=10,
    revenue=1000.00,
    cost=200.00,
    is_automated=True,
    automation_applied=["bid_optimization"]
)
```

## Reporting

### Report Generator

```python
from src.reporting import ReportGenerator, ReportType

generator = ReportGenerator()

# Generate weekly summary
weekly_report = await generator.generate_weekly_summary(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 7),
    campaign_ids=["camp_001", "camp_002"],
    include_automation_metrics=True
)

# Generate optimization report
optimization_report = await generator.generate_optimization_report(
    campaign_id="camp_001",
    optimization_date=datetime.now(),
    changes_made={"budget": "+20%"},
    performance_comparison=True
)

# Generate ROI analysis
roi_report = await generator.generate_roi_analysis(
    period_start=datetime(2024, 1, 1),
    period_end=datetime(2024, 1, 31),
    include_projections=True
)

# Generate executive dashboard
dashboard = await generator.generate_executive_dashboard(
    date=datetime.now(),
    highlight_automation_impact=True
)
```

## Error Handling

### Rate Limit Errors

```python
from src.integrations.base import RateLimitError

try:
    await client.fetch_campaign_performance(...)
except RateLimitError as e:
    print(f"Rate limit hit: {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
    # Retry request
```

### Authentication Errors

```python
from src.integrations.base import AuthenticationError

try:
    await client.connect()
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    # Handle re-authentication
```

### Custom Error Types

```python
class CampaignNotFoundError(Exception):
    """Raised when campaign doesn't exist"""
    pass

class BudgetConstraintError(Exception):
    """Raised when budget constraints can't be satisfied"""
    pass

class InsufficientDataError(Exception):
    """Raised when not enough data for analysis"""
    pass
```

## Environment Variables

Required environment variables for each integration:

### Google Ads
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_CUSTOMER_ID`

### Facebook Ads
- `FACEBOOK_APP_ID`
- `FACEBOOK_APP_SECRET`
- `FACEBOOK_ACCESS_TOKEN`
- `FACEBOOK_AD_ACCOUNT_ID`

### Google Analytics
- `GOOGLE_ANALYTICS_PROPERTY_ID`
- `GOOGLE_ANALYTICS_CLIENT_ID`
- `GOOGLE_ANALYTICS_CLIENT_SECRET`
- `GOOGLE_ANALYTICS_REFRESH_TOKEN`

### OpenAI
- `OPENAI_API_KEY`

### Database
- `DATABASE_URL` (optional, defaults to sqlite:///marketing_automation.db)