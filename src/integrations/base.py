"""Base integration client with common functionality"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import logging
from functools import wraps
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting"""
    requests_per_minute: int = Field(default=60)
    requests_per_hour: int = Field(default=1000)
    requests_per_day: int = Field(default=10000)
    retry_after_seconds: int = Field(default=60)
    max_retries: int = Field(default=3)


class APIError(Exception):
    """Base API error"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    pass


class AuthenticationError(APIError):
    """Authentication failed error"""
    pass


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.minute_bucket = []
        self.hour_bucket = []
        self.day_bucket = []
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self) -> bool:
        """Check if request can be made within rate limits"""
        async with self._lock:
            now = time.time()
            
            # Clean old entries
            minute_ago = now - 60
            hour_ago = now - 3600
            day_ago = now - 86400
            
            self.minute_bucket = [t for t in self.minute_bucket if t > minute_ago]
            self.hour_bucket = [t for t in self.hour_bucket if t > hour_ago]
            self.day_bucket = [t for t in self.day_bucket if t > day_ago]
            
            # Check limits
            if len(self.minute_bucket) >= self.config.requests_per_minute:
                return False
            if len(self.hour_bucket) >= self.config.requests_per_hour:
                return False
            if len(self.day_bucket) >= self.config.requests_per_day:
                return False
            
            # Add current request
            self.minute_bucket.append(now)
            self.hour_bucket.append(now)
            self.day_bucket.append(now)
            
            return True
    
    async def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        while not await self.check_rate_limit():
            await asyncio.sleep(self.config.retry_after_seconds)


def rate_limited(func: Callable) -> Callable:
    """Decorator for rate-limited methods"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        await self.rate_limiter.wait_if_needed()
        return await func(self, *args, **kwargs)
    return wrapper


def retry_on_error(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator for retrying failed requests"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                except RateLimitError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = e.response.get('retry_after', 60) if e.response else 60
                        logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                except AuthenticationError:
                    # Don't retry authentication errors
                    raise
            
            raise last_exception
        return wrapper
    return decorator


class BaseIntegrationClient(ABC):
    """Base class for all integration clients"""
    
    def __init__(self, rate_limit_config: Optional[RateLimitConfig] = None):
        self.rate_limiter = RateLimiter(rate_limit_config or RateLimitConfig())
        self._client: Optional[httpx.AsyncClient] = None
        self._authenticated = False
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP client and authenticate"""
        self._client = httpx.AsyncClient(timeout=30.0)
        await self.authenticate()
    
    async def disconnect(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self):
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate that credentials are working"""
        pass
    
    @rate_limited
    @retry_on_error()
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated HTTP request"""
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        if not self._authenticated:
            await self.authenticate()
        
        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            data=data
        )
        
        # Handle common error responses
        if response.status_code == 401:
            self._authenticated = False
            raise AuthenticationError("Authentication failed", response.status_code, response.json())
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", response.status_code, response.json())
        elif response.status_code >= 400:
            raise APIError(f"API error: {response.text}", response.status_code, response.json() if response.text else None)
        
        return response.json()
    
    # Abstract methods for common operations
    @abstractmethod
    async def fetch_campaign_performance(
        self,
        campaign_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Fetch campaign performance data"""
        pass
    
    @abstractmethod
    async def update_campaign_budget(
        self,
        campaign_id: str,
        new_budget: float,
        budget_type: str = "daily"
    ) -> Dict[str, Any]:
        """Update campaign budget"""
        pass
    
    @abstractmethod
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause a campaign"""
        pass
    
    @abstractmethod
    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Start/resume a campaign"""
        pass
    
    @abstractmethod
    async def get_audience_insights(
        self,
        audience_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get audience insights and demographics"""
        pass