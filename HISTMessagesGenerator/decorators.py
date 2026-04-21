# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

import logging
from functools import wraps

def log_exceptions(error_message_map, log_level="warning", raise_exception=False, logger=None):
    """
    Decorator to log specific exceptions in a clean, consistent way.
    If logger is a string (e.g., 'self.logger'), it will be resolved at runtime.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(error_message_map.keys()) as e:
                # Détermination du logger dynamiquement
                if callable(logger):
                    log_instance = logger(*args, **kwargs)
                elif isinstance(logger, str) and hasattr(args[0], logger):
                    log_instance = getattr(args[0], logger)
                else:
                    log_instance = logger or logging.getLogger()

                log_func = getattr(log_instance, log_level, log_instance.warning)
                message = error_message_map.get(type(e), "Unexpected error")
                log_func(f"{message}: {e}")
                if raise_exception:
                    raise
                return None
        return wrapper
    return decorator
