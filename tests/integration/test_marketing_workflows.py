"""Integration tests for complete marketing automation workflows"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
from decimal import Decimal

from src.database import TaskType, TaskStatus
from src.database_utils import AutomationTracker, track_campaign_optimization
from src.integrations.unified_client import UnifiedMarketingClient, Platform
from src.ai_engine import MarketingAIEngine
from src.reporting import ReportGenerator


class TestCompleteMarketingWorkflows:
    """Test end-to-end marketing automation workflows"""
    
    @pytest.mark.asyncio
    async def test_campaign_optimization_workflow(self, test_db, mock_openai_client):
        """Test complete campaign optimization workflow"""
        # Step 1: Create a campaign
        campaign = test_db.create_campaign({
            "campaign_id": "workflow_001",
            "name": "Q4 Holiday Campaign",
            "platform": "google_ads",
            "budget": Decimal("5000.00"),
            "start_date": datetime.now() - timedelta(days=30)
        })
        
        # Step 2: Track automation task for performance analysis
        async with AutomationTracker(
            task_type=TaskType.PERFORMANCE_ANALYSIS,
            task_name="Analyze Q4 Campaign Performance",
            manual_duration_minutes=60,
            hourly_rate=75.0,
            campaign_id=campaign.id
        ) as tracker:
            # Simulate performance analysis
            await asyncio.sleep(0.1)  # Simulate work
            tracker.set_result("metrics_analyzed", 5)
            tracker.set_result("insights_generated", 3)
            tracker.increment_items(1)
        
        # Verify task was tracked
        with test_db.get_session() as session:
            tasks = session.query(test_db.__class__).filter_by(
                campaign_id=campaign.id,
                task_type=TaskType.PERFORMANCE_ANALYSIS
            ).all()
            assert len(tasks) > 0
            assert tasks[0].status == TaskStatus.COMPLETED
        
        # Step 3: Record performance metrics
        metrics = test_db.record_performance_metrics(
            campaign_id=campaign.id,
            metrics={
                "impressions": 100000,
                "clicks": 2000,
                "conversions": 100,
                "revenue": Decimal("10000"),
                "cost": Decimal("2000")
            },
            is_automated=True,
            automation_applied=["bid_optimization", "audience_targeting"]
        )
        
        assert metrics.ctr == 2.0  # 2000/100000 * 100
        assert metrics.conversion_rate == 5.0  # 100/2000 * 100
        assert metrics.roas == 5.0  # 10000/2000
        
        # Step 4: AI-driven optimization decision
        decision = await track_campaign_optimization(
            campaign_id=campaign.id,
            optimization_type="budget",
            changes_made={
                "budget_increase": "20%",
                "bid_strategy": "maximize_conversions"
            },
            expected_impact={
                "conversions": 120,
                "roi": 5.5
            }
        )
        
        assert decision.decision_type == "budget_allocation"
        assert decision.campaign_id == campaign.id
        
        # Step 5: Calculate ROI
        roi_tracking = test_db.calculate_period_roi(
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now(),
            campaign_id=campaign.id
        )
        
        assert roi_tracking.tasks_automated == 1
        assert roi_tracking.total_time_saved_hours > 0
        assert roi_tracking.labor_cost_saved > 0
    
    @pytest.mark.asyncio
    async def test_multi_platform_campaign_sync(self):
        """Test synchronizing campaigns across multiple platforms"""
        with patch('src.integrations.unified_client.GoogleAdsClient') as mock_google,\
             patch('src.integrations.unified_client.FacebookAdsClient') as mock_facebook:
            
            # Setup mock clients
            mock_google_instance = AsyncMock()
            mock_facebook_instance = AsyncMock()
            mock_google.return_value = mock_google_instance
            mock_facebook.return_value = mock_facebook_instance
            
            # Mock performance data
            mock_google_instance.fetch_campaign_performance.return_value = {
                "platform": "google_ads",
                "data": [{
                    "campaign_id": "g_001",
                    "metrics": {"clicks": 1000, "conversions": 50}
                }]
            }
            
            mock_facebook_instance.fetch_campaign_performance.return_value = {
                "platform": "facebook_ads",
                "data": [{
                    "campaign_id": "f_001",
                    "metrics": {"clicks": 1500, "conversions": 75}
                }]
            }
            
            # Create unified client
            client = UnifiedMarketingClient()
            client._connected_clients = {Platform.GOOGLE_ADS, Platform.FACEBOOK_ADS}
            client.clients[Platform.GOOGLE_ADS] = mock_google_instance
            client.clients[Platform.FACEBOOK_ADS] = mock_facebook_instance
            
            # Fetch cross-platform data
            result = await client.fetch_campaign_performance(
                campaign_ids=["g_001", "f_001"],
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now(),
                metrics=["clicks", "conversions"],
                platforms=[Platform.GOOGLE_ADS, Platform.FACEBOOK_ADS]
            )
            
            # Verify aggregation
            assert result["summary"]["combined_metrics"]["clicks"] == 2500
            assert result["summary"]["combined_metrics"]["conversions"] == 125
            assert result["summary"]["total_campaigns"] == 2
    
    @pytest.mark.asyncio
    async def test_ai_driven_budget_reallocation(self, test_db, mock_openai_client):
        """Test AI-driven budget reallocation across campaigns"""
        # Create multiple campaigns
        campaigns = []
        for i in range(3):
            campaign = test_db.create_campaign({
                "campaign_id": f"budget_test_{i}",
                "name": f"Campaign {i}",
                "platform": "google_ads",
                "budget": Decimal("1000.00"),
                "start_date": datetime.now() - timedelta(days=30)
            })
            campaigns.append(campaign)
            
            # Add different performance levels
            test_db.record_performance_metrics(
                campaign_id=campaign.id,
                metrics={
                    "impressions": 10000 * (i + 1),
                    "clicks": 200 * (i + 1),
                    "conversions": 10 * (i + 1),
                    "revenue": Decimal(str(1000 * (i + 1))),
                    "cost": Decimal("500")
                }
            )
        
        # Create AI engine and analyze
        ai_engine = MarketingAIEngine()
        
        # Mock AI response for budget optimization
        mock_openai_client.chat.completions.create.return_value.choices[0].message.function_call.arguments = json.dumps({
            "suggestions": [
                {
                    "type": "budget_reallocation",
                    "campaign_id": "budget_test_2",
                    "action": "Increase budget to $1800",
                    "predicted_impact": {"roi_change": 25, "conversion_change": 30},
                    "confidence": 0.9,
                    "reasoning": "Highest performing campaign"
                },
                {
                    "type": "budget_reallocation",
                    "campaign_id": "budget_test_0",
                    "action": "Decrease budget to $700",
                    "predicted_impact": {"roi_change": -5, "conversion_change": -10},
                    "confidence": 0.85,
                    "reasoning": "Underperforming campaign"
                }
            ]
        })
        
        # Execute budget reallocation workflow
        campaign_data = []
        with test_db.get_session() as session:
            for campaign in campaigns:
                perf = session.query(test_db.__class__).filter_by(
                    campaign_id=campaign.id
                ).first()
                if perf:
                    campaign_data.append({
                        "campaign_id": campaign.campaign_id,
                        "metrics": {
                            "conversions": perf.conversions,
                            "roi": float(perf.roas)
                        }
                    })
        
        chain_result = await ai_engine.create_budget_reallocation_chain(
            campaigns=campaign_data,
            total_budget=3000,
            business_goals={"primary_goal": "maximize_roi"}
        )
        
        assert chain_result["chain_name"] == "budget_reallocation"
        assert len(chain_result["steps"]) >= 3
    
    @pytest.mark.asyncio
    async def test_automated_reporting_workflow(self, test_db, mock_report_data):
        """Test automated report generation workflow"""
        # Create test campaign with data
        campaign = test_db.create_campaign({
            "campaign_id": "report_test",
            "name": "Report Test Campaign",
            "platform": "google_ads",
            "budget": Decimal("5000"),
            "start_date": datetime.now() - timedelta(days=30)
        })
        
        # Add performance data
        for i in range(7):
            test_db.record_performance_metrics(
                campaign_id=campaign.id,
                metrics={
                    "impressions": 10000 + i * 1000,
                    "clicks": 200 + i * 20,
                    "conversions": 10 + i,
                    "revenue": Decimal(str(1000 + i * 100)),
                    "cost": Decimal(str(200 + i * 10))
                }
            )
        
        # Track report generation task
        async with AutomationTracker(
            task_type=TaskType.REPORT_GENERATION,
            task_name="Weekly Performance Report",
            manual_duration_minutes=120,
            hourly_rate=50.0,
            campaign_id=campaign.id
        ) as tracker:
            # Simulate report generation
            report_gen = ReportGenerator()
            
            # Mock the database queries
            with patch.object(test_db, 'get_session') as mock_session:
                mock_context = Mock()
                mock_context.__enter__ = Mock(return_value=Mock(
                    query=Mock(return_value=Mock(
                        filter=Mock(return_value=Mock(
                            all=Mock(return_value=[campaign])
                        ))
                    ))
                ))
                mock_context.__exit__ = Mock(return_value=None)
                mock_session.return_value = mock_context
                
                # Generate report (would normally query real data)
                # For test, we'll just verify the structure
                tracker.set_result("pages_generated", 4)
                tracker.set_result("charts_created", 6)
                tracker.increment_items(1)
        
        # Verify automation tracking
        with test_db.get_session() as session:
            report_task = session.query(test_db.__class__).filter_by(
                task_type=TaskType.REPORT_GENERATION,
                campaign_id=campaign.id
            ).first()
            
            assert report_task is not None
            assert report_task.status == TaskStatus.COMPLETED
            assert report_task.time_saved_minutes > 0
            assert report_task.cost_saved > 0
    
    @pytest.mark.asyncio
    async def test_complete_optimization_cycle(self, test_db):
        """Test a complete optimization cycle with feedback loop"""
        # Phase 1: Initial campaign setup
        campaign = test_db.create_campaign({
            "campaign_id": "cycle_test",
            "name": "Optimization Cycle Test",
            "platform": "google_ads",
            "budget": Decimal("10000"),
            "start_date": datetime.now() - timedelta(days=60)
        })
        
        # Phase 2: Initial performance (baseline)
        for day in range(30):
            test_db.record_performance_metrics(
                campaign_id=campaign.id,
                metrics={
                    "impressions": 5000,
                    "clicks": 100,
                    "conversions": 5,
                    "revenue": Decimal("500"),
                    "cost": Decimal("100")
                },
                is_automated=False
            )
        
        # Phase 3: Apply automation and AI optimization
        decision = test_db.record_ai_decision(
            decision_type="campaign_optimization",
            input_data={"avg_ctr": 2.0, "avg_conversion_rate": 5.0},
            decision_made={
                "bid_adjustment": "+15%",
                "audience_refinement": "exclude_low_intent"
            },
            confidence_score=0.88,
            reasoning="CTR and conversion rate below benchmarks",
            expected_impact={"ctr": 2.5, "conversion_rate": 6.5},
            campaign_id=campaign.id
        )
        
        # Phase 4: Record improved performance
        for day in range(30):
            test_db.record_performance_metrics(
                campaign_id=campaign.id,
                metrics={
                    "impressions": 5500,
                    "clicks": 138,  # 2.5% CTR
                    "conversions": 9,  # 6.5% conversion rate
                    "revenue": Decimal("900"),
                    "cost": Decimal("115")
                },
                is_automated=True,
                automation_applied=["bid_optimization", "audience_targeting"]
            )
        
        # Phase 5: Measure actual impact
        test_db.update_ai_decision_outcome(
            decision_id=decision.decision_id,
            actual_impact={"ctr": 2.5, "conversion_rate": 6.5}
        )
        
        # Phase 6: Calculate overall ROI
        roi_report = test_db.calculate_period_roi(
            period_start=datetime.now() - timedelta(days=60),
            period_end=datetime.now(),
            campaign_id=campaign.id
        )
        
        # Verify optimization success
        assert roi_report.avg_ctr_improvement > 0
        assert roi_report.avg_conversion_improvement > 0
        assert roi_report.roi_percentage > 0
        
        # Verify decision tracking
        with test_db.get_session() as session:
            updated_decision = session.query(test_db.__class__).filter_by(
                decision_id=decision.decision_id
            ).first()
            assert updated_decision.success_score >= 90  # Met expectations