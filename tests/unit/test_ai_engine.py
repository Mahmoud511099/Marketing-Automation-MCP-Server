"""Unit tests for AI engine and decision making"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock

from src.ai_engine import (
    MarketingAIEngine,
    CampaignPerformance,
    OptimizationSuggestion,
    AdCopyVariant,
    DecisionType
)


class TestMarketingAIEngine:
    """Test AI engine functionality"""
    
    @pytest.fixture
    def ai_engine(self):
        """Create AI engine with mocked OpenAI"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            return MarketingAIEngine(model="gpt-4-turbo-preview")
    
    @pytest.mark.asyncio
    async def test_analyze_campaign_performance(self, ai_engine, mock_openai_client):
        """Test campaign performance analysis"""
        campaigns = [
            {
                "campaign_id": "camp_001",
                "campaign_name": "Summer Sale",
                "metrics": {
                    "impressions": 50000,
                    "clicks": 1000,
                    "conversions": 50,
                    "cost": 500,
                    "revenue": 2500
                }
            }
        ]
        
        result = await ai_engine.analyze_campaign_performance(
            campaigns=campaigns,
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            benchmarks={"ctr": 2.0, "conversion_rate": 3.0}
        )
        
        # Verify results
        assert len(result) == 1
        assert isinstance(result[0], CampaignPerformance)
        assert result[0].campaign_id == "camp_001"
        assert result[0].trend == "improving"
        
        # Verify OpenAI was called with correct function
        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args.kwargs["functions"][0]["name"] == "analyze_campaigns"
    
    @pytest.mark.asyncio
    async def test_generate_optimization_suggestions(self, ai_engine, mock_openai_client):
        """Test optimization suggestion generation"""
        # Mock OpenAI response for optimization
        mock_openai_client.chat.completions.create.return_value.choices[0].message.function_call.arguments = json.dumps({
            "suggestions": [
                {
                    "type": "budget_reallocation",
                    "campaign_id": "camp_001",
                    "action": "Increase budget by 20%",
                    "predicted_impact": {
                        "roi_change": 15.0,
                        "conversion_change": 10.0,
                        "cost_change": 20.0
                    },
                    "confidence": 0.85,
                    "reasoning": "High performing campaign with room for growth",
                    "implementation_steps": ["Step 1", "Step 2"]
                }
            ],
            "budget_allocation": {"camp_001": 12000},
            "expected_overall_impact": {
                "total_roi": 4.5,
                "total_conversions": 150,
                "total_revenue": 7500
            }
        })
        
        campaigns = [
            CampaignPerformance(
                campaign_id="camp_001",
                campaign_name="Summer Sale",
                impressions=50000,
                clicks=1000,
                conversions=50,
                cost=500,
                revenue=2500,
                ctr=2.0,
                conversion_rate=5.0,
                roi=400.0,
                trend="improving"
            )
        ]
        
        result = await ai_engine.generate_optimization_suggestions(
            campaigns=campaigns,
            total_budget=10000,
            optimization_goal="maximize_roi"
        )
        
        assert len(result) == 1
        assert isinstance(result[0], OptimizationSuggestion)
        assert result[0].type == "budget_reallocation"
        assert result[0].confidence == 0.85
        assert result[0].predicted_impact["roi_change"] == 15.0
    
    @pytest.mark.asyncio
    async def test_create_personalized_ad_copy(self, ai_engine, mock_openai_client):
        """Test personalized ad copy generation"""
        # Mock OpenAI response for ad copy
        mock_openai_client.chat.completions.create.return_value.choices[0].message.function_call.arguments = json.dumps({
            "variants": [
                {
                    "headline": "Transform Your Marketing",
                    "description": "AI-powered automation that delivers results",
                    "call_to_action": "Start Free Trial",
                    "target_audience": "Marketing managers",
                    "tone": "professional",
                    "predicted_ctr": 3.5,
                    "keywords": ["AI", "automation", "marketing"]
                },
                {
                    "headline": "Boost ROI with AI",
                    "description": "Smart automation for modern marketers",
                    "call_to_action": "Get Started",
                    "target_audience": "Marketing managers",
                    "tone": "professional",
                    "predicted_ctr": 3.2,
                    "keywords": ["ROI", "AI", "automation"]
                }
            ],
            "recommendations": {
                "best_variant_index": 0,
                "a_b_test_suggestion": "Test both variants",
                "platform_specific_tips": ["Use sitelinks", "Add extensions"]
            }
        })
        
        result = await ai_engine.create_personalized_ad_copy(
            product_name="Marketing AI Platform",
            product_description="Automate your marketing with AI",
            target_audience={"role": "marketing manager", "company_size": "medium"},
            platform="google_ads",
            num_variants=2,
            tone="professional"
        )
        
        assert len(result) == 2
        assert all(isinstance(v, AdCopyVariant) for v in result)
        assert result[0].headline == "Transform Your Marketing"
        assert result[0].predicted_ctr == 3.5
        assert "AI" in result[0].keywords
    
    @pytest.mark.asyncio
    async def test_prompt_template_rendering(self, ai_engine):
        """Test prompt template system"""
        # Test campaign analysis template
        template = ai_engine.get_prompt_template("campaign_analysis")
        assert template.name == "campaign_analysis"
        assert template.category == DecisionType.CAMPAIGN_ANALYSIS
        
        # Test rendering with variables
        rendered = ai_engine.render_prompt(
            "campaign_analysis",
            campaign_data=[{"id": "test", "impressions": 1000}],
            start_date="2024-01-01",
            end_date="2024-01-31",
            benchmarks={"ctr": 2.0}
        )
        
        assert "test" in rendered
        assert "1000" in rendered
        assert "2024-01-01" in rendered
    
    @pytest.mark.asyncio
    async def test_prompt_chain_execution(self, ai_engine, mock_openai_client):
        """Test executing a prompt chain"""
        # Mock responses for each step
        mock_openai_client.chat.completions.create.side_effect = [
            # Step 1: Performance analysis
            Mock(choices=[Mock(message=Mock(function_call=Mock(arguments=json.dumps({
                "campaigns": [{"campaign_id": "camp_001", "trend": "improving"}],
                "summary": {"total_campaigns": 1}
            }))))]),
            # Step 2: Trend prediction
            Mock(choices=[Mock(message=Mock(content="Positive trend expected"))]),
            # Step 3: Optimization
            Mock(choices=[Mock(message=Mock(function_call=Mock(arguments=json.dumps({
                "suggestions": [{
                    "type": "budget_reallocation",
                    "campaign_id": "camp_001",
                    "action": "Increase budget",
                    "predicted_impact": {"roi_change": 10},
                    "confidence": 0.8,
                    "reasoning": "Good performance"
                }]
            }))))])
        ]
        
        result = await ai_engine.create_budget_reallocation_chain(
            campaigns=[{"campaign_id": "camp_001", "metrics": {"clicks": 100}}],
            total_budget=10000,
            business_goals={"primary_goal": "maximize_roi"}
        )
        
        assert result["chain_name"] == "budget_reallocation"
        assert len(result["steps"]) == 3
        assert "performance_analysis" in [s["step_name"] for s in result["steps"]]
        assert "trend_prediction" in [s["step_name"] for s in result["steps"]]
        assert "optimization" in [s["step_name"] for s in result["steps"]]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, ai_engine, mock_openai_client):
        """Test error handling in AI engine"""
        # Mock OpenAI to raise an error
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            await ai_engine.analyze_campaign_performance(
                campaigns=[],
                start_date=datetime.now(),
                end_date=datetime.now()
            )
    
    @pytest.mark.asyncio
    async def test_missing_template_variables(self, ai_engine):
        """Test error when missing required template variables"""
        with pytest.raises(ValueError, match="Missing required variables"):
            ai_engine.render_prompt(
                "campaign_analysis",
                campaign_data=[],  # Missing other required variables
            )


class TestAIDecisionTracking:
    """Test AI decision tracking functionality"""
    
    @pytest.mark.asyncio
    async def test_decision_success_calculation(self):
        """Test success score calculation for AI decisions"""
        from src.database import AIDecisionHistory
        
        decision = AIDecisionHistory(
            decision_id="dec_001",
            decision_type="budget_allocation",
            expected_impact={"conversions": 100, "roi": 3.0},
            actual_impact={"conversions": 110, "roi": 3.3}
        )
        
        decision.calculate_success_score()
        
        assert decision.success_score > 100  # Better than expected
        assert decision.success_score < 120  # But not unrealistically high
    
    @pytest.mark.asyncio
    async def test_decision_tracking_integration(self, test_db):
        """Test tracking AI decisions in database"""
        from src.database import DecisionType
        
        # Record a decision
        decision = test_db.record_ai_decision(
            decision_type=DecisionType.BUDGET_ALLOCATION,
            input_data={"current_budget": 1000},
            decision_made={"new_budget": 1200},
            confidence_score=0.85,
            reasoning="High performing campaign",
            expected_impact={"roi_increase": 15},
            campaign_id=None
        )
        
        assert decision.decision_id
        assert decision.confidence_score == 0.85
        
        # Update with actual outcome
        test_db.update_ai_decision_outcome(
            decision_id=decision.decision_id,
            actual_impact={"roi_increase": 18}
        )
        
        # Verify success score was calculated
        with test_db.get_session() as session:
            updated = session.query(test_db.__class__).filter_by(
                decision_id=decision.decision_id
            ).first()
            assert updated.success_score > 100  # Exceeded expectations