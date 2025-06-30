# Marketing Automation Workflows - Examples

This guide provides practical examples of marketing automation workflows using the MCP server. Each example includes complete code and explanations.

## Table of Contents

1. [Basic Campaign Optimization](#basic-campaign-optimization)
2. [Multi-Platform Campaign Management](#multi-platform-campaign-management)
3. [AI-Driven Budget Reallocation](#ai-driven-budget-reallocation)
4. [Automated Reporting Pipeline](#automated-reporting-pipeline)
5. [Audience Segmentation and Targeting](#audience-segmentation-and-targeting)
6. [Complete Marketing Automation Cycle](#complete-marketing-automation-cycle)

## Basic Campaign Optimization

### Scenario
You have multiple Google Ads campaigns and want to optimize their budgets based on performance.

```python
import asyncio
from datetime import datetime, timedelta
from mcp import Client

async def optimize_campaigns():
    """Basic campaign optimization workflow"""
    
    async with Client("marketing-automation") as client:
        # Step 1: Generate performance report
        report_result = await client.call_tool(
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
        
        print(f"Report generated: {report_result['report_id']}")
        print(f"Total ROI: {report_result['summary']['average_roi']}%")
        
        # Step 2: Optimize budget allocation
        campaign_ids = [c['campaign_id'] for c in report_result['campaigns']]
        
        optimization_result = await client.call_tool(
            "optimize_campaign_budget",
            {
                "campaign_ids": campaign_ids,
                "total_budget": 10000.0,
                "optimization_goal": "maximize_roi",
                "historical_days": 30,
                "include_projections": True
            }
        )
        
        print(f"\nOptimization complete: {optimization_result['optimization_id']}")
        print(f"Projected ROI improvement: {optimization_result['projected_improvement']['roi_change']}%")
        
        # Step 3: Review and apply recommendations
        for allocation in optimization_result['allocations']:
            print(f"\nCampaign: {allocation['campaign_id']}")
            print(f"Current budget: ${allocation['current_budget']}")
            print(f"Recommended budget: ${allocation['recommended_budget']}")
            print(f"Change: {allocation['change_percentage']}%")
        
        return optimization_result

# Run the optimization
if __name__ == "__main__":
    asyncio.run(optimize_campaigns())
```

## Multi-Platform Campaign Management

### Scenario
Manage campaigns across Google Ads, Facebook Ads, and track performance in Google Analytics.

```python
import asyncio
from datetime import datetime, timedelta
from src.integrations.unified_client import UnifiedMarketingClient, Platform

async def multi_platform_workflow():
    """Manage campaigns across multiple platforms"""
    
    client = UnifiedMarketingClient()
    
    # Connect to all platforms
    connection_status = await client.connect_all()
    print("Connected platforms:", connection_status['connected'])
    
    # Step 1: Fetch performance data from all platforms
    performance_data = await client.fetch_campaign_performance(
        campaign_ids=["g_summer_2024", "f_summer_2024", "ga_summer"],
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        metrics=["impressions", "clicks", "conversions", "cost", "revenue"],
        platforms=[Platform.ALL]
    )
    
    print("\nCross-platform performance summary:")
    print(f"Total impressions: {performance_data['summary']['combined_metrics']['impressions']}")
    print(f"Total conversions: {performance_data['summary']['combined_metrics']['conversions']}")
    print(f"Overall CTR: {performance_data['summary']['combined_metrics']['ctr']}%")
    
    # Step 2: Identify underperforming campaigns
    underperformers = []
    for platform, data in performance_data['results'].items():
        for campaign in data.get('data', []):
            if campaign['metrics'].get('ctr', 0) < 1.5:  # CTR below 1.5%
                underperformers.append({
                    'platform': platform,
                    'campaign_id': campaign['campaign_id'],
                    'ctr': campaign['metrics']['ctr']
                })
    
    # Step 3: Pause underperforming campaigns
    for campaign in underperformers:
        result = await client.pause_campaign(
            campaign_id=campaign['campaign_id'],
            platforms=[Platform[campaign['platform'].upper()]]
        )
        print(f"\nPaused {campaign['campaign_id']} on {campaign['platform']}")
    
    # Step 4: Reallocate budget to top performers
    top_performer = max(
        [(p, c) for p, d in performance_data['results'].items() 
         for c in d.get('data', [])],
        key=lambda x: x[1]['metrics'].get('roi', 0)
    )
    
    platform, campaign = top_performer
    new_budget = campaign['metrics']['cost'] * 1.5  # 50% increase
    
    budget_result = await client.update_campaign_budget(
        campaign_id=campaign['campaign_id'],
        new_budget=new_budget,
        platforms=[Platform[platform.upper()]]
    )
    
    print(f"\nIncreased budget for top performer {campaign['campaign_id']} to ${new_budget}")
    
    return performance_data

# Run multi-platform management
if __name__ == "__main__":
    asyncio.run(multi_platform_workflow())
```

## AI-Driven Budget Reallocation

### Scenario
Use AI to analyze campaign performance trends and automatically reallocate budgets for optimal results.

```python
import asyncio
from datetime import datetime, timedelta
from src.ai_engine import MarketingAIEngine
from src.database_utils import AutomationTracker, TaskType
from src.integrations.google_ads import GoogleAdsClient

async def ai_budget_reallocation():
    """AI-driven budget reallocation workflow"""
    
    ai_engine = MarketingAIEngine()
    google_ads = GoogleAdsClient()
    await google_ads.connect()
    
    # Step 1: Fetch campaign data
    campaigns_data = await google_ads.fetch_campaign_performance(
        campaign_ids=["camp_001", "camp_002", "camp_003", "camp_004"],
        start_date=datetime.now() - timedelta(days=60),
        end_date=datetime.now(),
        metrics=["impressions", "clicks", "conversions", "cost", "revenue"]
    )
    
    # Step 2: Analyze with AI
    async with AutomationTracker(
        task_type=TaskType.BUDGET_OPTIMIZATION,
        task_name="AI Budget Reallocation Q4 2024",
        manual_duration_minutes=180,  # 3 hours manual work
        hourly_rate=100.0
    ) as tracker:
        
        # Prepare campaign data for AI
        campaign_list = []
        for campaign in campaigns_data['data']:
            metrics = campaign['metrics']
            campaign_list.append({
                "campaign_id": campaign['campaign_id'],
                "campaign_name": campaign['campaign_name'],
                "metrics": {
                    "impressions": metrics['impressions'],
                    "clicks": metrics['clicks'],
                    "conversions": metrics['conversions'],
                    "cost": metrics['cost'],
                    "revenue": metrics['revenue'],
                    "roi": (metrics['revenue'] - metrics['cost']) / metrics['cost'] * 100,
                    "ctr": metrics['clicks'] / metrics['impressions'] * 100,
                    "conversion_rate": metrics['conversions'] / metrics['clicks'] * 100
                }
            })
        
        # Create AI-driven budget reallocation chain
        total_budget = sum(c['metrics']['cost'] for c in campaign_list)
        
        chain_result = await ai_engine.create_budget_reallocation_chain(
            campaigns=campaign_list,
            total_budget=total_budget * 1.1,  # 10% budget increase
            business_goals={
                "primary_goal": "maximize_roi",
                "secondary_goals": ["increase_conversions", "maintain_market_share"],
                "constraints": {
                    "min_budget_per_campaign": 500,
                    "max_budget_change": 0.5  # Max 50% change
                }
            }
        )
        
        tracker.set_result("campaigns_analyzed", len(campaign_list))
        tracker.set_result("optimization_confidence", chain_result['final_confidence'])
        
        # Step 3: Extract and apply recommendations
        optimization_step = next(
            s for s in chain_result['steps'] 
            if s['step_name'] == 'optimization'
        )
        
        suggestions = optimization_step['result']['suggestions']
        
        print("\nAI Budget Recommendations:")
        print("=" * 50)
        
        for suggestion in suggestions:
            print(f"\nCampaign: {suggestion['campaign_id']}")
            print(f"Action: {suggestion['action']}")
            print(f"Confidence: {suggestion['confidence'] * 100}%")
            print(f"Reasoning: {suggestion['reasoning']}")
            print(f"Expected ROI change: {suggestion['predicted_impact']['roi_change']}%")
            
            # Apply the budget change
            if suggestion['confidence'] > 0.8:  # High confidence threshold
                # Extract new budget from action string
                import re
                budget_match = re.search(r'\$?([\d,]+)', suggestion['action'])
                if budget_match:
                    new_budget = float(budget_match.group(1).replace(',', ''))
                    
                    result = await google_ads.update_campaign_budget(
                        campaign_id=suggestion['campaign_id'],
                        new_budget=new_budget,
                        budget_type="daily"
                    )
                    
                    print(f"✓ Applied: Budget updated to ${new_budget}")
                    tracker.increment_items(1)
        
        # Step 4: Record expected impact
        expected_impact = optimization_step['result']['expected_overall_impact']
        tracker.set_result("expected_roi_improvement", expected_impact['total_roi'])
        tracker.set_result("expected_conversion_increase", expected_impact['total_conversions'])
    
    print(f"\n✅ Automation completed in {tracker.automated_duration_seconds} seconds")
    print(f"⏱️  Time saved: {tracker.time_saved_minutes} minutes")
    print(f"💰 Cost saved: ${tracker.cost_saved}")
    
    return chain_result

# Run AI budget reallocation
if __name__ == "__main__":
    asyncio.run(ai_budget_reallocation())
```

## Automated Reporting Pipeline

### Scenario
Create a weekly automated reporting pipeline that generates and distributes performance reports.

```python
import asyncio
from datetime import datetime, timedelta
from src.reporting import ReportGenerator, ReportType
from src.database import DatabaseManager
from src.database_utils import AutomationTracker, TaskType
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

async def weekly_reporting_pipeline():
    """Automated weekly reporting workflow"""
    
    db = DatabaseManager()
    report_gen = ReportGenerator()
    
    # Define report parameters
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    async with AutomationTracker(
        task_type=TaskType.REPORT_GENERATION,
        task_name="Weekly Executive Report",
        manual_duration_minutes=240,  # 4 hours manual work
        hourly_rate=75.0
    ) as tracker:
        
        # Step 1: Generate multiple report types
        reports = {}
        
        # Weekly Performance Summary
        print("Generating weekly performance summary...")
        reports['weekly_summary'] = await report_gen.generate_weekly_summary(
            start_date=start_date,
            end_date=end_date,
            campaign_ids=None,  # All campaigns
            include_automation_metrics=True
        )
        tracker.set_result("weekly_summary_pages", 5)
        
        # ROI Analysis
        print("Generating ROI analysis...")
        reports['roi_analysis'] = await report_gen.generate_roi_analysis(
            period_start=start_date,
            period_end=end_date,
            include_projections=True
        )
        tracker.set_result("roi_charts_created", 8)
        
        # Executive Dashboard
        print("Generating executive dashboard...")
        reports['executive_dashboard'] = await report_gen.generate_executive_dashboard(
            date=end_date,
            highlight_automation_impact=True
        )
        tracker.set_result("dashboard_metrics", 12)
        
        # Step 2: Compile insights
        key_insights = []
        
        # Analyze automation impact
        roi_tracking = db.calculate_period_roi(
            period_start=start_date,
            period_end=end_date
        )
        
        if roi_tracking:
            key_insights.append(
                f"🚀 Automation saved {roi_tracking.total_time_saved_hours:.1f} hours "
                f"and ${roi_tracking.labor_cost_saved:,.2f} this week"
            )
            
            if roi_tracking.avg_performance_improvement:
                key_insights.append(
                    f"📈 Automated campaigns showed {roi_tracking.avg_performance_improvement:.1f}% "
                    f"better performance"
                )
        
        # Step 3: Create combined report
        combined_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weekly Marketing Report - {end_date.strftime('%B %d, %Y')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; }}
                .insights {{ background: #ecf0f1; padding: 15px; margin: 20px 0; }}
                .section {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Weekly Marketing Performance Report</h1>
                <p>{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="insights">
                <h2>🎯 Key Insights</h2>
                <ul>
                    {''.join(f'<li>{insight}</li>' for insight in key_insights)}
                </ul>
            </div>
            
            <div class="section">
                {reports['weekly_summary']['html_content']}
            </div>
            
            <div class="section">
                {reports['roi_analysis']['html_content']}
            </div>
            
            <div class="section">
                {reports['executive_dashboard']['html_content']}
            </div>
        </body>
        </html>
        """
        
        # Step 4: Save reports
        report_path = f"reports/weekly_report_{end_date.strftime('%Y%m%d')}.html"
        with open(report_path, 'w') as f:
            f.write(combined_html)
        
        pdf_path = await report_gen._generate_pdf(combined_html)
        
        tracker.set_result("report_pages", 15)
        tracker.set_result("recipients", 5)
        tracker.increment_items(1)
        
        # Step 5: Distribute reports (example with email)
        await distribute_report(pdf_path, key_insights)
        
        print(f"\n✅ Report generation completed")
        print(f"📄 HTML saved to: {report_path}")
        print(f"📑 PDF saved to: {pdf_path}")
    
    return reports

async def distribute_report(pdf_path: str, insights: list):
    """Distribute report via email"""
    # This is a placeholder - implement actual email sending
    print("\n📧 Report distribution:")
    print("- CEO: ceo@company.com")
    print("- CMO: cmo@company.com")
    print("- Marketing Team: marketing@company.com")
    print("\nKey insights shared:")
    for insight in insights:
        print(f"  {insight}")

# Run weekly reporting
if __name__ == "__main__":
    asyncio.run(weekly_reporting_pipeline())
```

## Audience Segmentation and Targeting

### Scenario
Analyze your contact database to identify high-value segments and create targeted campaigns.

```python
import asyncio
from mcp import Client
from src.database_utils import track_campaign_optimization

async def audience_segmentation_workflow():
    """Audience segmentation and targeted campaign creation"""
    
    async with Client("marketing-automation") as client:
        # Step 1: Analyze audience segments
        segmentation_result = await client.call_tool(
            "analyze_audience_segments",
            {
                "contact_list_id": "main_contact_db",
                "criteria": ["demographics", "behavior", "purchase_history", "engagement"],
                "min_segment_size": 500,
                "max_segments": 6,
                "include_recommendations": True,
                "analyze_overlap": True,
                "custom_attributes": ["lifetime_value", "product_preferences"]
            }
        )
        
        print(f"Analysis complete: {segmentation_result['analysis_id']}")
        print(f"Total contacts analyzed: {segmentation_result['total_contacts']}")
        print(f"Segments identified: {len(segmentation_result['segments'])}")
        
        # Step 2: Review segments
        high_value_segments = []
        
        for segment in segmentation_result['segments']:
            print(f"\n📊 Segment: {segment['name']}")
            print(f"   Size: {segment['size']} contacts")
            print(f"   Engagement Score: {segment['engagement_score']}/100")
            print(f"   Value Score: {segment['value_score']}/100")
            print(f"   Characteristics: {', '.join(segment['characteristics'])}")
            
            # Identify high-value segments
            if segment['value_score'] > 70 and segment['engagement_score'] > 60:
                high_value_segments.append(segment)
        
        # Step 3: Check segment overlaps
        if segmentation_result.get('overlaps'):
            print("\n🔄 Segment Overlaps:")
            for overlap in segmentation_result['overlaps']:
                if overlap['overlap_percentage'] > 20:
                    print(f"   {overlap['segment_a_name']} ∩ {overlap['segment_b_name']}: "
                          f"{overlap['overlap_percentage']:.1f}% overlap")
        
        # Step 4: Create targeted campaigns for high-value segments
        created_campaigns = []
        
        for segment in high_value_segments[:3]:  # Top 3 segments
            print(f"\n🎯 Creating targeted campaign for: {segment['name']}")
            
            # Generate personalized copy for this segment
            copy_result = await client.call_tool(
                "create_campaign_copy",
                {
                    "product_name": "Premium Subscription",
                    "product_description": "Unlock advanced features and priority support",
                    "target_audience": segment['description'],
                    "tone": "professional" if segment['characteristics'][0] == "B2B" else "casual",
                    "copy_type": "email_campaign",
                    "variants_count": 2,
                    "keywords": segment.get('interests', []),
                    "call_to_action": "Upgrade Now"
                }
            )
            
            # Select best variant
            best_variant = copy_result['variants'][copy_result['best_performer_index']]
            
            # Record the campaign optimization
            decision = await track_campaign_optimization(
                campaign_id=f"segment_{segment['segment_id']}_campaign",
                optimization_type="audience_targeting",
                changes_made={
                    "segment_targeted": segment['name'],
                    "segment_size": segment['size'],
                    "personalization": "AI-generated copy",
                    "copy_variant": best_variant['variant_id']
                },
                expected_impact={
                    "open_rate": segment['engagement_score'] * 0.5,
                    "conversion_rate": segment['value_score'] * 0.1,
                    "revenue_per_contact": segment['avg_transaction_value'] * 1.2
                }
            )
            
            created_campaigns.append({
                'segment': segment['name'],
                'campaign_id': f"segment_{segment['segment_id']}_campaign",
                'copy': best_variant,
                'expected_conversions': int(segment['size'] * segment['value_score'] * 0.001)
            })
            
            print(f"   ✓ Campaign created with {best_variant['tone']} tone")
            print(f"   ✓ Expected conversions: {created_campaigns[-1]['expected_conversions']}")
        
        # Step 5: Summary and recommendations
        print("\n📋 Segmentation Summary:")
        print(f"- High-value segments identified: {len(high_value_segments)}")
        print(f"- Targeted campaigns created: {len(created_campaigns)}")
        print(f"- Total addressable audience: {sum(s['size'] for s in high_value_segments)}")
        
        print("\n💡 AI Recommendations:")
        for rec in segmentation_result['recommendations'][:5]:
            print(f"- {rec}")
        
        return {
            'segments': segmentation_result['segments'],
            'campaigns': created_campaigns,
            'insights': segmentation_result['insights']
        }

# Run audience segmentation
if __name__ == "__main__":
    asyncio.run(audience_segmentation_workflow())
```

## Complete Marketing Automation Cycle

### Scenario
A complete end-to-end marketing automation workflow that combines all capabilities.

```python
import asyncio
from datetime import datetime, timedelta
from mcp import Client
from src.integrations.unified_client import UnifiedMarketingClient, Platform
from src.ai_engine import MarketingAIEngine
from src.database import DatabaseManager
from src.database_utils import AutomationTracker, TaskType
from src.reporting import ReportGenerator

async def complete_automation_cycle():
    """Complete marketing automation cycle with feedback loop"""
    
    # Initialize components
    mcp_client = Client("marketing-automation")
    unified_client = UnifiedMarketingClient()
    ai_engine = MarketingAIEngine()
    db = DatabaseManager()
    report_gen = ReportGenerator()
    
    print("🚀 Starting Complete Marketing Automation Cycle")
    print("=" * 60)
    
    # Phase 1: Initial Analysis
    print("\n📊 Phase 1: Initial Campaign Analysis")
    
    async with mcp_client:
        # Generate baseline report
        baseline_report = await mcp_client.call_tool(
            "generate_campaign_report",
            {
                "campaign_ids": ["camp_001", "camp_002", "camp_003", "camp_004"],
                "date_range": {
                    "start": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end": datetime.now().strftime("%Y-%m-%d")
                },
                "metrics": ["impressions", "clicks", "conversions", "cost", "revenue", "roi"],
                "format": "json",
                "include_insights": True
            }
        )
    
    print(f"✓ Baseline report generated: {baseline_report['report_id']}")
    print(f"  Average ROI: {baseline_report['summary']['average_roi']:.1f}%")
    print(f"  Total conversions: {baseline_report['summary']['total_conversions']}")
    
    # Phase 2: AI-Driven Optimization
    print("\n🤖 Phase 2: AI-Driven Optimization")
    
    async with AutomationTracker(
        task_type=TaskType.CAMPAIGN_MANAGEMENT,
        task_name="Complete Automation Cycle",
        manual_duration_minutes=480,  # 8 hours manual work
        hourly_rate=100.0
    ) as tracker:
        
        # Budget optimization
        async with mcp_client:
            budget_optimization = await mcp_client.call_tool(
                "optimize_campaign_budget",
                {
                    "campaign_ids": [c['campaign_id'] for c in baseline_report['campaigns']],
                    "total_budget": sum(c['cost'] for c in baseline_report['campaigns']) * 1.1,
                    "optimization_goal": "maximize_roi",
                    "constraints": {
                        c['campaign_id']: {
                            "min": c['cost'] * 0.5,
                            "max": c['cost'] * 1.5
                        } for c in baseline_report['campaigns']
                    },
                    "include_projections": True
                }
            )
        
        print(f"✓ Budget optimization complete: {budget_optimization['optimization_id']}")
        print(f"  Projected ROI improvement: {budget_optimization['projected_improvement']['roi_change']:.1f}%")
        
        tracker.set_result("budget_optimizations", len(budget_optimization['allocations']))
        
        # Phase 3: Audience Analysis
        print("\n👥 Phase 3: Audience Segmentation")
        
        async with mcp_client:
            audience_analysis = await mcp_client.call_tool(
                "analyze_audience_segments",
                {
                    "contact_list_id": "main_database",
                    "criteria": ["demographics", "behavior", "engagement"],
                    "min_segment_size": 1000,
                    "max_segments": 5,
                    "include_recommendations": True
                }
            )
        
        print(f"✓ Audience analysis complete: {audience_analysis['analysis_id']}")
        print(f"  Segments identified: {len(audience_analysis['segments'])}")
        
        # Phase 4: Creative Generation
        print("\n✍️ Phase 4: AI-Powered Creative Generation")
        
        creative_variants = []
        for segment in audience_analysis['segments'][:3]:  # Top 3 segments
            async with mcp_client:
                copy_result = await mcp_client.call_tool(
                    "create_campaign_copy",
                    {
                        "product_name": "Marketing Automation Platform",
                        "product_description": "Save time and increase ROI with AI",
                        "target_audience": segment['description'],
                        "tone": "professional",
                        "copy_type": "ad_creative",
                        "variants_count": 2,
                        "keywords": ["automation", "ROI", "efficiency"]
                    }
                )
            
            creative_variants.append({
                'segment': segment['name'],
                'variants': copy_result['variants']
            })
            
            print(f"✓ Created {len(copy_result['variants'])} variants for {segment['name']}")
        
        tracker.set_result("creative_variants", sum(len(cv['variants']) for cv in creative_variants))
        
        # Phase 5: Implementation
        print("\n🚀 Phase 5: Implementation")
        
        # Connect to platforms
        await unified_client.connect_all()
        
        implementation_results = []
        
        # Apply budget changes
        for allocation in budget_optimization['allocations']:
            if abs(allocation['change_percentage']) > 5:  # Significant change
                result = await unified_client.update_campaign_budget(
                    campaign_id=allocation['campaign_id'],
                    new_budget=allocation['recommended_budget'],
                    platforms=[Platform.ALL]
                )
                
                implementation_results.append({
                    'type': 'budget_update',
                    'campaign_id': allocation['campaign_id'],
                    'change': allocation['change_percentage']
                })
                
                print(f"✓ Updated budget for {allocation['campaign_id']}: "
                      f"{allocation['change_percentage']:+.1f}%")
                
                tracker.increment_items(1)
        
        # Phase 6: Monitoring
        print("\n📈 Phase 6: Performance Monitoring (Simulated 7-day period)")
        
        # Simulate 7 days of monitoring
        monitoring_results = []
        
        for day in range(7):
            # In real implementation, this would fetch actual data
            daily_performance = {
                'day': day + 1,
                'total_impressions': 50000 + (day * 5000),
                'total_clicks': 1000 + (day * 100),
                'total_conversions': 50 + (day * 10),
                'average_ctr': 2.0 + (day * 0.1),
                'average_roi': baseline_report['summary']['average_roi'] * (1 + day * 0.02)
            }
            
            monitoring_results.append(daily_performance)
            
            # Check if intervention needed
            if daily_performance['average_ctr'] < 1.5:
                print(f"  ⚠️ Day {day + 1}: Low CTR detected, triggering optimization")
                # Would trigger real-time optimization here
        
        # Phase 7: Reporting and Analysis
        print("\n📊 Phase 7: Final Reporting and ROI Analysis")
        
        # Generate comprehensive report
        final_report = await report_gen.generate_optimization_report(
            campaign_id="all_campaigns",
            optimization_date=datetime.now(),
            changes_made={
                'budget_reallocations': len(implementation_results),
                'audience_segments': len(audience_analysis['segments']),
                'creative_variants': sum(len(cv['variants']) for cv in creative_variants)
            },
            performance_comparison=True
        )
        
        # Calculate actual ROI impact
        roi_tracking = db.calculate_period_roi(
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now()
        )
        
        tracker.set_result("final_roi_improvement", 15.3)  # Simulated
        tracker.set_result("conversions_increase", 127)  # Simulated
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 AUTOMATION CYCLE COMPLETE")
    print("=" * 60)
    
    print("\n📊 Results Summary:")
    print(f"  • Time saved: {tracker.time_saved_minutes:.0f} minutes")
    print(f"  • Cost saved: ${tracker.cost_saved:,.2f}")
    print(f"  • Budget optimizations: {tracker.results.get('budget_optimizations', 0)}")
    print(f"  • Creative variants: {tracker.results.get('creative_variants', 0)}")
    print(f"  • ROI improvement: {tracker.results.get('final_roi_improvement', 0):.1f}%")
    print(f"  • Additional conversions: {tracker.results.get('conversions_increase', 0)}")
    
    print("\n💡 Next Steps:")
    print("  1. Review AI-generated insights in the executive dashboard")
    print("  2. A/B test the top-performing creative variants")
    print("  3. Schedule next automation cycle for optimal results")
    print("  4. Share ROI report with stakeholders")
    
    return {
        'baseline': baseline_report,
        'optimization': budget_optimization,
        'audience': audience_analysis,
        'creatives': creative_variants,
        'implementation': implementation_results,
        'monitoring': monitoring_results,
        'roi_impact': tracker.results
    }

# Run complete automation cycle
if __name__ == "__main__":
    result = asyncio.run(complete_automation_cycle())
    
    # Save results for analysis
    import json
    with open('automation_cycle_results.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("\n✅ Full results saved to automation_cycle_results.json")
```

## Best Practices

### 1. Error Handling
Always implement proper error handling for API failures:

```python
from src.integrations.base import RateLimitError, AuthenticationError

try:
    result = await client.fetch_campaign_performance(...)
except RateLimitError as e:
    print(f"Rate limit hit, waiting {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
    # Retry
except AuthenticationError:
    print("Authentication failed, refreshing tokens...")
    await client.reconnect()
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log error and handle gracefully
```

### 2. Automation Tracking
Always track automation tasks for ROI calculation:

```python
async with AutomationTracker(
    task_type=TaskType.BUDGET_OPTIMIZATION,
    task_name="Q4 Budget Reallocation",
    manual_duration_minutes=120,
    hourly_rate=75.0
) as tracker:
    # Perform automation
    tracker.set_result("key_metric", value)
    tracker.increment_items(1)
```

### 3. Incremental Changes
Make incremental changes and monitor impact:

```python
# Start with small changes
if optimization_confidence > 0.9:
    change_factor = 0.2  # 20% change
elif optimization_confidence > 0.8:
    change_factor = 0.1  # 10% change
else:
    change_factor = 0.05  # 5% change
```

### 4. Data Validation
Always validate data before processing:

```python
# Validate campaign data
if not campaigns or len(campaigns) == 0:
    raise ValueError("No campaigns found for optimization")

# Validate metrics
required_metrics = ["impressions", "clicks", "conversions", "cost"]
for campaign in campaigns:
    missing = [m for m in required_metrics if m not in campaign.get("metrics", {})]
    if missing:
        raise ValueError(f"Missing metrics for {campaign['id']}: {missing}")
```

### 5. Logging and Monitoring
Implement comprehensive logging:

```python
import logging

logger = logging.getLogger("marketing_automation")

# Log important events
logger.info(f"Starting optimization for {len(campaigns)} campaigns")
logger.debug(f"Campaign data: {campaigns}")
logger.warning(f"Low CTR detected for campaign {campaign_id}")
logger.error(f"Failed to update budget: {error}")
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check environment variables are set correctly
   - Verify API credentials haven't expired
   - Ensure proper OAuth scopes

2. **Rate Limiting**
   - Implement exponential backoff
   - Use batch operations where possible
   - Monitor API quotas

3. **Data Inconsistencies**
   - Validate data types and formats
   - Handle missing or null values
   - Implement data cleaning routines

4. **Performance Issues**
   - Use async operations for parallel processing
   - Implement caching for frequently accessed data
   - Optimize database queries

For more examples and advanced use cases, see the test files in the `tests/` directory.