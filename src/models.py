"""Pydantic models for marketing automation tools"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class ReportFormat(str, Enum):
    """Supported report formats"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class MetricType(str, Enum):
    """Types of marketing metrics"""
    OPENS = "opens"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    CTR = "ctr"
    CONVERSION_RATE = "conversion_rate"
    ROI = "roi"
    ENGAGEMENT_RATE = "engagement_rate"


class CampaignStatus(str, Enum):
    """Campaign status types"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ToneOfVoice(str, Enum):
    """Marketing copy tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"


class SegmentCriteria(str, Enum):
    """Audience segmentation criteria"""
    DEMOGRAPHICS = "demographics"
    BEHAVIOR = "behavior"
    ENGAGEMENT = "engagement"
    PURCHASE_HISTORY = "purchase_history"
    INTERESTS = "interests"
    LOCATION = "location"


# Input Models
class GenerateCampaignReportInput(BaseModel):
    """Input schema for generate_campaign_report tool"""
    campaign_ids: List[str] = Field(..., description="List of campaign IDs to include in report")
    date_range: Dict[str, str] = Field(..., description="Date range with 'start' and 'end' keys (ISO format)")
    metrics: List[MetricType] = Field(..., description="Metrics to include in the report")
    format: ReportFormat = Field(default=ReportFormat.JSON, description="Output format for the report")
    include_charts: bool = Field(default=True, description="Whether to include visual charts")
    group_by: Optional[str] = Field(None, description="Group results by: 'day', 'week', 'month', or 'campaign'")
    
    @validator('date_range')
    def validate_date_range(cls, v):
        if 'start' not in v or 'end' not in v:
            raise ValueError("date_range must have 'start' and 'end' keys")
        try:
            datetime.fromisoformat(v['start'])
            datetime.fromisoformat(v['end'])
        except:
            raise ValueError("Dates must be in ISO format")
        return v


class OptimizeCampaignBudgetInput(BaseModel):
    """Input schema for optimize_campaign_budget tool"""
    campaign_ids: List[str] = Field(..., description="Campaign IDs to optimize")
    total_budget: float = Field(..., gt=0, description="Total budget to allocate")
    optimization_goal: str = Field(..., description="Goal: 'maximize_conversions', 'maximize_roi', 'maximize_reach'")
    constraints: Optional[Dict[str, Any]] = Field(default={}, description="Budget constraints per campaign")
    historical_days: int = Field(default=30, ge=7, description="Days of historical data to analyze")
    include_projections: bool = Field(default=True, description="Include performance projections")


class CreateCampaignCopyInput(BaseModel):
    """Input schema for create_campaign_copy tool"""
    product_name: str = Field(..., description="Name of the product/service")
    product_description: str = Field(..., description="Description of the product/service")
    target_audience: str = Field(..., description="Target audience description")
    tone: ToneOfVoice = Field(..., description="Desired tone of voice")
    copy_type: str = Field(..., description="Type: 'email_subject', 'email_body', 'ad_headline', 'ad_copy', 'social_post'")
    variants_count: int = Field(default=3, ge=1, le=10, description="Number of copy variants to generate")
    keywords: Optional[List[str]] = Field(default=[], description="Keywords to include")
    max_length: Optional[int] = Field(None, description="Maximum character/word count")
    call_to_action: Optional[str] = Field(None, description="Specific CTA to include")


class AnalyzeAudienceSegmentsInput(BaseModel):
    """Input schema for analyze_audience_segments tool"""
    contact_list_id: str = Field(..., description="ID of the contact list to analyze")
    criteria: List[SegmentCriteria] = Field(..., description="Criteria to use for segmentation")
    min_segment_size: int = Field(default=100, ge=10, description="Minimum contacts per segment")
    max_segments: int = Field(default=10, ge=2, le=20, description="Maximum number of segments to create")
    include_recommendations: bool = Field(default=True, description="Include targeting recommendations")
    analyze_overlap: bool = Field(default=True, description="Analyze overlap between segments")


# Output Models
class CampaignMetrics(BaseModel):
    """Campaign performance metrics"""
    campaign_id: str
    campaign_name: str
    sent: int
    delivered: int
    opens: int
    unique_opens: int
    clicks: int
    unique_clicks: int
    conversions: int
    revenue: float
    ctr: float
    conversion_rate: float
    roi: float


class GenerateCampaignReportOutput(BaseModel):
    """Output schema for generate_campaign_report tool"""
    report_id: str
    generated_at: datetime
    date_range: Dict[str, str]
    campaigns: List[CampaignMetrics]
    summary: Dict[str, Any]
    charts: Optional[List[Dict[str, Any]]] = None
    format: ReportFormat
    download_url: Optional[str] = None


class BudgetAllocation(BaseModel):
    """Budget allocation for a campaign"""
    campaign_id: str
    campaign_name: str
    current_budget: float
    recommended_budget: float
    change_percentage: float
    expected_impact: Dict[str, float]
    reasoning: str


class OptimizeCampaignBudgetOutput(BaseModel):
    """Output schema for optimize_campaign_budget tool"""
    optimization_id: str
    total_budget: float
    optimization_goal: str
    allocations: List[BudgetAllocation]
    projected_improvement: Dict[str, float]
    confidence_score: float
    recommendations: List[str]


class CopyVariant(BaseModel):
    """A single copy variant"""
    variant_id: str
    content: str
    tone_match_score: float
    predicted_ctr: Optional[float] = None
    key_elements: List[str]
    character_count: int
    word_count: int


class CreateCampaignCopyOutput(BaseModel):
    """Output schema for create_campaign_copy tool"""
    copy_generation_id: str
    copy_type: str
    variants: List[CopyVariant]
    tone: ToneOfVoice
    target_audience: str
    keywords_used: List[str]
    best_variant_id: str
    generation_metadata: Dict[str, Any]


class AudienceSegment(BaseModel):
    """A single audience segment"""
    segment_id: str
    name: str
    size: int
    criteria: Dict[str, Any]
    characteristics: Dict[str, Any]
    engagement_score: float
    value_score: float
    recommended_campaigns: List[str]


class SegmentOverlap(BaseModel):
    """Overlap information between segments"""
    segment_a_id: str
    segment_b_id: str
    overlap_count: int
    overlap_percentage: float


class AnalyzeAudienceSegmentsOutput(BaseModel):
    """Output schema for analyze_audience_segments tool"""
    analysis_id: str
    total_contacts: int
    segments: List[AudienceSegment]
    uncategorized_count: int
    overlaps: Optional[List[SegmentOverlap]] = None
    recommendations: List[Dict[str, Any]]
    insights: List[str]
    created_at: datetime