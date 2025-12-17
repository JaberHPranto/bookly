import redis.asyncio as redis

from src.config import Config

JTI_EXPIRATION_SECONDS = 3600  # 1 hour

token_blocklist_redis = redis.from_url(Config.REDIS_URL, decode_responses=True)


async def add_token_to_blocklist(jti: str):
    await token_blocklist_redis.set(name=jti, value="", ex=JTI_EXPIRATION_SECONDS)


async def is_token_blocked(jti: str) -> bool:
    is_blocked = await token_blocklist_redis.get(jti)
    return is_blocked is not None
