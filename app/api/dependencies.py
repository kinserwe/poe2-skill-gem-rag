from fastapi import Depends, Request, HTTPException
from starlette import status

from app.rate_limiter import RateLimiter, get_limiter


def rate_limit(request: Request, limiter: RateLimiter = Depends(get_limiter)) -> None:
    if request.client is None:
        return

    result = limiter.check(request.client.host)
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
            headers={"Retry-After": str(result.retry_after)},
        )
