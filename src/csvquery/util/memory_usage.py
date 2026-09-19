import logging
from logging import getLogger
from typing import Callable, Any
import functools
import tracemalloc

logger = getLogger(__name__)


def memory_usage(task: str, level: int = logging.INFO) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracemalloc.start()
            try:
                return func(*args, **kwargs)
            finally:
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                logger.log(level, "%s peak memory usage %.1f MB", task, peak / 1024**2)

        return wrapper
    return decorator
