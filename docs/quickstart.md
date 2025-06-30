# Marketing Automation MCP - Quick Start Guide

Welcome to the Marketing Automation MCP server! This guide will help you get up and running with automated marketing workflows in under 30 minutes.

## Prerequisites

- Python 3.8 or higher
- API credentials for at least one platform (Google Ads, Facebook Ads, or Google Analytics)
- OpenAI API key for AI-powered features
- Basic understanding of marketing concepts

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/marketing-automation-mcp.git
cd marketing-automation-mcp
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Google Ads Configuration (Optional)
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id

# Facebook Ads Configuration (Optional)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_AD_ACCOUNT_ID=your_ad_account_id

# Google Analytics Configuration (Optional)
GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id
GOOGLE_ANALYTICS_CLIENT_ID=your_client_id
GOOGLE_ANALYTICS_CLIENT_SECRET=your_client_secret
GOOGLE_ANALYTICS_REFRESH_TOKEN=your_refresh_token

# Database Configuration (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///marketing_automation.db
```

## Quick Start Tutorial

### Step 1: Start the MCP Server

```bash
python -m src.server
```

You should see:
```
Marketing Automation MCP Server started
Listening on stdio...
```

### Step 2: Your First Automation - Campaign Report

Let's generate a performance report for your campaigns:

```python
import asyncio
from mcp import Client

async def generate_first_report():
    async with Client("marketing-automation") as client:
        # Generate a campaign report
        result = await client.call_tool(
            "generate_campaign_report",
            {
                "campaign_ids": ["camp_001", "camp_002"],  # Replace with your campaign IDs
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-01-31"
                },
                "metrics": ["impressions", "clicks", "conversions", "roi"],
                "format": "html",
                "include_charts": True
            }
        )
        
        print(f"Report generated successfully!")
        print(f"Report ID: {result['report_id']}")
        print(f"Summary: {result['summary']}")
        
        # Save the report
        if result.get('download_url'):
            print(f"Download your report: {result['download_url']}")

# Run the automation
asyncio.run(generate_first_report())
```

### Step 3: Optimize Campaign Budgets

Now let's use AI to optimize your campaign budgets:

```python
async def optimize_budgets():
    async with Client("marketing-automation") as client:
        # First, get campaign IDs from the report
        report = await client.call_tool(
            "generate_campaign_report",
            {
                "campaign_ids": ["camp_001", "camp_002", "camp_003"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                "metrics": ["cost", "conversions", "roi"],
                "format": "json"
            }
        )
        
        # Extract campaign IDs
        campaign_ids = [c['campaign_id'] for c in report['campaigns']]
        total_budget = sum(c['cost'] for c in report['campaigns'])
        
        # Optimize budget allocation
        optimization = await client.call_tool(
            "optimize_campaign_budget",
            {
                "campaign_ids": campaign_ids,
                "total_budget": total_budget * 1.1,  # 10% budget increase
                "optimization_goal": "maximize_roi",
                "include_projections": True
            }
        )
        
        print("\n🎯 Budget Optimization Results:")
        print(f"Confidence Score: {optimization['confidence_score']:.1%}")
        print(f"Projected ROI Improvement: {optimization['projected_improvement']['roi_change']:.1f}%")
        
        print("\n💰 Recommended Budget Allocations:")
        for allocation in optimization['allocations']:
            print(f"  {allocation['campaign_id']}: "
                  f"${allocation['current_budget']:.2f} → "
                  f"${allocation['recommended_budget']:.2f} "
                  f"({allocation['change_percentage']:+.1f}%)")

asyncio.run(optimize_budgets())
```

### Step 4: Create AI-Powered Ad Copy

Generate personalized ad copy for your campaigns:

```python
async def create_ad_copy():
    async with Client("marketing-automation") as client:
        result = await client.call_tool(
            "create_campaign_copy",
            {
                "product_name": "Marketing Automation Platform",
                "product_description": "Save 10+ hours per week with AI-powered marketing automation",
                "target_audience": "Marketing managers at B2B SaaS companies",
                "tone": "professional",
                "copy_type": "ad_headline",
                "variants_count": 3,
                "keywords": ["automation", "AI", "marketing", "efficiency"],
                "max_length": 30  # Google Ads headline limit
            }
        )
        
        print("🎨 Generated Ad Copy Variants:")
        for i, variant in enumerate(result['variants'], 1):
            print(f"\nVariant {i}:")
            print(f"  Headline: {variant['headline']}")
            print(f"  Description: {variant['description']}")
            print(f"  Predicted CTR: {variant['predicted_ctr']:.1f}%")
            print(f"  Keywords: {', '.join(variant['keywords'])}")
        
        print(f"\n⭐ Recommended variant: #{result['best_performer_index'] + 1}")

asyncio.run(create_ad_copy())
```

### Step 5: Analyze Audience Segments

Identify high-value audience segments:

```python
async def analyze_audiences():
    async with Client("marketing-automation") as client:
        result = await client.call_tool(
            "analyze_audience_segments",
            {
                "contact_list_id": "main_database",
                "criteria": ["demographics", "behavior", "engagement"],
                "min_segment_size": 100,
                "max_segments": 5,
                "include_recommendations": True
            }
        )
        
        print("👥 Audience Segmentation Results:")
        print(f"Total Contacts Analyzed: {result['total_contacts']}")
        print(f"Segments Identified: {len(result['segments'])}")
        
        print("\n📊 Top Segments:")
        for segment in result['segments'][:3]:
            print(f"\n{segment['name']}:")
            print(f"  Size: {segment['size']} contacts")
            print(f"  Value Score: {segment['value_score']}/100")
            print(f"  Engagement Score: {segment['engagement_score']}/100")
            print(f"  Recommended Campaigns: {', '.join(segment['recommended_campaigns'])}")
        
        print("\n💡 AI Insights:")
        for insight in result['insights'][:3]:
            print(f"  • {insight}")

asyncio.run(analyze_audiences())
```

## Complete Automation Workflow

Here's a complete example that combines all tools:

```python
import asyncio
from datetime import datetime, timedelta
from mcp import Client

async def complete_marketing_automation():
    """Complete marketing automation workflow"""
    
    async with Client("marketing-automation") as client:
        print("🚀 Starting Marketing Automation Workflow")
        print("=" * 50)
        
        # Step 1: Analyze Current Performance
        print("\n📊 Step 1: Analyzing Campaign Performance...")
        
        report = await client.call_tool(
            "generate_campaign_report",
            {
                "campaign_ids": ["camp_001", "camp_002", "camp_003"],
                "date_range": {
                    "start": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end": datetime.now().strftime("%Y-%m-%d")
                },
                "metrics": ["impressions", "clicks", "conversions", "cost", "revenue", "roi"],
                "format": "json",
                "include_insights": True
            }
        )
        
        print(f"✓ Current Average ROI: {report['summary']['average_roi']:.1f}%")
        print(f"✓ Total Conversions: {report['summary']['total_conversions']}")
        
        # Step 2: Optimize Budget Allocation
        print("\n💰 Step 2: Optimizing Budget Allocation...")
        
        campaign_ids = [c['campaign_id'] for c in report['campaigns']]
        current_budget = sum(c['cost'] for c in report['campaigns'])
        
        optimization = await client.call_tool(
            "optimize_campaign_budget",
            {
                "campaign_ids": campaign_ids,
                "total_budget": current_budget,
                "optimization_goal": "maximize_roi",
                "include_projections": True
            }
        )
        
        print(f"✓ Optimization Confidence: {optimization['confidence_score']:.1%}")
        print(f"✓ Projected ROI Improvement: +{optimization['projected_improvement']['roi_change']:.1f}%")
        
        # Step 3: Analyze Audience for Better Targeting
        print("\n👥 Step 3: Analyzing Audience Segments...")
        
        segments = await client.call_tool(
            "analyze_audience_segments",
            {
                "contact_list_id": "main_database",
                "criteria": ["demographics", "behavior"],
                "min_segment_size": 100,
                "max_segments": 3,
                "include_recommendations": True
            }
        )
        
        print(f"✓ Identified {len(segments['segments'])} high-value segments")
        top_segment = segments['segments'][0]
        print(f"✓ Top segment: {top_segment['name']} ({top_segment['size']} contacts)")
        
        # Step 4: Create Targeted Ad Copy
        print("\n✍️ Step 4: Creating Personalized Ad Copy...")
        
        ad_copy = await client.call_tool(
            "create_campaign_copy",
            {
                "product_name": "Your Product",
                "product_description": "Transform your marketing with AI",
                "target_audience": top_segment['description'],
                "tone": "professional",
                "copy_type": "ad_creative",
                "variants_count": 2,
                "keywords": ["automation", "efficiency", "ROI"]
            }
        )
        
        best_variant = ad_copy['variants'][ad_copy['best_performer_index']]
        print(f"✓ Created {len(ad_copy['variants'])} ad variants")
        print(f"✓ Best variant predicted CTR: {best_variant['predicted_ctr']:.1f}%")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 AUTOMATION COMPLETE!")
        print("=" * 50)
        
        print("\n📈 Results Summary:")
        print(f"  • Campaigns Analyzed: {len(campaign_ids)}")
        print(f"  • Budget Optimized: ${current_budget:,.2f}")
        print(f"  • Expected ROI Improvement: {optimization['projected_improvement']['roi_change']:.1f}%")
        print(f"  • Audience Segments: {len(segments['segments'])}")
        print(f"  • Ad Variants Created: {len(ad_copy['variants'])}")
        
        print("\n🎬 Next Steps:")
        print("  1. Review and apply budget recommendations")
        print("  2. Launch campaigns targeting identified segments")
        print("  3. A/B test the generated ad copy")
        print("  4. Monitor performance and iterate")
        
        return {
            'report': report,
            'optimization': optimization,
            'segments': segments,
            'ad_copy': ad_copy
        }

# Run the complete workflow
if __name__ == "__main__":
    results = asyncio.run(complete_marketing_automation())
    print("\n✅ Workflow completed successfully!")
```

## Integration with Existing Systems

### Using with MCP Clients

The Marketing Automation MCP server works with any MCP-compatible client:

```python
# With the official MCP Python SDK
from mcp import Client

async with Client("marketing-automation") as client:
    # Use any of the four tools
    result = await client.call_tool("tool_name", parameters)
```

### Direct API Integration

You can also use the individual components directly:

```python
from src.integrations.unified_client import UnifiedMarketingClient, Platform
from src.ai_engine import MarketingAIEngine
from src.reporting import ReportGenerator

# Initialize components
unified_client = UnifiedMarketingClient()
ai_engine = MarketingAIEngine()
report_gen = ReportGenerator()

# Use them in your workflows
await unified_client.connect_all()
data = await unified_client.fetch_campaign_performance(...)
```

## Monitoring and Tracking

### ROI Tracking

All automation tasks are automatically tracked for ROI calculation:

```python
from src.database_utils import AutomationTracker, TaskType

async with AutomationTracker(
    task_type=TaskType.BUDGET_OPTIMIZATION,
    task_name="Weekly Budget Review",
    manual_duration_minutes=120,
    hourly_rate=75.0
) as tracker:
    # Your automation code here
    await optimize_campaigns()
    
    # Metrics are automatically calculated
    print(f"Time saved: {tracker.time_saved_minutes} minutes")
    print(f"Cost saved: ${tracker.cost_saved}")
```

### Database Queries

Access historical data and ROI metrics:

```python
from src.database import DatabaseManager

db = DatabaseManager()

# Get ROI for a period
roi = db.calculate_period_roi(
    period_start=datetime(2024, 1, 1),
    period_end=datetime(2024, 1, 31)
)

print(f"Total time saved: {roi.total_time_saved_hours} hours")
print(f"Total cost saved: ${roi.labor_cost_saved:,.2f}")
print(f"Average performance improvement: {roi.avg_performance_improvement:.1f}%")
```

## Best Practices

### 1. Start Small
- Begin with one platform and one campaign
- Test with conservative budget changes (5-10%)
- Monitor results before scaling

### 2. Use Automation Tracking
- Always wrap automated tasks with `AutomationTracker`
- Set realistic manual duration estimates
- Track all automation touchpoints

### 3. Validate AI Recommendations
- Review AI suggestions before implementing
- Start with high-confidence recommendations (>80%)
- A/B test generated content

### 4. Regular Monitoring
- Check automation logs daily
- Review ROI reports weekly
- Adjust strategies based on data

## Troubleshooting

### Common Issues

1. **"No campaigns found"**
   - Verify campaign IDs are correct
   - Check API credentials
   - Ensure date range contains data

2. **"Rate limit exceeded"**
   - Implement exponential backoff
   - Reduce request frequency
   - Use batch operations

3. **"Authentication failed"**
   - Verify environment variables
   - Check token expiration
   - Refresh OAuth tokens

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Explore Advanced Features**
   - Read the [API Reference](./api/README.md)
   - Review [Example Workflows](./examples/README.md)
   - Understand [ROI Methodology](./guides/roi-methodology.md)

2. **Customize for Your Needs**
   - Add custom integrations
   - Create specialized workflows
   - Extend AI capabilities

3. **Scale Your Automation**
   - Connect additional platforms
   - Automate more campaign types
   - Build scheduled workflows

## Support

- **Documentation**: Full docs in the `/docs` directory
- **Examples**: Working examples in `/docs/examples`
- **Tests**: Comprehensive tests in `/tests`
- **Issues**: Report bugs on GitHub

Happy automating! 🚀