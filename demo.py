#!/usr/bin/env python3
"""
Marketing Automation MCP Demo for DoorDash Interview
Demonstrates key capabilities with realistic sample data
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
from pathlib import Path

# For demo purposes, we'll simulate API responses
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

class MarketingAutomationDemo:
    """Demo showcasing Marketing Automation MCP capabilities"""
    
    def __init__(self):
        self.sample_campaigns = self._generate_sample_campaigns()
        self.demo_results = {}
        
    def _generate_sample_campaigns(self) -> List[Dict[str, Any]]:
        """Generate realistic DoorDash marketing campaign data"""
        campaigns = [
            {
                "campaign_id": "dd_search_001",
                "name": "DoorDash Search - Food Delivery",
                "platform": "google_ads",
                "budget": 15000.0,
                "impressions": 850000,
                "clicks": 17000,
                "conversions": 425,
                "cost": 14500.0,
                "revenue": 21250.0,
                "ctr": 2.0,
                "conversion_rate": 2.5,
                "cpa": 34.12,
                "roi": 46.55,
                "status": "underperforming"
            },
            {
                "campaign_id": "dd_display_002",
                "name": "DoorDash Display - Brand Awareness",
                "platform": "google_ads",
                "budget": 10000.0,
                "impressions": 2000000,
                "clicks": 20000,
                "conversions": 800,
                "cost": 9800.0,
                "revenue": 40000.0,
                "ctr": 1.0,
                "conversion_rate": 4.0,
                "cpa": 12.25,
                "roi": 308.16,
                "status": "performing"
            },
            {
                "campaign_id": "dd_social_003",
                "name": "DoorDash Social - New User Acquisition",
                "platform": "facebook_ads",
                "budget": 20000.0,
                "impressions": 1500000,
                "clicks": 30000,
                "conversions": 1200,
                "cost": 19500.0,
                "revenue": 60000.0,
                "ctr": 2.0,
                "conversion_rate": 4.0,
                "cpa": 16.25,
                "roi": 207.69,
                "status": "performing"
            },
            {
                "campaign_id": "dd_video_004",
                "name": "DoorDash Video - Restaurant Partners",
                "platform": "facebook_ads",
                "budget": 8000.0,
                "impressions": 500000,
                "clicks": 5000,
                "conversions": 100,
                "cost": 7800.0,
                "revenue": 5000.0,
                "ctr": 1.0,
                "conversion_rate": 2.0,
                "cpa": 78.0,
                "roi": -35.90,
                "status": "critical"
            },
            {
                "campaign_id": "dd_retarget_005",
                "name": "DoorDash Retargeting - Cart Abandoners",
                "platform": "google_ads",
                "budget": 5000.0,
                "impressions": 250000,
                "clicks": 10000,
                "conversions": 800,
                "cost": 4800.0,
                "revenue": 40000.0,
                "ctr": 4.0,
                "conversion_rate": 8.0,
                "cpa": 6.0,
                "roi": 733.33,
                "status": "star_performer"
            }
        ]
        return campaigns
    
    async def run_demo(self):
        """Run the complete demo workflow"""
        print("\n" + "="*80)
        print("🚀 DoorDash Marketing Automation Demo")
        print("="*80)
        
        # Step 1: Connect to marketing accounts
        await self.connect_to_accounts()
        
        # Step 2: Analyze current performance
        await self.analyze_performance()
        
        # Step 3: Identify underperforming campaigns
        await self.identify_underperformers()
        
        # Step 4: Generate AI optimization recommendations
        await self.generate_optimizations()
        
        # Step 5: Show projected improvements
        await self.show_projections()
        
        # Step 6: Display savings dashboard
        await self.display_savings_dashboard()
        
        # Generate presentation
        await self.generate_presentation()
        
        return self.demo_results
    
    async def connect_to_accounts(self):
        """Simulate connecting to marketing platforms"""
        print("\n📡 Step 1: Connecting to Marketing Platforms")
        print("-" * 50)
        
        platforms = [
            ("Google Ads", "✓ Connected - 3 accounts, $58,000 monthly budget"),
            ("Facebook Ads", "✓ Connected - 2 accounts, $28,000 monthly budget"),
            ("Google Analytics", "✓ Connected - Tracking 5 properties")
        ]
        
        for platform, status in platforms:
            print(f"  {platform}: {status}")
            await asyncio.sleep(0.5)  # Simulate connection time
        
        print("\n✅ All platforms connected successfully!")
        
        self.demo_results["connections"] = {
            "total_accounts": 5,
            "total_monthly_budget": 86000,
            "platforms_connected": 3
        }
    
    async def analyze_performance(self):
        """Analyze current campaign performance"""
        print("\n📊 Step 2: Analyzing Campaign Performance")
        print("-" * 50)
        
        total_spend = sum(c["cost"] for c in self.sample_campaigns)
        total_revenue = sum(c["revenue"] for c in self.sample_campaigns)
        total_conversions = sum(c["conversions"] for c in self.sample_campaigns)
        avg_roi = ((total_revenue - total_spend) / total_spend) * 100
        
        print(f"\n  Campaign Summary (Last 30 Days):")
        print(f"  • Total Campaigns: {len(self.sample_campaigns)}")
        print(f"  • Total Spend: ${total_spend:,.2f}")
        print(f"  • Total Revenue: ${total_revenue:,.2f}")
        print(f"  • Total Conversions: {total_conversions:,}")
        print(f"  • Average ROI: {avg_roi:.1f}%")
        
        print("\n  Performance by Campaign:")
        for campaign in self.sample_campaigns:
            status_emoji = {
                "star_performer": "⭐",
                "performing": "✅",
                "underperforming": "⚠️",
                "critical": "🚨"
            }[campaign["status"]]
            
            print(f"  {status_emoji} {campaign['name']}")
            print(f"     ROI: {campaign['roi']:.1f}% | CPA: ${campaign['cpa']:.2f} | "
                  f"Conv Rate: {campaign['conversion_rate']:.1f}%")
        
        self.demo_results["current_performance"] = {
            "total_spend": total_spend,
            "total_revenue": total_revenue,
            "total_conversions": total_conversions,
            "average_roi": avg_roi
        }
    
    async def identify_underperformers(self):
        """Identify and analyze underperforming campaigns"""
        print("\n🔍 Step 3: Identifying Optimization Opportunities")
        print("-" * 50)
        
        underperformers = [c for c in self.sample_campaigns 
                          if c["status"] in ["underperforming", "critical"]]
        
        print(f"\n  Found {len(underperformers)} campaigns needing optimization:")
        
        for campaign in underperformers:
            print(f"\n  🎯 {campaign['name']}")
            print(f"     Current ROI: {campaign['roi']:.1f}%")
            
            # Identify specific issues
            issues = []
            if campaign["ctr"] < 1.5:
                issues.append(f"Low CTR ({campaign['ctr']:.1f}% vs 2.5% benchmark)")
            if campaign["conversion_rate"] < 3.0:
                issues.append(f"Low conversion rate ({campaign['conversion_rate']:.1f}% vs 4% benchmark)")
            if campaign["cpa"] > 30:
                issues.append(f"High CPA (${campaign['cpa']:.2f} vs $25 target)")
            
            print("     Issues identified:")
            for issue in issues:
                print(f"     • {issue}")
        
        self.demo_results["underperformers"] = underperformers
    
    async def generate_optimizations(self):
        """Generate AI-powered optimization recommendations"""
        print("\n🤖 Step 4: AI-Generated Optimization Recommendations")
        print("-" * 50)
        
        optimizations = [
            {
                "campaign": "DoorDash Search - Food Delivery",
                "recommendations": [
                    {
                        "action": "Implement dayparting strategy",
                        "details": "Increase bids 30% during lunch (11am-2pm) and dinner (5pm-9pm)",
                        "impact": "Expected 25% increase in conversions",
                        "confidence": 0.92
                    },
                    {
                        "action": "Refine keyword targeting",
                        "details": "Add 15 negative keywords, pause 8 low-performing keywords",
                        "impact": "Reduce wasted spend by $2,000/month",
                        "confidence": 0.88
                    },
                    {
                        "action": "Update ad copy",
                        "details": "Test 'Free delivery on first order' messaging",
                        "impact": "Projected 15% CTR improvement",
                        "confidence": 0.85
                    }
                ]
            },
            {
                "campaign": "DoorDash Video - Restaurant Partners",
                "recommendations": [
                    {
                        "action": "Pause campaign and reallocate budget",
                        "details": "Move $6,000 to high-performing retargeting campaign",
                        "impact": "Avoid $3,000 monthly loss, gain $18,000 from reallocation",
                        "confidence": 0.95
                    },
                    {
                        "action": "Redesign creative strategy",
                        "details": "Focus on restaurant success stories instead of features",
                        "impact": "Expected 3x improvement in engagement",
                        "confidence": 0.78
                    }
                ]
            }
        ]
        
        for opt in optimizations:
            print(f"\n  📋 {opt['campaign']}:")
            for i, rec in enumerate(opt['recommendations'], 1):
                print(f"\n     {i}. {rec['action']}")
                print(f"        Details: {rec['details']}")
                print(f"        Impact: {rec['impact']}")
                print(f"        Confidence: {rec['confidence']*100:.0f}%")
        
        self.demo_results["optimizations"] = optimizations
    
    async def show_projections(self):
        """Show projected improvements from optimizations"""
        print("\n📈 Step 5: Projected Impact Analysis")
        print("-" * 50)
        
        # Calculate projections
        current_total_spend = sum(c["cost"] for c in self.sample_campaigns)
        current_total_revenue = sum(c["revenue"] for c in self.sample_campaigns)
        current_roi = ((current_total_revenue - current_total_spend) / current_total_spend) * 100
        
        # Projected improvements
        projected_spend = current_total_spend - 2000  # Reduced waste
        projected_revenue = current_total_revenue * 1.28  # 28% improvement
        projected_roi = ((projected_revenue - projected_spend) / projected_spend) * 100
        roi_improvement = projected_roi - current_roi
        
        print("\n  Current State vs. Projected (After Optimizations):")
        print(f"\n  {'Metric':<20} {'Current':>15} {'Projected':>15} {'Change':>15}")
        print("  " + "-"*65)
        print(f"  {'Monthly Spend':<20} ${current_total_spend:>14,.2f} ${projected_spend:>14,.2f} "
              f"${projected_spend-current_total_spend:>14,.2f}")
        print(f"  {'Monthly Revenue':<20} ${current_total_revenue:>14,.2f} ${projected_revenue:>14,.2f} "
              f"${projected_revenue-current_total_revenue:>14,.2f}")
        print(f"  {'ROI':<20} {current_roi:>14.1f}% {projected_roi:>14.1f}% "
              f"{roi_improvement:>14.1f}%")
        print(f"  {'Conversions':<20} {sum(c['conversions'] for c in self.sample_campaigns):>15,} "
              f"{int(sum(c['conversions'] for c in self.sample_campaigns) * 1.35):>15,} "
              f"{int(sum(c['conversions'] for c in self.sample_campaigns) * 0.35):>15,}")
        
        print(f"\n  💰 Projected Annual Impact:")
        print(f"     • Additional Revenue: ${(projected_revenue - current_total_revenue) * 12:,.2f}")
        print(f"     • Cost Savings: ${(current_total_spend - projected_spend) * 12:,.2f}")
        print(f"     • Net Benefit: ${((projected_revenue - current_total_revenue) + (current_total_spend - projected_spend)) * 12:,.2f}")
        
        self.demo_results["projections"] = {
            "monthly_revenue_increase": projected_revenue - current_total_revenue,
            "monthly_cost_savings": current_total_spend - projected_spend,
            "roi_improvement": roi_improvement,
            "annual_net_benefit": ((projected_revenue - current_total_revenue) + 
                                 (current_total_spend - projected_spend)) * 12
        }
    
    async def display_savings_dashboard(self):
        """Display time and cost savings from automation"""
        print("\n⏱️  Step 6: Automation Savings Dashboard")
        print("-" * 50)
        
        # Automation metrics
        tasks = [
            {"name": "Campaign Performance Analysis", "manual_hours": 8, "automated_minutes": 2},
            {"name": "Budget Optimization", "manual_hours": 6, "automated_minutes": 1},
            {"name": "A/B Test Analysis", "manual_hours": 4, "automated_minutes": 0.5},
            {"name": "Report Generation", "manual_hours": 10, "automated_minutes": 3},
            {"name": "Audience Segmentation", "manual_hours": 12, "automated_minutes": 2}
        ]
        
        hourly_rate = 75  # Marketing analyst hourly rate
        
        print("\n  Weekly Time Savings by Task:")
        print(f"  {'Task':<35} {'Manual':>10} {'Automated':>12} {'Time Saved':>12}")
        print("  " + "-"*70)
        
        total_manual_hours = 0
        total_automated_hours = 0
        
        for task in tasks:
            manual = task["manual_hours"]
            automated = task["automated_minutes"] / 60
            saved = manual - automated
            total_manual_hours += manual
            total_automated_hours += automated
            
            print(f"  {task['name']:<35} {manual:>9.1f}h {automated:>11.1f}h {saved:>11.1f}h")
        
        total_saved = total_manual_hours - total_automated_hours
        weekly_cost_saved = total_saved * hourly_rate
        annual_hours_saved = total_saved * 52
        annual_cost_saved = weekly_cost_saved * 52
        
        print("  " + "-"*70)
        print(f"  {'TOTAL':<35} {total_manual_hours:>9.1f}h {total_automated_hours:>11.1f}h "
              f"{total_saved:>11.1f}h")
        
        print(f"\n  💼 Resource Savings Summary:")
        print(f"     • Weekly hours saved: {total_saved:.1f} hours")
        print(f"     • Weekly cost saved: ${weekly_cost_saved:,.2f}")
        print(f"     • Annual hours saved: {annual_hours_saved:,.0f} hours")
        print(f"     • Annual cost saved: ${annual_cost_saved:,.2f}")
        print(f"     • Equivalent to: {annual_hours_saved/2080:.1f} full-time employees")
        
        # ROI of automation
        automation_cost = 50000  # Annual cost of automation platform
        total_benefit = annual_cost_saved + self.demo_results["projections"]["annual_net_benefit"]
        automation_roi = ((total_benefit - automation_cost) / automation_cost) * 100
        
        print(f"\n  📊 Automation ROI:")
        print(f"     • Total Annual Benefit: ${total_benefit:,.2f}")
        print(f"     • Automation Cost: ${automation_cost:,.2f}")
        print(f"     • ROI: {automation_roi:.0f}%")
        print(f"     • Payback Period: {automation_cost/total_benefit*12:.1f} months")
        
        self.demo_results["savings"] = {
            "weekly_hours_saved": total_saved,
            "annual_cost_saved": annual_cost_saved,
            "fte_equivalent": annual_hours_saved/2080,
            "automation_roi": automation_roi
        }
    
    async def generate_presentation(self):
        """Generate presentation slides"""
        print("\n📑 Generating Presentation Deck...")
        print("-" * 50)
        
        # Create presentation data
        presentation = PresentationGenerator(self.demo_results)
        presentation.generate_slides()
        
        print("✅ Presentation deck generated: doordash_demo_deck.html")
        print("   Open in browser to view interactive slides")
        

class PresentationGenerator:
    """Generate HTML presentation deck from demo results"""
    
    def __init__(self, demo_results: Dict[str, Any]):
        self.results = demo_results
        
    def generate_slides(self):
        """Generate HTML presentation"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DoorDash Marketing Automation Demo</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            color: #ffffff;
            overflow: hidden;
        }}
        .slide {{
            width: 100vw;
            height: 100vh;
            display: none;
            padding: 60px;
            box-sizing: border-box;
            position: relative;
        }}
        .slide.active {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        h1 {{
            font-size: 48px;
            margin: 0 0 20px 0;
            color: #ff3008;
        }}
        h2 {{
            font-size: 36px;
            margin: 0 0 30px 0;
            color: #ffffff;
        }}
        h3 {{
            font-size: 28px;
            margin: 20px 0;
            color: #ff3008;
        }}
        .metric {{
            font-size: 64px;
            font-weight: bold;
            color: #ff3008;
            margin: 20px 0;
        }}
        .sub-metric {{
            font-size: 24px;
            color: #cccccc;
            margin: 10px 0;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 40px;
            margin: 30px 0;
        }}
        .card {{
            background: #2a2a2a;
            padding: 30px;
            border-radius: 12px;
            border: 2px solid #ff3008;
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress {{
            height: 100%;
            background: #ff3008;
            transition: width 1s ease;
        }}
        .controls {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            gap: 10px;
        }}
        button {{
            background: #ff3008;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        button:hover {{
            background: #e62a00;
            transform: translateY(-2px);
        }}
        .highlight {{
            color: #ff3008;
            font-weight: bold;
        }}
        .savings-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            margin: 40px 0;
        }}
        .savings-card {{
            text-align: center;
            padding: 20px;
            background: #2a2a2a;
            border-radius: 8px;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fade-in {{
            animation: fadeIn 0.6s ease forwards;
        }}
    </style>
</head>
<body>
    <!-- Slide 1: Title -->
    <div class="slide active">
        <h1>Marketing Automation with AI</h1>
        <h2>Transforming DoorDash's Marketing Operations</h2>
        <div class="sub-metric">Powered by Model Context Protocol (MCP)</div>
        <div style="margin-top: 60px;">
            <div class="metric fade-in">{roi_improvement:.0f}% ROI Improvement</div>
            <div class="sub-metric fade-in" style="animation-delay: 0.3s">
                ${annual_benefit:,.0f} Annual Benefit
            </div>
        </div>
    </div>

    <!-- Slide 2: Current State -->
    <div class="slide">
        <h2>Current Campaign Performance</h2>
        <div class="grid">
            <div class="card fade-in">
                <h3>Monthly Spend</h3>
                <div class="metric">${current_spend:,.0f}</div>
                <div class="sub-metric">Across 5 campaigns</div>
            </div>
            <div class="card fade-in" style="animation-delay: 0.2s">
                <h3>Average ROI</h3>
                <div class="metric">{current_roi:.1f}%</div>
                <div class="sub-metric">Below industry benchmark</div>
            </div>
            <div class="card fade-in" style="animation-delay: 0.4s">
                <h3>Underperforming</h3>
                <div class="metric">2</div>
                <div class="sub-metric">Campaigns need optimization</div>
            </div>
            <div class="card fade-in" style="animation-delay: 0.6s">
                <h3>Opportunity</h3>
                <div class="metric">${waste:,.0f}</div>
                <div class="sub-metric">Monthly wasted spend</div>
            </div>
        </div>
    </div>

    <!-- Slide 3: AI Recommendations -->
    <div class="slide">
        <h2>AI-Powered Optimization Strategy</h2>
        <div style="margin: 40px 0;">
            <h3>🎯 DoorDash Search Campaign</h3>
            <ul style="font-size: 24px; line-height: 1.8;">
                <li class="fade-in">Implement dayparting: <span class="highlight">+25% conversions</span></li>
                <li class="fade-in" style="animation-delay: 0.2s">Refine keywords: <span class="highlight">-$2,000/month waste</span></li>
                <li class="fade-in" style="animation-delay: 0.4s">Update ad copy: <span class="highlight">+15% CTR</span></li>
            </ul>
            
            <h3 style="margin-top: 40px;">🚨 Video Campaign (Critical)</h3>
            <ul style="font-size: 24px; line-height: 1.8;">
                <li class="fade-in" style="animation-delay: 0.6s">Pause & reallocate: <span class="highlight">+$21,000 monthly gain</span></li>
                <li class="fade-in" style="animation-delay: 0.8s">Redesign creative: <span class="highlight">3x engagement</span></li>
            </ul>
        </div>
        <div class="progress-bar">
            <div class="progress" style="width: 88%;"></div>
        </div>
        <div class="sub-metric">Average Confidence Score: 88%</div>
    </div>

    <!-- Slide 4: Projected Impact -->
    <div class="slide">
        <h2>Projected Business Impact</h2>
        <div class="grid">
            <div style="flex: 1;">
                <h3>Revenue Growth</h3>
                <div class="metric fade-in">${monthly_revenue_increase:,.0f}</div>
                <div class="sub-metric">Additional monthly revenue</div>
                
                <h3 style="margin-top: 40px;">Cost Reduction</h3>
                <div class="metric fade-in" style="animation-delay: 0.3s">${monthly_cost_savings:,.0f}</div>
                <div class="sub-metric">Monthly savings from optimization</div>
            </div>
            <div style="flex: 1; display: flex; align-items: center; justify-content: center;">
                <div style="text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 20px;">Annual Net Benefit</div>
                    <div class="metric" style="font-size: 80px; color: #00ff00;">
                        ${annual_net_benefit:,.0f}
                    </div>
                    <div class="sub-metric" style="font-size: 28px; margin-top: 20px;">
                        ROI Improvement: <span class="highlight">{roi_improvement:.1f}%</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 5: Time Savings -->
    <div class="slide">
        <h2>Operational Efficiency Gains</h2>
        <div class="savings-grid">
            <div class="savings-card fade-in">
                <div class="icon">⏱️</div>
                <div class="metric" style="font-size: 48px;">{weekly_hours:.0f}</div>
                <div class="sub-metric">Hours saved weekly</div>
            </div>
            <div class="savings-card fade-in" style="animation-delay: 0.2s">
                <div class="icon">💰</div>
                <div class="metric" style="font-size: 48px;">${annual_labor_saved:,.0f}</div>
                <div class="sub-metric">Annual labor savings</div>
            </div>
            <div class="savings-card fade-in" style="animation-delay: 0.4s">
                <div class="icon">👥</div>
                <div class="metric" style="font-size: 48px;">{fte:.1f}</div>
                <div class="sub-metric">FTE equivalent</div>
            </div>
        </div>
        <div style="margin-top: 40px;">
            <h3>Task Automation Breakdown</h3>
            <div style="font-size: 20px; line-height: 1.8;">
                <div class="fade-in" style="animation-delay: 0.6s">
                    📊 Campaign Analysis: <span class="highlight">8h → 2min</span> (99.6% reduction)
                </div>
                <div class="fade-in" style="animation-delay: 0.7s">
                    💰 Budget Optimization: <span class="highlight">6h → 1min</span> (99.7% reduction)
                </div>
                <div class="fade-in" style="animation-delay: 0.8s">
                    📈 Report Generation: <span class="highlight">10h → 3min</span> (99.5% reduction)
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 6: ROI Summary -->
    <div class="slide">
        <h2>Return on Investment</h2>
        <div style="text-align: center; margin: 60px 0;">
            <div class="metric" style="font-size: 120px; margin-bottom: 40px;">
                {automation_roi:.0f}%
            </div>
            <div class="sub-metric" style="font-size: 32px;">First Year ROI</div>
            
            <div class="grid" style="margin-top: 60px; max-width: 800px; margin-left: auto; margin-right: auto;">
                <div class="card">
                    <h3>Investment</h3>
                    <div style="font-size: 36px;">$50,000</div>
                    <div class="sub-metric">Annual platform cost</div>
                </div>
                <div class="card">
                    <h3>Payback Period</h3>
                    <div style="font-size: 36px;">{payback:.1f} months</div>
                    <div class="sub-metric">Break-even timeline</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 7: Next Steps -->
    <div class="slide">
        <h2>Implementation Roadmap</h2>
        <div style="font-size: 28px; line-height: 2; margin: 40px 0;">
            <div class="fade-in">
                <span class="highlight">Week 1-2:</span> Platform setup and integration
            </div>
            <div class="fade-in" style="animation-delay: 0.2s">
                <span class="highlight">Week 3-4:</span> Historical data analysis and baseline
            </div>
            <div class="fade-in" style="animation-delay: 0.4s">
                <span class="highlight">Month 2:</span> Implement first optimizations
            </div>
            <div class="fade-in" style="animation-delay: 0.6s">
                <span class="highlight">Month 3:</span> Scale to all campaigns
            </div>
            <div class="fade-in" style="animation-delay: 0.8s">
                <span class="highlight">Ongoing:</span> Continuous optimization and reporting
            </div>
        </div>
        <div style="text-align: center; margin-top: 60px;">
            <button onclick="window.location.href='mailto:demo@marketing-automation.ai'" 
                    style="font-size: 24px; padding: 20px 40px;">
                Schedule Deep Dive Discussion
            </button>
        </div>
    </div>

    <!-- Navigation -->
    <div class="controls">
        <button onclick="previousSlide()">Previous</button>
        <button onclick="nextSlide()">Next</button>
        <button onclick="autoPlay()">Auto Play</button>
    </div>

    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        let autoPlayInterval = null;

        function showSlide(index) {{
            slides.forEach(slide => slide.classList.remove('active'));
            slides[index].classList.add('active');
            
            // Reset animations
            const fadeElements = slides[index].querySelectorAll('.fade-in');
            fadeElements.forEach(el => {{
                el.style.animation = 'none';
                el.offsetHeight; // Trigger reflow
                el.style.animation = null;
            }});
        }}

        function nextSlide() {{
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }}

        function previousSlide() {{
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide);
        }}

        function autoPlay() {{
            if (autoPlayInterval) {{
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
            }} else {{
                autoPlayInterval = setInterval(nextSlide, 8000);
            }}
        }}

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextSlide();
            if (e.key === 'ArrowLeft') previousSlide();
            if (e.key === ' ') autoPlay();
        }});
    </script>
</body>
</html>
"""
        
        # Format with actual values
        html_content = html_content.format(
            roi_improvement=self.results['projections']['roi_improvement'],
            annual_benefit=self.results['projections']['annual_net_benefit'] + 
                          self.results['savings']['annual_cost_saved'],
            current_spend=self.results['current_performance']['total_spend'],
            current_roi=self.results['current_performance']['average_roi'],
            waste=2000,  # Estimated monthly waste
            monthly_revenue_increase=self.results['projections']['monthly_revenue_increase'],
            monthly_cost_savings=self.results['projections']['monthly_cost_savings'],
            annual_net_benefit=self.results['projections']['annual_net_benefit'],
            weekly_hours=self.results['savings']['weekly_hours_saved'],
            annual_labor_saved=self.results['savings']['annual_cost_saved'],
            fte=self.results['savings']['fte_equivalent'],
            automation_roi=self.results['savings']['automation_roi'],
            payback=50000/(self.results['projections']['annual_net_benefit'] + 
                          self.results['savings']['annual_cost_saved'])*12
        )
        
        # Save presentation
        with open('doordash_demo_deck.html', 'w') as f:
            f.write(html_content)


# Main execution
async def main():
    """Run the demo"""
    demo = MarketingAutomationDemo()
    results = await demo.run_demo()
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)
    print("\nKey Takeaways:")
    print(f"• ROI Improvement: {results['projections']['roi_improvement']:.1f}%")
    print(f"• Annual Benefit: ${results['projections']['annual_net_benefit'] + results['savings']['annual_cost_saved']:,.2f}")
    print(f"• Time Saved: {results['savings']['weekly_hours_saved']:.1f} hours/week")
    print(f"• Automation ROI: {results['savings']['automation_roi']:.0f}%")
    
    # Save results to JSON for further analysis
    with open('demo_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n📄 Results saved to: demo_results.json")
    print("🎯 Presentation deck: doordash_demo_deck.html")


if __name__ == "__main__":
    asyncio.run(main())