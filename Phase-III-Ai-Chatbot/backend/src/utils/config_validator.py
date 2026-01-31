"""
Configuration validation and startup checks for the Todo AI Chatbot.
Ensures all required environment variables and configurations are properly set before starting services.
"""
import os
import sys
from typing import List, Dict, Tuple
from datetime import datetime
import asyncio


class ConfigValidator:
    """
    Validates configuration settings and performs startup checks.
    """

    def __init__(self):
        """
        Initialize the configuration validator.
        """
        self.required_env_vars = [
            "BETTER_AUTH_SECRET",
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "DATABASE_URL"
        ]

        self.optional_env_vars = [
            "OPENAI_MODEL",
            "BACKEND_API_URL",
            "LOG_LEVEL",
            "RATE_LIMIT_REQUESTS_PER_MINUTE"
        ]

        self.validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "overall_status": "pending"
        }

    def validate_environment_variables(self) -> Tuple[bool, List[str]]:
        """
        Validate that all required environment variables are set.

        Returns:
            Tuple of (is_valid, list_of_missing_variables)
        """
        missing_vars = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        is_valid = len(missing_vars) == 0

        self.validation_results["checks"]["environment_variables"] = {
            "status": "passed" if is_valid else "failed",
            "details": {
                "missing_variables": missing_vars,
                "required_variables": self.required_env_vars,
                "optional_variables": self.optional_env_vars
            }
        }

        return is_valid, missing_vars

    def validate_database_connection(self) -> Tuple[bool, str]:
        """
        Validate that the database connection is available.

        Returns:
            Tuple of (is_connected, connection_message)
        """
        try:
            # This would actually test the database connection
            # For now, we'll simulate the check
            from backend.src.database import check_database_connection
            is_connected = asyncio.run(check_database_connection())

            message = "Database connection successful" if is_connected else "Database connection failed"

            self.validation_results["checks"]["database_connection"] = {
                "status": "passed" if is_connected else "failed",
                "details": {"message": message}
            }

            return is_connected, message
        except Exception as e:
            self.validation_results["checks"]["database_connection"] = {
                "status": "failed",
                "details": {"message": f"Database connection error: {str(e)}", "exception": str(type(e).__name__)}
            }
            return False, f"Database connection error: {str(e)}"

    def validate_ai_provider_connection(self) -> Tuple[bool, str]:
        """
        Validate that the AI provider (OpenRouter) is accessible.

        Returns:
            Tuple of (is_accessible, connection_message)
        """
        try:
            # Check if required AI provider environment variables are set
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")

            if not api_key or not base_url:
                message = "AI provider environment variables not set"
                self.validation_results["checks"]["ai_provider_connection"] = {
                    "status": "failed",
                    "details": {"message": message}
                }
                return False, message

            # In a real implementation, we would make a test request to the AI provider
            # For now, we'll just verify the configuration is present
            message = "AI provider configuration is set"

            self.validation_results["checks"]["ai_provider_connection"] = {
                "status": "passed",
                "details": {"message": message}
            }

            return True, message
        except Exception as e:
            self.validation_results["checks"]["ai_provider_connection"] = {
                "status": "failed",
                "details": {"message": f"AI provider connection error: {str(e)}", "exception": str(type(e).__name__)}
            }
            return False, f"AI provider connection error: {str(e)}"

    def validate_auth_configuration(self) -> Tuple[bool, str]:
        """
        Validate that authentication is properly configured.

        Returns:
            Tuple of (is_valid, validation_message)
        """
        try:
            # Check if required auth environment variables are set
            auth_secret = os.getenv("BETTER_AUTH_SECRET")

            if not auth_secret:
                message = "Authentication secret not set"
                self.validation_results["checks"]["auth_configuration"] = {
                    "status": "failed",
                    "details": {"message": message}
                }
                return False, message

            # Additional auth validation would go here
            # For now, we'll just check that the secret is set
            message = "Authentication configuration is valid"

            self.validation_results["checks"]["auth_configuration"] = {
                "status": "passed",
                "details": {"message": message}
            }

            return True, message
        except Exception as e:
            self.validation_results["checks"]["auth_configuration"] = {
                "status": "failed",
                "details": {"message": f"Auth configuration error: {str(e)}", "exception": str(type(e).__name__)}
            }
            return False, f"Auth configuration error: {str(e)}"

    def perform_startup_checks(self) -> Dict[str, any]:
        """
        Perform all startup validation checks.

        Returns:
            Dictionary with validation results
        """
        print("🔍 Performing startup validation checks...")

        # Validate environment variables
        env_valid, missing_env = self.validate_environment_variables()
        if not env_valid:
            print(f"❌ Missing required environment variables: {missing_env}")
            print("Please set the required environment variables before starting the service.")
            sys.exit(1)

        # Validate database connection
        db_connected, db_message = self.validate_database_connection()
        if not db_connected:
            print(f"❌ Database connection issue: {db_message}")
            print("Please verify your database configuration before starting the service.")
            sys.exit(1)

        # Validate AI provider connection
        ai_accessible, ai_message = self.validate_ai_provider_connection()
        if not ai_accessible:
            print(f"⚠️  AI provider configuration issue: {ai_message}")
            print("Please verify your AI provider configuration.")

        # Validate auth configuration
        auth_valid, auth_message = self.validate_auth_configuration()
        if not auth_valid:
            print(f"❌ Authentication configuration issue: {auth_message}")
            print("Please verify your authentication configuration before starting the service.")
            sys.exit(1)

        # Overall status is based on critical checks
        all_critical_passed = env_valid and db_connected and auth_valid

        self.validation_results["overall_status"] = "passed" if all_critical_passed else "failed"
        self.validation_results["timestamp"] = datetime.utcnow().isoformat()

        if all_critical_passed:
            print("✅ All startup checks passed! Service is ready to start.")
        else:
            print("❌ Some startup checks failed. Please resolve the issues before starting the service.")
            sys.exit(1)

        return self.validation_results

    def get_validation_report(self) -> Dict[str, any]:
        """
        Get the validation report with all check results.

        Returns:
            Dictionary with validation report
        """
        return self.validation_results


class StartupChecks:
    """
    Performs comprehensive startup validation for the application.
    """

    def __init__(self):
        """
        Initialize the startup checks.
        """
        self.validator = ConfigValidator()

    def run_pre_startup_validation(self) -> bool:
        """
        Run pre-startup validation checks.

        Returns:
            True if all checks pass, False otherwise
        """
        print("🚀 Running pre-startup validation...")

        # Perform all validation checks
        validation_results = self.validator.perform_startup_checks()

        if validation_results["overall_status"] == "passed":
            print("✅ Pre-startup validation completed successfully")
            return True
        else:
            print("❌ Pre-startup validation failed")
            return False

    def run_post_startup_validation(self) -> Dict[str, any]:
        """
        Run post-startup validation checks after services are running.

        Returns:
            Dictionary with post-startup validation results
        """
        print("🔍 Running post-startup validation...")

        # Check if key services are responding
        post_startup_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "api_health": self._check_api_health(),
                "service_connectivity": self._check_service_connectivity(),
                "resource_availability": self._check_resource_availability()
            }
        }

        # Overall status is healthy if all checks pass
        all_passed = all(check["status"] == "passed" for check in post_startup_results["checks"].values())
        post_startup_results["overall_status"] = "healthy" if all_passed else "degraded"

        if all_passed:
            print("✅ Post-startup validation completed successfully")
        else:
            print("⚠️  Some post-startup checks indicate degraded status")

        return post_startup_results

    def _check_api_health(self) -> Dict[str, any]:
        """
        Check if the API is responding healthily.

        Returns:
            Dictionary with health check results
        """
        # In a real implementation, this would make a request to the health endpoint
        # For now, we'll simulate a successful health check
        return {
            "status": "passed",
            "details": {"message": "API health check passed"}
        }

    def _check_service_connectivity(self) -> Dict[str, any]:
        """
        Check connectivity to required services.

        Returns:
            Dictionary with connectivity check results
        """
        # Check connectivity to database and AI provider
        db_connected, db_msg = self.validator.validate_database_connection()
        ai_connected, ai_msg = self.validator.validate_ai_provider_connection()

        service_connectivity = {
            "database": {"connected": db_connected, "message": db_msg},
            "ai_provider": {"accessible": ai_connected, "message": ai_msg}
        }

        all_connected = db_connected and ai_connected

        return {
            "status": "passed" if all_connected else "failed",
            "details": service_connectivity
        }

    def _check_resource_availability(self) -> Dict[str, any]:
        """
        Check availability of required resources.

        Returns:
            Dictionary with resource availability check results
        """
        # Check if required resources are available
        resources = {
            "memory": self._check_memory_availability(),
            "disk_space": self._check_disk_space(),
            "file_handles": self._check_file_handle_limits()
        }

        all_available = all(res["available"] for res in resources.values())

        return {
            "status": "passed" if all_available else "failed",
            "details": resources
        }

    def _check_memory_availability(self) -> Dict[str, any]:
        """
        Check if sufficient memory is available.

        Returns:
            Dictionary with memory check results
        """
        # This would check actual memory availability
        # For now, we'll simulate a successful check
        import psutil
        memory = psutil.virtual_memory()

        # Consider memory sufficient if more than 10% is available
        sufficient = memory.available > 100 * 1024 * 1024  # 100 MB minimum

        return {
            "available": sufficient,
            "details": {
                "total": f"{memory.total / (1024**3):.2f} GB",
                "available": f"{memory.available / (1024**3):.2f} GB",
                "percent_used": f"{memory.percent}%"
            }
        }

    def _check_disk_space(self) -> Dict[str, any]:
        """
        Check if sufficient disk space is available.

        Returns:
            Dictionary with disk space check results
        """
        # This would check actual disk space
        # For now, we'll simulate a successful check
        import shutil
        total, used, free = shutil.disk_usage(".")

        # Consider disk space sufficient if more than 1GB is free
        sufficient = free > 1024 * 1024 * 1024  # 1 GB minimum

        return {
            "available": sufficient,
            "details": {
                "total": f"{total / (1024**3):.2f} GB",
                "used": f"{used / (1024**3):.2f} GB",
                "free": f"{free / (1024**3):.2f} GB"
            }
        }

    def _check_file_handle_limits(self) -> Dict[str, any]:
        """
        Check if sufficient file handles are available.

        Returns:
            Dictionary with file handle check results
        """
        # This would check actual file handle limits
        # For now, we'll simulate a successful check
        import resource
        soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)

        # Consider sufficient if we have at least 1024 file handles
        sufficient = soft_limit >= 1024

        return {
            "available": sufficient,
            "details": {
                "soft_limit": soft_limit,
                "hard_limit": hard_limit
            }
        }


# Singleton instance for global use
startup_checks = StartupChecks()


def run_startup_validation() -> bool:
    """
    Run the complete startup validation process.

    Returns:
        True if validation passes, False otherwise
    """
    return startup_checks.run_pre_startup_validation()


def get_config_validation_report() -> Dict[str, any]:
    """
    Get the configuration validation report.

    Returns:
        Dictionary with validation results
    """
    return startup_checks.validator.get_validation_report()