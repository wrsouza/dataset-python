"""TokenBucketRateLimiter — Redis-backed implementation of RateLimiter.

Uses a single Lua script executed atomically server-side in Redis (EVAL) so
the "read remaining tokens, refill, consume one" sequence cannot race across
concurrent gRPC calls for the same client_id. This is one concrete strategy;
swapping it for a SlidingWindowRateLimiter requires no change to the Proxy
(OCP) because both implement the same `RateLimiter` Protocol.
"""

from __future__ import annotations

import time

import redis.asyncio as redis

from rate_limiting.domain.entities import RateLimitConfig, RateLimitResult

# KEYS[1] = bucket key
# ARGV[1] = max_requests (bucket capacity)
# ARGV[2] = window_seconds (time to fully refill the bucket)
# ARGV[3] = now (unix seconds, float)
#
# Stored hash fields: "tokens" (float) and "ts" (float, last refill time).
# On first access the bucket starts full.
_TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(bucket[1])
local last_ts = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_ts = now
end

local refill_rate = capacity / window
local elapsed = math.max(0, now - last_ts)
tokens = math.min(capacity, tokens + elapsed * refill_rate)

local allowed = 0
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

redis.call("HMSET", key, "tokens", tokens, "ts", now)
redis.call("EXPIRE", key, window * 2)

local retry_after = 0
if allowed == 0 then
    retry_after = (1 - tokens) / refill_rate
end

return {allowed, tostring(tokens), tostring(retry_after)}
"""


class TokenBucketRateLimiter:
    """RateLimiter strategy implementing the token bucket algorithm.

    Each client_id maps to one Redis hash key storing its current token
    count and last-refill timestamp. Tokens are replenished continuously
    (capacity / window_seconds per second) rather than reset all-at-once,
    which smooths out bursts at window boundaries.
    """

    _KEY_PREFIX = "rate_limit:token_bucket:"

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def check_and_consume(
        self, client_id: str, config: RateLimitConfig
    ) -> RateLimitResult:
        """Atomically consume one token for client_id, refilling as needed."""
        key = f"{self._KEY_PREFIX}{client_id}"
        now = time.time()
        # EVAL (rather than EVALSHA via register_script) is used directly so
        # this also works against minimal Redis-compatible test doubles that
        # don't implement server-side script caching.
        allowed_flag, tokens_left, retry_after = await self._redis.eval(
            _TOKEN_BUCKET_LUA,
            1,
            key,
            config.max_requests,
            config.window_seconds,
            now,
        )
        return RateLimitResult(
            allowed=bool(int(allowed_flag)),
            remaining=int(float(tokens_left)),
            retry_after_seconds=float(retry_after),
        )
