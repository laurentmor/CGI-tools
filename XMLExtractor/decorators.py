# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

import logging
from functools import wraps


# Decorator to log exceptions based on a provided mapping of exception types to log messages.
# Parameters:
# - error_map: A dictionary mapping exception types to log messages.
# - log_level: The logging level to use (default is "warning").
# - raise_exception: Whether to re-raise the exception after logging (default is False).
# - logger: An optional logger instance or the name of a logger attribute on self
# #(if the decorated function is a method).
# Usage:
# @log_exceptions({ValueError: "A value error occurred", KeyError: "A key error occurred"},
# log_level="error", raise_exception=True, logger="my_logger")
# def my_function():
#    ...
#
#
#
def log_exceptions(error_map, log_level="warning", raise_exception=False, logger=None):
    """Decorator to log exceptions based on a provided mapping of exception types to log messages.
    Parameters:
    - error_map: A dictionary mapping exception types to log messages.
    - log_level: The logging level to use (default is "warning").
    - raise_exception: Whether to re-raise the exception after logging (default is False).
    - logger: An optional logger instance or the name of a logger attribute on self
    (if the decorated function is a method).
    Usage:
    @log_exceptions({ValueError: "A value error occurred", KeyError: "A key error occurred"},
    log_level="error", raise_exception=True, logger="my_logger")
    def my_function():
       ...
    """

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
