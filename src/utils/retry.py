# Plan:
# 1. Decorator accepts: max_attempts, base_delay, max_delay, exceptions to catch
# 2. On each failure: wait base_delay * 2^attempt, capped at max_delay
# 3. Add optional jitter to avoid thundering herd
# 4. Re-raise the last exception if all attempts exhausted
# 5. Support both sync functions (via functools.wraps)

import time
import random
import functools
from typing import Type


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple[Type[BaseException], ...] = (Exception,),
    jitter: bool = True,
):
    """Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Total number of attempts (including the first call).
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Upper bound on the delay between retries.
        exceptions: Exception types that trigger a retry.
        jitter: If True, adds random noise to each delay to spread load.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc

                    if attempt == max_attempts - 1:
                        break

                    delay = min(base_delay * (2 ** attempt), max_delay)
                    if jitter:
                        delay *= 0.5 + random.random()  # [0.5x, 1.5x]

                    time.sleep(delay)

            raise last_exc

        return wrapper
    return decorator
