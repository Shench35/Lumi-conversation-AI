import redis.asyncio as aioredis
from src.app.services.config import Config
import logging

# Setup logging to see issues in Render logs
logger = logging.getLogger(__name__)

# JTI_EXPIRY should ideally match your JWT_ACCESS_TOKEN_EXPIRES
JTI_EXPIRY = 3600 

# Initialize Redis with Connection Pool for efficiency
token_blocklist = aioredis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    password=Config.REDIS_PASSWORD,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

async def add_jti_to_blocklist(jti: str) -> None:
    try:
        # We only need to store the key; value can be empty to save memory
        await token_blocklist.set(name=jti, value="1", ex=JTI_EXPIRY)
    except Exception as e:
        logger.error(f"Redis Error (add_jti): {e}")

async def token_in_blocklist(jti: str) -> bool:
    try:
        # exists() is faster than get() if you only care if it's there
        return await token_blocklist.exists(jti) > 0
    except Exception as e:
        logger.error(f"Redis Error (check_jti): {e}")
        return False
