"""
Industry-Level OTP Service Module with Redis Support

Features:
- Redis-based OTP storage for production scalability
- Rate limiting and brute-force protection
- Automatic cleanup of expired OTPs
- Multi-channel OTP delivery (email, SMS)
- Comprehensive audit logging
- Fallback to in-memory storage if Redis unavailable
"""

import secrets
import string
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass, asdict
import json
import hashlib
from threading import Lock

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OTPData:
    """OTP data structure."""
    otp_hash: str  # Store hash instead of plain OTP for security
    expires_at: float  # Unix timestamp
    attempts: int
    created_at: float
    delivery_channel: str  # 'email', 'sms', or 'both'
    user_identifier: str  # Email or phone number
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RedisOTPStorage:
    """Redis-based OTP storage with connection pooling."""
    
    def __init__(self):
        self.redis_client = None
        self.connected = False
        self._lock = Lock()
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with retry logic."""
        try:
            import redis
            from redis.connection import ConnectionPool
            
            # Create connection pool
            pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=10,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            self.redis_client = redis.Redis(connection_pool=pool)
            
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("Successfully connected to Redis for OTP storage")
            
        except ImportError:
            logger.warning("redis package not installed. Falling back to in-memory storage.")
            self.connected = False
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Falling back to in-memory storage.")
            self.connected = False
    
    def set(self, key: str, value: OTPData, expiry_seconds: int):
        """Store OTP data in Redis."""
        if not self.connected:
            return False
        
        try:
            data_json = json.dumps(asdict(value))
            self.redis_client.setex(key, expiry_seconds, data_json)
            return True
        except Exception as e:
            logger.error(f"Failed to store OTP in Redis: {e}")
            return False
    
    def get(self, key: str) -> Optional[OTPData]:
        """Retrieve OTP data from Redis."""
        if not self.connected:
            return None
        
        try:
            data_json = self.redis_client.get(key)
            if data_json:
                data_dict = json.loads(data_json)
                return OTPData(**data_dict)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve OTP from Redis: {e}")
            return None
    
    def delete(self, key: str):
        """Delete OTP data from Redis."""
        if not self.connected:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete OTP from Redis: {e}")
    
    def increment_attempts(self, key: str) -> int:
        """Increment attempt counter for an OTP."""
        if not self.connected:
            return -1
        
        try:
            data = self.get(key)
            if data:
                data.attempts += 1
                ttl = self.redis_client.ttl(key)
                if ttl > 0:
                    self.set(key, data, ttl)
                return data.attempts
            return -1
        except Exception as e:
            logger.error(f"Failed to increment OTP attempts: {e}")
            return -1
    
    def get_rate_limit_key(self, identifier: str, window: str) -> str:
        """Generate rate limit key for OTP requests."""
        return f"otp:ratelimit:{window}:{identifier}"
    
    def check_rate_limit(self, identifier: str, max_per_hour: int = 5, max_per_day: int = 10) -> tuple[bool, str]:
        """Check if user has exceeded OTP request rate limits."""
        if not self.connected:
            return True, "OK"  # Allow if Redis unavailable
        
        try:
            # Check hourly limit
            hourly_key = self.get_rate_limit_key(identifier, "hour")
            hourly_count = self.redis_client.get(hourly_key)
            
            if hourly_count and int(hourly_count) >= max_per_hour:
                return False, "Too many OTP requests. Please try again in an hour."
            
            # Check daily limit
            daily_key = self.get_rate_limit_key(identifier, "day")
            daily_count = self.redis_client.get(daily_key)
            
            if daily_count and int(daily_count) >= max_per_day:
                return False, "Daily OTP request limit exceeded. Please try again tomorrow."
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True, "OK"  # Allow on error
    
    def record_otp_request(self, identifier: str):
        """Record an OTP request for rate limiting."""
        if not self.connected:
            return
        
        try:
            # Increment hourly counter
            hourly_key = self.get_rate_limit_key(identifier, "hour")
            pipe = self.redis_client.pipeline()
            pipe.incr(hourly_key)
            pipe.expire(hourly_key, 3600)  # 1 hour
            
            # Increment daily counter
            daily_key = self.get_rate_limit_key(identifier, "day")
            pipe.incr(daily_key)
            pipe.expire(daily_key, 86400)  # 24 hours
            
            pipe.execute()
            
        except Exception as e:
            logger.error(f"Failed to record OTP request: {e}")


class InMemoryOTPStorage:
    """Fallback in-memory OTP storage."""
    
    def __init__(self):
        self.storage: Dict[str, OTPData] = {}
        self.rate_limits: Dict[str, list] = {}
        self._lock = Lock()
    
    def set(self, key: str, value: OTPData, expiry_seconds: int):
        """Store OTP data in memory."""
        with self._lock:
            self.storage[key] = value
        return True
    
    def get(self, key: str) -> Optional[OTPData]:
        """Retrieve OTP data from memory."""
        with self._lock:
            data = self.storage.get(key)
            if data and datetime.utcnow().timestamp() > data.expires_at:
                del self.storage[key]
                return None
            return data
    
    def delete(self, key: str):
        """Delete OTP data from memory."""
        with self._lock:
            if key in self.storage:
                del self.storage[key]
    
    def increment_attempts(self, key: str) -> int:
        """Increment attempt counter."""
        with self._lock:
            if key in self.storage:
                self.storage[key].attempts += 1
                return self.storage[key].attempts
            return -1
    
    def check_rate_limit(self, identifier: str, max_per_hour: int = 5, max_per_day: int = 10) -> tuple[bool, str]:
        """Check rate limits."""
        with self._lock:
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)
            
            if identifier not in self.rate_limits:
                self.rate_limits[identifier] = []
            
            # Clean old timestamps
            self.rate_limits[identifier] = [
                ts for ts in self.rate_limits[identifier] if ts > one_day_ago
            ]
            
            recent_requests = self.rate_limits[identifier]
            hourly_count = sum(1 for ts in recent_requests if ts > one_hour_ago)
            
            if hourly_count >= max_per_hour:
                return False, "Too many OTP requests. Please try again in an hour."
            
            if len(recent_requests) >= max_per_day:
                return False, "Daily OTP request limit exceeded. Please try again tomorrow."
            
            return True, "OK"
    
    def record_otp_request(self, identifier: str):
        """Record an OTP request."""
        with self._lock:
            if identifier not in self.rate_limits:
                self.rate_limits[identifier] = []
            self.rate_limits[identifier].append(datetime.utcnow())


class OTPServiceV2:
    """
    Industry-level OTP service with Redis support, rate limiting,
    and multi-channel delivery.
    """
    
    def __init__(self):
        # Configuration
        self.otp_length = settings.OTP_LENGTH
        self.otp_expiry_minutes = settings.OTP_EXPIRE_MINUTES
        self.max_attempts = settings.OTP_MAX_ATTEMPTS
        self.max_requests_per_hour = settings.OTP_MAX_REQUESTS_PER_HOUR
        self.max_requests_per_day = settings.OTP_MAX_REQUESTS_PER_DAY
        
        # Initialize storage (Redis with in-memory fallback)
        self.redis_storage = RedisOTPStorage()
        self.memory_storage = InMemoryOTPStorage()
        
        # Use Redis if available, otherwise in-memory
        self.storage = (
            self.redis_storage if self.redis_storage.connected 
            else self.memory_storage
        )
        
        # Metrics
        self.metrics = {
            "otps_generated": 0,
            "otps_validated": 0,
            "otps_failed": 0,
            "rate_limited": 0,
            "storage_type": "redis" if self.redis_storage.connected else "memory"
        }
        self._metrics_lock = Lock()
        
        logger.info(f"OTP Service initialized with {self.metrics['storage_type']} storage")
    
    @staticmethod
    def _hash_otp(otp: str) -> str:
        """Hash OTP for secure storage."""
        return hashlib.sha256(otp.encode()).hexdigest()
    
    @staticmethod
    def _generate_otp_code(length: int) -> str:
        """Generate a secure random OTP."""
        return "".join(secrets.choice(string.digits) for _ in range(length))
    
    def _get_otp_key(self, user_id: str | int, purpose: str = "password_reset") -> str:
        """Generate Redis/storage key for OTP."""
        return f"otp:{purpose}:{user_id}"
    
    def generate_otp(
        self,
        user_id: str | int,
        user_identifier: str,  # email or phone
        delivery_channel: Literal["email", "sms", "both"] = "email",
        purpose: str = "password_reset",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """
        Generate a new OTP for a user.
        
        Args:
            user_id: User's unique identifier
            user_identifier: Email or phone number
            delivery_channel: How OTP should be delivered
            purpose: Purpose of OTP (password_reset, login, etc.)
            ip_address: Client IP for security logging
            user_agent: Client user agent for security logging
        
        Returns:
            tuple: (success, message, otp_code)
        """
        try:
            # Check rate limits
            can_request, rate_limit_msg = self.storage.check_rate_limit(
                user_identifier,
                self.max_requests_per_hour,
                self.max_requests_per_day
            )
            
            if not can_request:
                with self._metrics_lock:
                    self.metrics["rate_limited"] += 1
                logger.warning(f"Rate limit exceeded for {user_identifier}: {rate_limit_msg}")
                return False, rate_limit_msg, None
            
            # Generate OTP
            otp_code = self._generate_otp_code(self.otp_length)
            otp_hash = self._hash_otp(otp_code)
            
            # Create OTP data
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=self.otp_expiry_minutes)
            
            otp_data = OTPData(
                otp_hash=otp_hash,
                expires_at=expires_at.timestamp(),
                attempts=0,
                created_at=now.timestamp(),
                delivery_channel=delivery_channel,
                user_identifier=user_identifier,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Store OTP
            key = self._get_otp_key(user_id, purpose)
            expiry_seconds = self.otp_expiry_minutes * 60
            
            success = self.storage.set(key, otp_data, expiry_seconds)
            
            if not success:
                logger.error(f"Failed to store OTP for user {user_id}")
                return False, "Failed to generate OTP. Please try again.", None
            
            # Record request for rate limiting
            self.storage.record_otp_request(user_identifier)
            
            # Update metrics
            with self._metrics_lock:
                self.metrics["otps_generated"] += 1
            
            logger.info(
                f"OTP generated for user {user_id} via {delivery_channel} "
                f"(purpose: {purpose}, IP: {ip_address})"
            )
            
            return True, "OTP generated successfully", otp_code
            
        except Exception as e:
            logger.error(f"Error generating OTP for user {user_id}: {e}")
            return False, "An error occurred while generating OTP", None
    
    def validate_otp(
        self,
        user_id: str | int,
        otp: str,
        purpose: str = "password_reset"
    ) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate an OTP for a user.
        
        Args:
            user_id: User's unique identifier
            otp: OTP to validate
            purpose: Purpose of OTP
        
        Returns:
            tuple: (is_valid, message, otp_metadata)
        """
        try:
            key = self._get_otp_key(user_id, purpose)
            otp_data = self.storage.get(key)
            
            if not otp_data:
                return False, "No OTP found or OTP has expired", None
            
            # Check expiration
            if datetime.utcnow().timestamp() > otp_data.expires_at:
                self.storage.delete(key)
                return False, "OTP has expired. Please request a new one.", None
            
            # Check attempts
            if otp_data.attempts >= self.max_attempts:
                self.storage.delete(key)
                with self._metrics_lock:
                    self.metrics["otps_failed"] += 1
                return False, "Maximum OTP verification attempts exceeded. Please request a new OTP.", None
            
            # Validate OTP
            otp_hash = self._hash_otp(otp)
            
            if otp_hash != otp_data.otp_hash:
                # Increment attempts
                new_attempts = self.storage.increment_attempts(key)
                if new_attempts == -1:
                    new_attempts = otp_data.attempts + 1
                
                remaining = self.max_attempts - new_attempts
                
                logger.warning(
                    f"Invalid OTP attempt for user {user_id} "
                    f"({new_attempts}/{self.max_attempts})"
                )
                
                return (
                    False,
                    f"Invalid OTP. You have {remaining} attempt(s) remaining.",
                    None
                )
            
            # OTP is valid
            metadata = {
                "delivery_channel": otp_data.delivery_channel,
                "user_identifier": otp_data.user_identifier,
                "created_at": datetime.fromtimestamp(otp_data.created_at).isoformat(),
                "validated_at": datetime.utcnow().isoformat()
            }
            
            with self._metrics_lock:
                self.metrics["otps_validated"] += 1
            
            logger.info(f"OTP validated successfully for user {user_id} (purpose: {purpose})")
            
            return True, "OTP validated successfully", metadata
            
        except Exception as e:
            logger.error(f"Error validating OTP for user {user_id}: {e}")
            return False, "An error occurred while validating OTP", None
    
    def clear_otp(self, user_id: str | int, purpose: str = "password_reset"):
        """Clear OTP for a user after successful validation."""
        try:
            key = self._get_otp_key(user_id, purpose)
            self.storage.delete(key)
            logger.info(f"OTP cleared for user {user_id} (purpose: {purpose})")
        except Exception as e:
            logger.error(f"Error clearing OTP for user {user_id}: {e}")
    
    def get_otp_status(
        self,
        user_id: str | int,
        purpose: str = "password_reset"
    ) -> Optional[Dict[str, Any]]:
        """Get OTP status for a user."""
        try:
            key = self._get_otp_key(user_id, purpose)
            otp_data = self.storage.get(key)
            
            if not otp_data:
                return None
            
            now = datetime.utcnow().timestamp()
            time_remaining = max(0, (otp_data.expires_at - now) / 60)
            
            return {
                "has_otp": True,
                "time_remaining_minutes": round(time_remaining, 2),
                "attempts_remaining": self.max_attempts - otp_data.attempts,
                "is_expired": now > otp_data.expires_at,
                "delivery_channel": otp_data.delivery_channel,
                "created_at": datetime.fromtimestamp(otp_data.created_at).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting OTP status for user {user_id}: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get OTP service metrics."""
        with self._metrics_lock:
            return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        with self._metrics_lock:
            storage_type = self.metrics["storage_type"]
            self.metrics = {
                "otps_generated": 0,
                "otps_validated": 0,
                "otps_failed": 0,
                "rate_limited": 0,
                "storage_type": storage_type
            }


# Create singleton instance
otp_service_v2 = OTPServiceV2()

# For backward compatibility
otp_service = otp_service_v2
