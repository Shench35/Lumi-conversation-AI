import redis.asyncio as aioredis
from src.app.config import Config

JTI_EXPIRY = 3360

token_blocklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,  # Add timeout
    socket_timeout=5,
    retry_on_timeout=True
)

async def add_jti_to_blocklist(jti:str)->None:
    try:
        await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)
    except Exception as e:
        # Gracefully handle Redis unavailability
        print(f"Warning: Could not add token to blocklist: {e}")


async def token_in_blocklist(jti:str)->bool:
    try:
        jti=await token_blocklist.get(jti)
        return True if jti is not None else False
    except Exception as e:
        # Gracefully handle Redis unavailability
        print(f"Warning: Could not check token blocklist: {e}")
        return False