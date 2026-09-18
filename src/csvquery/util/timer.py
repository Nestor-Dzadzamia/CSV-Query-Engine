import functools
import logging
from collections.abc import Callable
from time import perf_counter
from typing import Any

logger = logging.getLogger(__name__)


def timed(task: str, level: int = logging.INFO) -> Callable:
    def decorator(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                logger.log(level, "%s took %.3f seconds", task, perf_counter() - start)

        return wrapper

    return decorator
