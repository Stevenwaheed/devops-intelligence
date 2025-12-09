"""Flask extensions initialization."""
import os
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
import redis

# SQLAlchemy
db = SQLAlchemy()

# Cache
cache = Cache()

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Rate Limiter - use Redis database 3 for rate limiting
RATE_LIMIT_STORAGE = REDIS_URL.rsplit("/", 1)[0] + "/3"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=RATE_LIMIT_STORAGE,
)

# Celery
celery = Celery(
    "devguard",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Redis client
redis_client = redis.from_url(REDIS_URL)
