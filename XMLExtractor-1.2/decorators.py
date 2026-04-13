import logging
from functools import wraps

def log_exceptions(error_map, log_level="warning", raise_exception=False, logger=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # If logger is a string, resolve it as an attribute on self
            if isinstance(logger, str):
                _logger = getattr(args[0], logger)
            else:
                _logger = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except tuple(error_map.keys()) as e:
                getattr(_logger, log_level)(f"{error_map[type(e)]}: {e}")
                if raise_exception:
                    raise
        wrapper.__wrapped__ = func  # expose the original function for testing  
        return wrapper
    return decorator