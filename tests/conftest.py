"""Pytest configuration and shared fixtures"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import os
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Base, DatabaseManager, Campaign, AutomationTask, TaskType
from src.models import CampaignMetrics, OptimizationSuggestion, AdCopyVariant
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"
    
    # Create database manager
    db_manager = DatabaseManager(db_url)
    
    yield db_manager
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing"""
    return {
        "campaign_id": "camp_001",
        "name": "Summer Sale 2024",
        "platform": "google_ads",
        "status": "active",
        "budget": 10000.00,
        "start_date": datetime.now() - timedelta(days=30),
        "end_date": datetime.now() + timedelta(days=30)
    }


@pytest.fixture
def sample_performance_metrics():
    """Sample performance metrics for testing"""
    return [
        CampaignMetrics(
            campaign_id="camp_001",
            campaign_name="Summer Sale 2024",
            impressions=50000,
            clicks=1000,
            conversions=50,
            cost=500.0,
            revenue=2500.0,
            ctr=2.0,
            conversion_rate=5.0,
            roi=400.0,
            trend="improving"
        ),
        CampaignMetrics(
            campaign_id="camp_002",
            campaign_name="Fall Collection",
            impressions=30000,
            clicks=450,
            conversions=20,
            cost=300.0,
            revenue=1000.0,
            ctr=1.5,
            conversion_rate=4.4,
            roi=233.0,
            trend="stable"
        )
    ]


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for AI engine tests"""
    with patch('src.ai_engine.AsyncOpenAI') as mock_client:
        # Create mock response structure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.function_call.arguments = '''
        {
            "campaigns": [
                {
                    "campaign_id": "camp_001",
                    "campaign_name": "Summer Sale 2024",
                    "trend": "improving",
                    "issues": [],
                    "opportunities": ["Increase budget"]
                }
            ],
            "summary": {
                "total_campaigns": 1,
                "underperforming_count": 0,
                "top_performers": ["camp_001"],
                "key_insights": ["Campaign performing well"]
            }
        }
        '''
        
        # Set up async mock
        mock_instance = AsyncMock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def mock_google_ads_client():
    """Mock Google Ads API client"""
    with patch('src.integrations.google_ads.httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        
        # Mock authentication response
        mock_instance.post.return_value = Mock(
            status_code=200,
            json=lambda: {"access_token": "mock_token", "expires_in": 3600}
        )
        
        # Mock API responses
        mock_instance.request.return_value = Mock(
            status_code=200,
            json=lambda: {
                "results": [{
                    "campaign": {
                        "id": "123456",
                        "name": "Test Campaign",
                        "status": "ENABLED"
                    },
                    "metrics": {
                        "impressions": 10000,
                        "clicks": 200,
                        "conversions": 10,
                        "cost_micros": 500000000
                    }
                }]
            }
        )
        
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_facebook_ads_client():
    """Mock Facebook Ads API client"""
    with patch('src.integrations.facebook_ads.httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        
        # Mock API responses
        mock_instance.request.return_value = Mock(
            status_code=200,
            json=lambda: {
                "data": [{
                    "campaign_id": "789012",
                    "campaign_name": "Test FB Campaign",
                    "impressions": "15000",
                    "clicks": "300",
                    "spend": "600",
                    "conversions": 15
                }],
                "paging": {}
            }
        )
        
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_report_data():
    """Sample data for report generation tests"""
    return {
        "campaigns": [
            {
                "id": 1,
                "name": "Summer Sale",
                "status": "active",
                "budget": 5000
            }
        ],
        "performance_metrics": [
            {
                "impressions": 10000,
                "clicks": 200,
                "conversions": 10,
                "revenue": 1000,
                "cost": 200,
                "ctr": 2.0,
                "conversion_rate": 5.0
            }
        ],
        "automation_tasks": [
            {
                "task_type": TaskType.BUDGET_OPTIMIZATION,
                "time_saved_minutes": 30,
                "cost_saved": 25.0
            }
        ]
    }


@pytest.fixture
async def mcp_server():
    """Create MCP server instance for testing"""
    from src.server import MarketingAutomationServer
    server = MarketingAutomationServer()
    return server