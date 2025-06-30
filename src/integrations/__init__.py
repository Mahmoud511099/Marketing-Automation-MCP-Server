"""Marketing platform integrations module"""

from .unified_client import UnifiedMarketingClient
from .google_ads import GoogleAdsClient
from .facebook_ads import FacebookAdsClient
from .google_analytics import GoogleAnalyticsClient

__all__ = [
    "UnifiedMarketingClient",
    "GoogleAdsClient",
    "FacebookAdsClient",
    "GoogleAnalyticsClient"
]