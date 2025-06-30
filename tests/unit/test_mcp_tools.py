"""Unit tests for MCP marketing automation tools"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock

from src.tools.marketing_tools import (
    generate_campaign_report,
    optimize_campaign_budget,
    create_campaign_copy,
    analyze_audience_segments
)
from src.models import (
    GenerateCampaignReportInput,
    OptimizeCampaignBudgetInput,
    CreateCampaignCopyInput,
    AnalyzeAudienceSegmentsInput,
    ReportFormat,
    ToneOfVoice,
    SegmentCriteria
)


class TestGenerateCampaignReport:
    """Test campaign report generation tool"""
    
    @pytest.mark.asyncio
    async def test_generate_campaign_report_success(self):
        """Test successful campaign report generation"""
        # Prepare input
        input_data = GenerateCampaignReportInput(
            campaign_ids=["camp_001", "camp_002"],
            date_range={
                "start": "2024-01-01",
                "end": "2024-01-31"
            },
            metrics=["impressions", "clicks", "conversions", "ctr"],
            format=ReportFormat.JSON,
            include_charts=True,
            group_by="campaign"
        )
        
        # Execute
        result = await generate_campaign_report(input_data)
        
        # Verify
        assert result.report_id
        assert result.format == ReportFormat.JSON
        assert len(result.campaigns) == 2
        assert result.summary
        assert result.charts is not None
        
        # Check campaign metrics
        for campaign in result.campaigns:
            assert campaign.campaign_id in ["camp_001", "camp_002"]
            assert campaign.impressions > 0
            assert campaign.clicks > 0
            assert campaign.ctr > 0
    
    @pytest.mark.asyncio
    async def test_generate_campaign_report_pdf_format(self):
        """Test report generation with PDF format"""
        input_data = GenerateCampaignReportInput(
            campaign_ids=["camp_001"],
            date_range={"start": "2024-01-01", "end": "2024-01-31"},
            metrics=["impressions", "clicks"],
            format=ReportFormat.PDF,
            include_charts=False
        )
        
        result = await generate_campaign_report(input_data)
        
        assert result.format == ReportFormat.PDF
        assert result.download_url is not None
        assert result.charts is None
    
    @pytest.mark.asyncio
    async def test_generate_campaign_report_validation_error(self):
        """Test report generation with invalid date range"""
        with pytest.raises(ValueError, match="date_range must have 'start' and 'end' keys"):
            GenerateCampaignReportInput(
                campaign_ids=["camp_001"],
                date_range={"start": "2024-01-01"},  # Missing 'end'
                metrics=["clicks"]
            )


class TestOptimizeCampaignBudget:
    """Test campaign budget optimization tool"""
    
    @pytest.mark.asyncio
    async def test_optimize_budget_maximize_roi(self):
        """Test budget optimization for maximizing ROI"""
        # Mock campaign performance data
        campaigns = [
            Mock(campaign_id="camp_001", campaign_name="High ROI Campaign", 
                 ctr=3.5, conversion_rate=6.0, roi=500),
            Mock(campaign_id="camp_002", campaign_name="Low ROI Campaign",
                 ctr=1.5, conversion_rate=2.0, roi=150)
        ]
        
        input_data = OptimizeCampaignBudgetInput(
            campaign_ids=["camp_001", "camp_002"],
            total_budget=10000,
            optimization_goal="maximize_roi",
            historical_days=30,
            include_projections=True
        )
        
        result = await optimize_campaign_budget(input_data)
        
        # Verify
        assert result.optimization_id
        assert result.total_budget == 10000
        assert len(result.allocations) == 2
        assert result.confidence_score > 0
        assert len(result.recommendations) > 0
        
        # Check that high ROI campaign gets more budget
        high_roi_alloc = next(a for a in result.allocations if a.campaign_id == "camp_001")
        low_roi_alloc = next(a for a in result.allocations if a.campaign_id == "camp_002")
        assert high_roi_alloc.recommended_budget > low_roi_alloc.recommended_budget
    
    @pytest.mark.asyncio
    async def test_optimize_budget_with_constraints(self):
        """Test budget optimization with constraints"""
        input_data = OptimizeCampaignBudgetInput(
            campaign_ids=["camp_001", "camp_002"],
            total_budget=10000,
            optimization_goal="maximize_conversions",
            constraints={
                "camp_001": {"min": 2000, "max": 6000},
                "camp_002": {"min": 1000, "max": 4000}
            }
        )
        
        result = await optimize_campaign_budget(input_data)
        
        # Verify constraints are respected
        for allocation in result.allocations:
            if allocation.campaign_id in input_data.constraints:
                constraints = input_data.constraints[allocation.campaign_id]
                assert allocation.recommended_budget >= constraints.get("min", 0)
                assert allocation.recommended_budget <= constraints.get("max", float('inf'))
        
        # Verify total equals input budget
        total_allocated = sum(a.recommended_budget for a in result.allocations)
        assert abs(total_allocated - input_data.total_budget) < 1  # Allow small rounding difference


class TestCreateCampaignCopy:
    """Test campaign copy generation tool"""
    
    @pytest.mark.asyncio
    async def test_create_ad_copy_google_ads(self):
        """Test ad copy generation for Google Ads"""
        input_data = CreateCampaignCopyInput(
            product_name="Marketing Automation Platform",
            product_description="AI-powered platform that automates marketing tasks and increases ROI",
            target_audience="Marketing managers at medium-sized businesses",
            tone=ToneOfVoice.PROFESSIONAL,
            copy_type="ad_headline",
            variants_count=3,
            keywords=["automation", "ROI", "AI"],
            max_length=30
        )
        
        result = await create_campaign_copy(input_data)
        
        # Verify
        assert result.copy_generation_id
        assert result.copy_type == "ad_headline"
        assert len(result.variants) == 3
        assert result.tone == ToneOfVoice.PROFESSIONAL
        
        # Check each variant
        for variant in result.variants:
            assert len(variant.headline) <= 30
            assert variant.predicted_ctr > 0
            assert input_data.product_name in variant.headline
            # Check at least one keyword is used
            assert any(kw.lower() in variant.headline.lower() for kw in input_data.keywords)
    
    @pytest.mark.asyncio
    async def test_create_email_copy(self):
        """Test email copy generation"""
        input_data = CreateCampaignCopyInput(
            product_name="Summer Sale",
            product_description="50% off on all products",
            target_audience="Existing customers",
            tone=ToneOfVoice.CASUAL,
            copy_type="email_body",
            variants_count=2,
            call_to_action="Shop Now"
        )
        
        result = await create_campaign_copy(input_data)
        
        assert len(result.variants) == 2
        for variant in result.variants:
            assert variant.call_to_action == "Shop Now"
            assert input_data.product_name in variant.description
            assert variant.tone == ToneOfVoice.CASUAL


class TestAnalyzeAudienceSegments:
    """Test audience segmentation tool"""
    
    @pytest.mark.asyncio
    async def test_analyze_segments_demographics(self):
        """Test audience segmentation by demographics"""
        input_data = AnalyzeAudienceSegmentsInput(
            contact_list_id=��list_001",
            criteria=[SegmentCriteria.DEMOGRAPHICS, SegmentCriteria.BEHAVIOR],
            min_segment_size=100,
            max_segments=5,
            include_recommendations=True,
            analyze_overlap=True
        )
        
        result = await analyze_audience_segments(input_data)
        
        # Verify
        assert result.analysis_id
        assert result.total_contacts > 0
        assert len(result.segments) <= 5
        assert all(s.size >= 100 for s in result.segments)
        assert len(result.recommendations) > 0
        assert len(result.insights) > 0
        
        # Check segments have required fields
        for segment in result.segments:
            assert segment.segment_id
            assert segment.name
            assert segment.engagement_score >= 0
            assert segment.value_score >= 0
            assert len(segment.recommended_campaigns) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_segments_with_overlap(self):
        """Test segment overlap analysis"""
        input_data = AnalyzeAudienceSegmentsInput(
            contact_list_id="list_001",
            criteria=[SegmentCriteria.ENGAGEMENT, SegmentCriteria.PURCHASE_HISTORY],
            min_segment_size=50,
            max_segments=3,
            analyze_overlap=True
        )
        
        result = await analyze_audience_segments(input_data)
        
        # Verify overlaps are calculated
        if len(result.segments) > 1 and result.overlaps:
            for overlap in result.overlaps:
                assert overlap.segment_a_id
                assert overlap.segment_b_id
                assert overlap.overlap_count >= 0
                assert 0 <= overlap.overlap_percentage <= 100


class TestToolIntegration:
    """Test integration between different tools"""
    
    @pytest.mark.asyncio
    async def test_report_to_optimization_flow(self):
        """Test flow from report generation to budget optimization"""
        # Generate report
        report_input = GenerateCampaignReportInput(
            campaign_ids=["camp_001", "camp_002"],
            date_range={"start": "2024-01-01", "end": "2024-01-31"},
            metrics=["conversions", "roi", "ctr"],
            format=ReportFormat.JSON
        )
        
        report_result = await generate_campaign_report(report_input)
        
        # Use report data for optimization
        campaign_ids = [c.campaign_id for c in report_result.campaigns]
        
        optimization_input = OptimizeCampaignBudgetInput(
            campaign_ids=campaign_ids,
            total_budget=15000,
            optimization_goal="maximize_roi"
        )
        
        optimization_result = await optimize_campaign_budget(optimization_input)
        
        # Verify flow works
        assert len(optimization_result.allocations) == len(report_result.campaigns)
        assert all(a.campaign_id in campaign_ids for a in optimization_result.allocations)