import functools, logging
from datetime import datetime
from typing import Callable


logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def timer_schema_validation(level=logging.INFO) -> Callable:
    def decorator(cls):
        if not hasattr(cls, "__init__"):
            return None

        init_function = cls.__init__
        @functools.wraps(init_function)
        def wrapper(self, *args, **kwargs):
            start = datetime.now()
            try:
                init_function(self, *args, **kwargs)
            finally:
                end = datetime.now()
                logger.log(level, f"schema validation took {(end - start).total_seconds()} seconds")

        setattr(cls, "__init__", wrapper)
        return cls
    return decorator


def timer_query_execution(level=logging.INFO) -> Callable:
    def decorator(cls):
        if not hasattr(cls, "save"):
            return None

        query_execution_function = cls.save
        @functools.wraps(query_execution_function)
        def wrapper(self, *args, **kwargs):
            start = datetime.now()
            try:
                query_execution_function(self, *args, **kwargs)
            finally:
                end = datetime.now()
                logger.log(level, f"query execution took {(end - start).total_seconds()} seconds")

        setattr(cls, "save", wrapper)
        return cls
    return decorator