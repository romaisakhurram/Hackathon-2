"""
Monitoring and error reporting utilities for the Todo AI Chatbot.
Provides hooks for metrics collection, error reporting, and system health monitoring.
"""
import time
import functools
import json
from typing import Callable, Any
from datetime import datetime
import traceback
import sys
from enum import Enum


class MetricType(Enum):
    """
    Types of metrics that can be tracked.
    """
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricsCollector:
    """
    Collects and manages application metrics.
    """

    def __init__(self):
        """
        Initialize the metrics collector.
        """
        self.metrics = {}

    def increment_counter(self, name: str, labels: dict = None, amount: int = 1):
        """
        Increment a counter metric.

        Args:
            name: Name of the metric
            labels: Optional labels to associate with the metric
            amount: Amount to increment by (default 1)
        """
        key = self._get_metric_key(name, labels)
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += amount

    def set_gauge(self, name: str, value: float, labels: dict = None):
        """
        Set a gauge metric to a specific value.

        Args:
            name: Name of the metric
            value: Value to set the gauge to
            labels: Optional labels to associate with the metric
        """
        key = self._get_metric_key(name, labels)
        self.metrics[key] = value

    def observe_histogram(self, name: str, value: float, labels: dict = None):
        """
        Observe a value for a histogram metric.

        Args:
            name: Name of the metric
            value: Value to observe
            labels: Optional labels to associate with the metric
        """
        key = self._get_metric_key(name, labels)
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)

    def _get_metric_key(self, name: str, labels: dict = None) -> str:
        """
        Create a unique key for a metric with its labels.

        Args:
            name: Name of the metric
            labels: Optional labels to associate with the metric

        Returns:
            Unique string key for the metric
        """
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name

    def get_metrics(self) -> dict:
        """
        Get all collected metrics.

        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()


class ErrorReporter:
    """
    Reports errors and exceptions to monitoring systems.
    """

    def __init__(self):
        """
        Initialize the error reporter.
        """
        self.error_count = 0
        self.errors = []

    def report_error(self, error: Exception, context: dict = None, severity: str = "error"):
        """
        Report an error with context information.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            severity: Severity level (debug, info, warning, error, critical)
        """
        self.error_count += 1

        error_info = {
            "id": self.error_count,
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "severity": severity
        }

        self.errors.append(error_info)

        # In a real implementation, this would send to an external service
        # like Sentry, Datadog, or similar
        print(f"ERROR [{severity.upper()}]: {error_info['error_message']}")
        if context:
            print(f"CONTEXT: {context}")

    def get_error_report(self) -> dict:
        """
        Get a summary report of all errors.

        Returns:
            Dictionary with error summary information
        """
        return {
            "total_errors": self.error_count,
            "recent_errors": self.errors[-10:],  # Last 10 errors
            "error_types": list(set(err["error_type"] for err in self.errors))
        }


class HealthChecker:
    """
    Performs health checks on various system components.
    """

    def __init__(self):
        """
        Initialize the health checker.
        """
        self.health_status = {}

    async def check_database_health(self) -> bool:
        """
        Check if the database is accessible and healthy.

        Returns:
            True if database is healthy, False otherwise
        """
        try:
            # This would check the actual database connection
            # For now, we'll simulate the check
            from backend.src.database import check_database_connection
            return await check_database_connection()
        except Exception:
            return False

    async def check_ai_provider_health(self) -> bool:
        """
        Check if the AI provider (OpenRouter) is accessible.

        Returns:
            True if AI provider is healthy, False otherwise
        """
        try:
            # This would make a test request to the AI provider
            # For now, we'll simulate the check
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

            # Check if environment variables are set
            return bool(api_key and base_url)
        except Exception:
            return False

    async def check_system_health(self) -> dict:
        """
        Perform comprehensive system health check.

        Returns:
            Dictionary with health status for all components
        """
        health_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {
                "database": await self.check_database_health(),
                "ai_provider": await self.check_ai_provider_health(),
                "api_server": True,  # Assume API server is running if this code executes
                "authentication": True  # Assume auth is available
            }
        }

        # Overall status is healthy only if all components are healthy
        if not all(health_results["components"].values()):
            health_results["overall_status"] = "degraded"

        return health_results


# Global instances
metrics_collector = MetricsCollector()
error_reporter = ErrorReporter()
health_checker = HealthChecker()


def monitor_execution_time(metric_name: str, labels: dict = None):
    """
    Decorator to monitor execution time of functions.

    Args:
        metric_name: Name of the metric to track
        labels: Optional labels to associate with the metric
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Record execution time as a histogram
                metrics_collector.observe_histogram(
                    f"{metric_name}_duration_seconds",
                    execution_time,
                    labels
                )

                # Also increment a counter for successful executions
                metrics_collector.increment_counter(
                    f"{metric_name}_success_total",
                    labels
                )

                return result
            except Exception as e:
                execution_time = time.time() - start_time

                # Record execution time for failed executions too
                metrics_collector.observe_histogram(
                    f"{metric_name}_duration_seconds",
                    execution_time,
                    labels
                )

                # Increment error counter
                error_labels = {**(labels or {}), "status": "error"}
                metrics_collector.increment_counter(
                    f"{metric_name}_error_total",
                    error_labels
                )

                # Report the error
                error_reporter.report_error(
                    e,
                    context={
                        "function": func.__name__,
                        "execution_time": execution_time,
                        "args": str(args)[:100],  # Limit context size
                        "kwargs": str(kwargs)[:100]  # Limit context size
                    }
                )

                raise
        return wrapper
    return decorator


def report_api_call(user_id: str, endpoint: str, method: str, response_time: float, status_code: int):
    """
    Report an API call with metrics.

    Args:
        user_id: ID of the user making the call
        endpoint: API endpoint that was called
        method: HTTP method used
        response_time: Time taken to process the request in seconds
        status_code: HTTP status code returned
    """
    labels = {
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "status_code": str(status_code)
    }

    # Record response time
    metrics_collector.observe_histogram("api_response_time_seconds", response_time, labels)

    # Increment counter based on status
    if 200 <= status_code < 300:
        metrics_collector.increment_counter("api_requests_success_total", labels)
    else:
        metrics_collector.increment_counter("api_requests_error_total", labels)


def report_mcp_tool_usage(tool_name: str, user_id: str, success: bool, execution_time: float):
    """
    Report MCP tool usage with metrics.

    Args:
        tool_name: Name of the MCP tool that was used
        user_id: ID of the user who triggered the tool
        success: Whether the tool execution was successful
        execution_time: Time taken to execute the tool in seconds
    """
    labels = {
        "tool_name": tool_name,
        "user_id": user_id,
        "success": str(success)
    }

    # Record execution time
    metrics_collector.observe_histogram("mcp_tool_execution_time_seconds", execution_time, labels)

    # Increment counter
    if success:
        metrics_collector.increment_counter("mcp_tool_success_total", labels)
    else:
        metrics_collector.increment_counter("mcp_tool_error_total", labels)


def report_message_processing(user_id: str, message_type: str, processing_time: float, success: bool):
    """
    Report message processing with metrics.

    Args:
        user_id: ID of the user whose message was processed
        message_type: Type of message (user_input, ai_response)
        processing_time: Time taken to process the message in seconds
        success: Whether the processing was successful
    """
    labels = {
        "user_id": user_id,
        "message_type": message_type,
        "success": str(success)
    }

    # Record processing time
    metrics_collector.observe_histogram("message_processing_time_seconds", processing_time, labels)

    # Increment counter
    if success:
        metrics_collector.increment_counter("messages_processed_success_total", labels)
    else:
        metrics_collector.increment_counter("messages_processed_error_total", labels)


async def get_monitoring_summary() -> dict:
    """
    Get a summary of all monitoring data.

    Returns:
        Dictionary with metrics, errors, and health information
    """
    return {
        "metrics": metrics_collector.get_metrics(),
        "errors": error_reporter.get_error_report(),
        "health": await health_checker.check_system_health(),
        "timestamp": datetime.utcnow().isoformat()
    }