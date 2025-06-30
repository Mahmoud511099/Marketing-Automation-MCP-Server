"""Facebook Ads API client implementation"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode

from .base import (
    BaseIntegrationClient,
    RateLimitConfig,
    APIError,
    AuthenticationError,
    rate_limited,
    retry_on_error
)

logger = logging.getLogger(__name__)


class FacebookAdsClient(BaseIntegrationClient):
    """Facebook Ads API client with authentication and rate limiting"""
    
    API_VERSION = "v18.0"
    BASE_URL = "https://graph.facebook.com"
    
    def __init__(self):
        # Facebook has different rate limits per tier
        rate_config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1800,
            requests_per_day=40000
        )
        super().__init__(rate_config)
        
        # Load credentials from environment
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
        
        # Ensure ad account ID has correct format
        if self.ad_account_id and not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"
    
    async def authenticate(self):
        """Authenticate with Facebook Ads API"""
        if not all([self.app_id, self.access_token, self.ad_account_id]):
            raise AuthenticationError("Missing required Facebook Ads credentials")
        
        # For Facebook, we can use long-lived access tokens
        # In production, implement token refresh logic
        self._authenticated = True
    
    async def validate_credentials(self) -> bool:
        """Validate Facebook Ads credentials"""
        try:
            # Try to fetch ad account info
            url = f"{self.BASE_URL}/{self.API_VERSION}/{self.ad_account_id}"
            params = {
                "access_token": self.access_token,
                "fields": "id,name,account_status"
            }
            
            response = await self._make_request("GET", url, params=params)
            return response.get("account_status") == 1  # 1 = Active
        except Exception as e:
            logger.error(f"Facebook Ads credential validation failed: {e}")
            return False
    
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL"""
        return f"{self.BASE_URL}/{self.API_VERSION}/{endpoint}"
    
    def _get_default_params(self) -> Dict[str, str]:
        """Get default parameters including access token"""
        return {"access_token": self.access_token}
    
    @rate_limited
    @retry_on_error()
    async def fetch_campaign_performance(
        self,
        campaign_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Fetch campaign performance data from Facebook Ads"""
        
        # Map generic metrics to Facebook metrics
        metric_mapping = {
            "impressions": "impressions",
            "clicks": "clicks",
            "conversions": "conversions",
            "cost": "spend",
            "ctr": "ctr",
            "conversion_rate": "conversion_rate_ranking",
            "reach": "reach",
            "frequency": "frequency",
            "cpm": "cpm",
            "cpc": "cpc"
        }
        
        fb_metrics = [metric_mapping.get(m, m) for m in metrics]
        
        # Build insights request
        insights_data = []
        
        for campaign_id in campaign_ids:
            url = self._build_url(f"{campaign_id}/insights")
            
            params = {
                **self._get_default_params(),
                "fields": ",".join(fb_metrics + ["campaign_id", "campaign_name", "date_start", "date_stop"]),
                "time_range": json.dumps({
                    "since": start_date.strftime("%Y-%m-%d"),
                    "until": end_date.strftime("%Y-%m-%d")
                }),
                "level": "campaign",
                "time_increment": 1  # Daily breakdown
            }
            
            response = await self._make_request("GET", url, params=params)
            
            # Process response data
            for insight in response.get("data", []):
                result = {
                    "campaign_id": insight.get("campaign_id"),
                    "campaign_name": insight.get("campaign_name"),
                    "date": insight.get("date_start"),
                    "metrics": {}
                }
                
                for metric in metrics:
                    fb_metric = metric_mapping.get(metric, metric)
                    value = insight.get(fb_metric, 0)
                    
                    # Convert string numbers to float
                    if isinstance(value, str) and value.replace(".", "").isdigit():
                        value = float(value)
                    
                    result["metrics"][metric] = value
                
                insights_data.append(result)
            
            # Handle pagination if needed
            if "paging" in response and "next" in response["paging"]:
                # In production, implement pagination handling
                pass
        
        return {
            "platform": "facebook_ads",
            "data": insights_data,
            "total_results": len(insights_data),
            "query_date": datetime.utcnow().isoformat()
        }
    
    @rate_limited
    @retry_on_error()
    async def update_campaign_budget(
        self,
        campaign_id: str,
        new_budget: float,
        budget_type: str = "daily"
    ) -> Dict[str, Any]:
        """Update campaign budget in Facebook Ads"""
        
        # First, get the campaign details to find the adset
        campaign_url = self._build_url(campaign_id)
        campaign_params = {
            **self._get_default_params(),
            "fields": "adsets{id,daily_budget,lifetime_budget}"
        }
        
        campaign_response = await self._make_request("GET", campaign_url, params=campaign_params)
        
        if not campaign_response.get("adsets", {}).get("data"):
            raise APIError(f"No adsets found for campaign {campaign_id}")
        
        # Update budget for all adsets in the campaign
        updated_adsets = []
        
        for adset in campaign_response["adsets"]["data"]:
            adset_id = adset["id"]
            url = self._build_url(adset_id)
            
            # Facebook uses cents for budget
            budget_cents = int(new_budget * 100)
            
            data = {
                "access_token": self.access_token
            }
            
            if budget_type == "daily":
                data["daily_budget"] = budget_cents
            else:
                data["lifetime_budget"] = budget_cents
            
            response = await self._make_request("POST", url, data=data)
            
            updated_adsets.append({
                "adset_id": adset_id,
                "status": "updated"
            })
        
        return {
            "platform": "facebook_ads",
            "campaign_id": campaign_id,
            "updated_adsets": updated_adsets,
            "new_budget": new_budget,
            "budget_type": budget_type,
            "status": "updated",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @rate_limited
    @retry_on_error()
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause a Facebook Ads campaign"""
        return await self._update_campaign_status(campaign_id, "PAUSED")
    
    @rate_limited
    @retry_on_error()
    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Start/resume a Facebook Ads campaign"""
        return await self._update_campaign_status(campaign_id, "ACTIVE")
    
    async def _update_campaign_status(self, campaign_id: str, status: str) -> Dict[str, Any]:
        """Update campaign status"""
        url = self._build_url(campaign_id)
        
        data = {
            "access_token": self.access_token,
            "status": status
        }
        
        response = await self._make_request("POST", url, data=data)
        
        return {
            "platform": "facebook_ads",
            "campaign_id": campaign_id,
            "status": status.lower(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @rate_limited
    @retry_on_error()
    async def get_audience_insights(
        self,
        audience_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get audience insights from Facebook Ads"""
        
        insights_data = {
            "platform": "facebook_ads",
            "audiences": [],
            "demographic_insights": {},
            "interest_insights": {},
            "behavioral_insights": {}
        }
        
        # If specific audience ID provided, get custom audience details
        if audience_id:
            url = self._build_url(audience_id)
            params = {
                **self._get_default_params(),
                "fields": "id,name,description,approximate_count,operation_status,data_source,lookalike_spec"
            }
            
            response = await self._make_request("GET", url, params=params)
            
            insights_data["audiences"].append({
                "id": response.get("id"),
                "name": response.get("name"),
                "description": response.get("description"),
                "size": response.get("approximate_count", 0),
                "status": response.get("operation_status", {}).get("status"),
                "source": response.get("data_source", {}).get("type")
            })
        else:
            # Get all custom audiences
            url = self._build_url(f"{self.ad_account_id}/customaudiences")
            params = {
                **self._get_default_params(),
                "fields": "id,name,description,approximate_count,operation_status",
                "limit": 100
            }
            
            response = await self._make_request("GET", url, params=params)
            
            for audience in response.get("data", []):
                insights_data["audiences"].append({
                    "id": audience.get("id"),
                    "name": audience.get("name"),
                    "description": audience.get("description"),
                    "size": audience.get("approximate_count", 0),
                    "status": audience.get("operation_status", {}).get("status")
                })
        
        # Get audience insights if filters provided
        if filters:
            insights_url = self._build_url(f"{self.ad_account_id}/insights")
            
            # Build targeting spec based on filters
            targeting_spec = {}
            
            if filters.get("age_min") or filters.get("age_max"):
                targeting_spec["age_min"] = filters.get("age_min", 18)
                targeting_spec["age_max"] = filters.get("age_max", 65)
            
            if filters.get("genders"):
                targeting_spec["genders"] = filters["genders"]
            
            if filters.get("locations"):
                targeting_spec["geo_locations"] = {
                    "countries": filters.get("locations", [])
                }
            
            if filters.get("interests"):
                targeting_spec["interests"] = [
                    {"id": interest_id, "name": interest_name}
                    for interest_id, interest_name in filters["interests"].items()
                ]
            
            params = {
                **self._get_default_params(),
                "fields": "reach,impressions,clicks,spend,actions",
                "date_preset": "last_30d",
                "level": "account",
                "targeting_spec": json.dumps(targeting_spec) if targeting_spec else None
            }
            
            insights_response = await self._make_request("GET", insights_url, params=params)
            
            if insights_response.get("data"):
                data = insights_response["data"][0]
                
                # Extract demographic insights
                insights_data["demographic_insights"] = {
                    "reach": data.get("reach", 0),
                    "impressions": data.get("impressions", 0),
                    "clicks": data.get("clicks", 0),
                    "spend": float(data.get("spend", 0)),
                    "targeting_spec": targeting_spec
                }
        
        # Get interest categories if requested
        if filters and filters.get("include_interests"):
            interests_url = self._build_url("search")
            params = {
                **self._get_default_params(),
                "type": "adinterest",
                "q": filters.get("interest_query", "marketing"),
                "limit": 20
            }
            
            interests_response = await self._make_request("GET", interests_url, params=params)
            
            insights_data["interest_insights"] = {
                "available_interests": [
                    {
                        "id": interest.get("id"),
                        "name": interest.get("name"),
                        "audience_size": interest.get("audience_size", 0),
                        "topic": interest.get("topic")
                    }
                    for interest in interests_response.get("data", [])
                ]
            }
        
        insights_data["total_audiences"] = len(insights_data["audiences"])
        insights_data["retrieved_at"] = datetime.utcnow().isoformat()
        
        return insights_data