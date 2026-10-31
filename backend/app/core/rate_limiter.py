import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from backend.app.core.config import settings

# In-memory IP tracking fallback: {ip: (timestamp_window_start, request_count)}
_memory_rate_limit: Dict[str, Tuple[float, int]] = {}


async def check_rate_limit(request: Request) -> None:
    """Enforce rate limits per IP address using Redis or memory fallback."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    limit = settings.RATE_LIMIT_PER_MINUTE
    window = 60  # seconds

    if settings.REDIS_ENABLED:
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            key = f"rate_limit:{client_ip}"
            current = await r.incr(key)
            if current == 1:
                await r.expire(key, window)
            await r.close()
            if current > limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again in a minute."
                )
            return
        except HTTPException:
            raise
        except Exception:
            # Fall back to in-memory check if Redis temporarily fails
            pass

    # In-memory rate limiting
    now = time.time()
    if client_ip in _memory_rate_limit:
        start_time, count = _memory_rate_limit[client_ip]
        if now - start_time < window:
            if count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again in a minute."
                )
            _memory_rate_limit[client_ip] = (start_time, count + 1)
        else:
            _memory_rate_limit[client_ip] = (now, 1)
    else:
        _memory_rate_limit[client_ip] = (now, 1)

