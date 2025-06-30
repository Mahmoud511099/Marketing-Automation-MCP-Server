"""Unit tests for API integrations with mocked external calls"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, AsyncMock
import os

from src.integrations.google_ads import GoogleAdsClient
from src.integrations.facebook_ads import FacebookAdsClient
from src.integrations.google_analytics import GoogleAnalyticsClient
from src.integrations.unified_client import UnifiedMarketingClient, Platform
from src.integrations.base import RateLimitError, AuthenticationError


class TestGoogleAdsClient:
    """Test Google Ads API client"""
    
    @pytest.fixture
    def google_ads_client(self):
        """Create Google Ads client with test credentials"""
        with patch.dict(os.environ, {
            'GOOGLE_ADS_DEVELOPER_TOKEN': 'test_token',
            'GOOGLE_ADS_CLIENT_ID': 'test_client_id',
            'GOOGLE_ADS_CLIENT_SECRET': 'test_secret',
            'GOOGLE_ADS_REFRESH_TOKEN': 'test_refresh',
            'GOOGLE_ADS_CUSTOMER_ID': '1234567890'
        }):
            return GoogleAdsClient()
    
    @pytest.mark.asyncio
    async def test_authentication_oauth(self, google_ads_client, mock_google_ads_client):
        """Test OAuth authentication"""
        await google_ads_client.connect()
        
        # Verify authentication was called
        assert google_ads_client._authenticated
        assert google_ads_client._access_token == "mock_token"
        
        # Verify refresh token was used
        mock_google_ads_client.post.assert_called_with(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "refresh_token": "test_refresh",
                "grant_type": "refresh_token"
            }
        )
    
    @pytest.mark.asyncio
    async def test_fetch_campaign_performance(self, google_ads_client, mock_google_ads_client):
        """Test fetching campaign performance data"""
        await google_ads_client.connect()
        
        result = await google_ads_client.fetch_campaign_performance(
            campaign_ids=["123456"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            metrics=["impressions", "clicks", "conversions", "cost"]
        )
        
        assert result["platform"] == "google_ads"
        assert len(result["data"]) > 0
        assert result["data"][0]["campaign_id"] == "123456"
        assert "metrics" in result["data"][0]
        
        # Verify API was called with correct query
        mock_google_ads_client.request.assert_called()
        call_args = mock_google_ads_client.request.call_args
        assert "searchStream" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_update_campaign_budget(self, google_ads_client, mock_google_ads_client):
        """Test updating campaign budget"""
        await google_ads_client.connect()
        
        # Mock campaign budget query response
        mock_google_ads_client.request.side_effect = [
            Mock(status_code=200, json=lambda: {
                "results": [{
                    "campaignBudget": {"id": "999"}
                }]
            }),
            Mock(status_code=200, json=lambda: {"results": []})
        ]
        
        result = await google_ads_client.update_campaign_budget(
            campaign_id="123456",
            new_budget=5000.0,
            budget_type="daily"
        )
        
        assert result["platform"] == "google_ads"
        assert result["campaign_id"] == "123456"
        assert result["new_budget"] == 5000.0
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_pause_campaign(self, google_ads_client, mock_google_ads_client):
        """Test pausing a campaign"""
        await google_ads_client.connect()
        
        result = await google_ads_client.pause_campaign("123456")
        
        assert result["platform"] == "google_ads"
        assert result["campaign_id"] == "123456"
        assert result["status"] == "paused"
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, google_ads_client, mock_google_ads_client):
        """Test rate limit error handling"""
        await google_ads_client.connect()
        
        # Mock rate limit response
        mock_google_ads_client.request.return_value = Mock(
            status_code=429,
            json=lambda: {"error": "Rate limit exceeded"}
        )
        
        with pytest.raises(RateLimitError):
            await google_ads_client.fetch_campaign_performance(
                campaign_ids=["123456"],
                start_date=datetime.now(),
                end_date=datetime.now(),
                metrics=["clicks"]
            )


class TestFacebookAdsClient:
    """Test Facebook Ads API client"""
    
    @pytest.fixture
    def facebook_ads_client(self):
        """Create Facebook Ads client with test credentials"""
        with patch.dict(os.environ, {
            'FACEBOOK_APP_ID': 'test_app_id',
            'FACEBOOK_APP_SECRET': 'test_secret',
            'FACEBOOK_ACCESS_TOKEN': 'test_token',
            'FACEBOOK_AD_ACCOUNT_ID': '1234567890'
        }):
            return FacebookAdsClient()
    
    @pytest.mark.asyncio
    async def test_fetch_campaign_performance(self, facebook_ads_client, mock_facebook_ads_client):
        """Test fetching campaign performance from Facebook"""
        await facebook_ads_client.connect()
        
        result = await facebook_ads_client.fetch_campaign_performance(
            campaign_ids=["789012"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            metrics=["impressions", "clicks", "conversions"]
        )
        
        assert result["platform"] == "facebook_ads"
        assert len(result["data"]) > 0
        assert result["data"][0]["campaign_id"] == "789012"
        
        # Verify correct API endpoint was called
        mock_facebook_ads_client.request.assert_called()
        call_args = mock_facebook_ads_client.request.call_args
        assert "/insights" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_update_campaign_budget(self, facebook_ads_client, mock_facebook_ads_client):
        """Test updating Facebook campaign budget"""
        await facebook_ads_client.connect()
        
        # Mock campaign and adset responses
        mock_facebook_ads_client.request.side_effect = [
            Mock(status_code=200, json=lambda: {
                "adsets": {
                    "data": [{"id": "adset_001"}]
                }
            }),
            Mock(status_code=200, json=lambda: {"success": True})
        ]
        
        result = await facebook_ads_client.update_campaign_budget(
            campaign_id="789012",
            new_budget=1000.0,
            budget_type="daily"
        )
        
        assert result["platform"] == "facebook_ads"
        assert result["campaign_id"] == "789012"
        assert result["new_budget"] == 1000.0
        assert len(result["updated_adsets"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_audience_insights(self, facebook_ads_client, mock_facebook_ads_client):
        """Test getting audience insights"""
        await facebook_ads_client.connect()
        
        # Mock custom audiences response
        mock_facebook_ads_client.request.return_value = Mock(
            status_code=200,
            json=lambda: {
                "data": [{
                    "id": "aud_001",
                    "name": "High Value Customers",
                    "approximate_count": 50000,
                    "operation_status": {"status": "NORMAL"}
                }]
            }
        )
        
        result = await facebook_ads_client.get_audience_insights()
        
        assert result["platform"] == "facebook_ads"
        assert len(result["audiences"]) > 0
        assert result["audiences"][0]["name"] == "High Value Customers"


class TestGoogleAnalyticsClient:
    """Test Google Analytics API client"""
    
    @pytest.fixture
    def ga_client(self):
        """Create Google Analytics client with test credentials"""
        with patch.dict(os.environ, {
            'GOOGLE_ANALYTICS_PROPERTY_ID': '123456789',
            'GOOGLE_ANALYTICS_CLIENT_ID': 'test_client_id',
            'GOOGLE_ANALYTICS_CLIENT_SECRET': 'test_secret',
            'GOOGLE_ANALYTICS_REFRESH_TOKEN': 'test_refresh'
        }):
            return GoogleAnalyticsClient()
    
    @pytest.mark.asyncio
    async def test_fetch_campaign_performance(self, ga_client, mock_google_ads_client):
        """Test fetching campaign data from GA4"""
        # Reuse Google Ads mock for OAuth
        await ga_client.connect()
        
        # Mock GA4 API response
        mock_google_ads_client.request.return_value = Mock(
            status_code=200,
            json=lambda: {
                "rows": [{
                    "dimensionValues": [
                        {"value": "camp_001"},
                        {"value": "Summer Campaign"},
                        {"value": "2024-01-15"}
                    ],
                    "metricValues": [
                        {"value": "1000"},  # sessions
                        {"value": "500"},   # users
                        {"value": "50"}     # conversions
                    ]
                }]
            }
        )
        
        result = await ga_client.fetch_campaign_performance(
            campaign_ids=["camp_001"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            metrics=["sessions", "users", "conversions"]
        )
        
        assert result["platform"] == "google_analytics"
        assert len(result["data"]) > 0
        assert result["data"][0]["campaign_id"] == "camp_001"
    
    @pytest.mark.asyncio
    async def test_read_only_operations(self, ga_client):
        """Test that GA client returns appropriate responses for write operations"""
        await ga_client.connect()
        
        # Test budget update (not supported)
        result = await ga_client.update_campaign_budget("camp_001", 1000)
        assert result["status"] == "not_supported"
        assert "read-only" in result["message"]
        
        # Test pause campaign (not supported)
        result = await ga_client.pause_campaign("camp_001")
        assert result["status"] == "not_supported"


class TestUnifiedMarketingClient:
    """Test unified marketing client"""
    
    @pytest.fixture
    async def unified_client(self):
        """Create unified client"""
        client = UnifiedMarketingClient()
        return client
    
    @pytest.mark.asyncio
    async def test_connect_all_platforms(self, unified_client):
        """Test connecting to all platforms"""
        with patch.object(unified_client.clients[Platform.GOOGLE_ADS], 'connect', new_callable=AsyncMock),\
             patch.object(unified_client.clients[Platform.FACEBOOK_ADS], 'connect', new_callable=AsyncMock),\
             patch.object(unified_client.clients[Platform.GOOGLE_ANALYTICS], 'connect', new_callable=AsyncMock):
            
            await unified_client.connect_all()
            
            # Verify all platforms attempted connection
            for platform in Platform:
                if platform != Platform.ALL:
                    unified_client.clients[platform].connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_campaign_performance_multi_platform(self, unified_client):
        """Test fetching data from multiple platforms"""
        # Mock individual client methods
        mock_results = {
            Platform.GOOGLE_ADS: {
                "platform": "google_ads",
                "data": [{"campaign_id": "g_001", "metrics": {"clicks": 100}}]
            },
            Platform.FACEBOOK_ADS: {
                "platform": "facebook_ads",
                "data": [{"campaign_id": "f_001", "metrics": {"clicks": 200}}]
            }
        }
        
        for platform, result in mock_results.items():
            unified_client.clients[platform].fetch_campaign_performance = AsyncMock(return_value=result)
            unified_client._connected_clients.add(platform)
        
        result = await unified_client.fetch_campaign_performance(
            campaign_ids=["g_001", "f_001"],
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            metrics=["clicks"],
            platforms=[Platform.GOOGLE_ADS, Platform.FACEBOOK_ADS]
        )
        
        assert "results" in result
        assert "google_ads" in result["results"]
        assert "facebook_ads" in result["results"]
        assert result["summary"]["combined_metrics"]["clicks"] == 300
    
    @pytest.mark.asyncio
    async def test_error_handling_partial_failure(self, unified_client):
        """Test handling when one platform fails"""
        # Mock Google Ads to succeed
        unified_client.clients[Platform.GOOGLE_ADS].fetch_campaign_performance = AsyncMock(
            return_value={"platform": "google_ads", "data": []}
        )
        unified_client._connected_clients.add(Platform.GOOGLE_ADS)
        
        # Mock Facebook to fail
        unified_client.clients[Platform.FACEBOOK_ADS].fetch_campaign_performance = AsyncMock(
            side_effect=Exception("Facebook API Error")
        )
        unified_client._connected_clients.add(Platform.FACEBOOK_ADS)
        
        result = await unified_client.fetch_campaign_performance(
            campaign_ids=["123"],
            start_date=datetime.now(),
            end_date=datetime.now(),
            metrics=["clicks"],
            platforms=[Platform.GOOGLE_ADS, Platform.FACEBOOK_ADS]
        )
        
        assert "google_ads" in result["results"]
        assert "facebook_ads" in result["errors"]
        assert "Facebook API Error" in result["errors"]["facebook_ads"]