"""
Utility functions for priority value conversion between string and integer representations.
"""
from typing import Union


def priority_string_to_int(priority: str) -> int:
    """
    Convert priority string to integer representation.

    Args:
        priority: Priority level as string ('low', 'medium', 'high')

    Returns:
        Integer representation of priority (1=low, 2=medium, 3=high)

    Raises:
        ValueError: If priority string is not recognized
    """
    priority_map = {
        'low': 1,
        'medium': 2,
        'high': 3
    }

    priority_lower = priority.lower()
    if priority_lower not in priority_map:
        raise ValueError(f"Invalid priority string: {priority}. Must be one of: low, medium, high")

    return priority_map[priority_lower]


def priority_int_to_string(priority: int) -> str:
    """
    Convert priority integer to string representation.

    Args:
        priority: Priority level as integer (1=low, 2=medium, 3=high)

    Returns:
        String representation of priority ('low', 'medium', 'high')

    Raises:
        ValueError: If priority integer is not recognized
    """
    priority_map = {
        1: 'low',
        2: 'medium',
        3: 'high'
    }

    if priority not in priority_map:
        raise ValueError(f"Invalid priority integer: {priority}. Must be one of: 1, 2, 3")

    return priority_map[priority]


def normalize_priority_value(priority: Union[str, int]) -> Union[str, int]:
    """
    Normalize priority value to ensure consistency.

    Args:
        priority: Priority value as string or integer

    Returns:
        Normalized priority in its original type (string->string, int->int)
    """
    if isinstance(priority, str):
        # Convert to int then back to string to normalize
        return priority_int_to_string(priority_string_to_int(priority))
    elif isinstance(priority, int):
        # Convert to string then back to int to normalize
        return priority_string_to_int(priority_int_to_string(priority))
    else:
        raise ValueError(f"Priority must be string or integer, got {type(priority)}")


def validate_priority_value(priority: Union[str, int]) -> bool:
    """
    Validate that a priority value is acceptable.

    Args:
        priority: Priority value to validate

    Returns:
        True if priority value is valid, False otherwise
    """
    try:
        if isinstance(priority, str):
            priority_string_to_int(priority)
        elif isinstance(priority, int):
            priority_int_to_string(priority)
        else:
            return False
        return True
    except ValueError:
        return False


def convert_task_priority_for_frontend(priority: int) -> str:
    """
    Convert task priority from backend integer representation to frontend string representation.

    Args:
        priority: Priority as integer from backend (1, 2, 3)

    Returns:
        Priority as string for frontend display ('low', 'medium', 'high')
    """
    return priority_int_to_string(priority)


def convert_task_priority_for_backend(priority: str) -> int:
    """
    Convert task priority from frontend string representation to backend integer representation.

    Args:
        priority: Priority as string from frontend ('low', 'medium', 'high')

    Returns:
        Priority as integer for backend storage (1, 2, 3)
    """
    return priority_string_to_int(priority)


def get_priority_display_text(priority: Union[str, int]) -> str:
    """
    Get user-friendly display text for priority.

    Args:
        priority: Priority as string or integer

    Returns:
        User-friendly display text for the priority
    """
    if isinstance(priority, int):
        priority_str = priority_int_to_string(priority)
    else:
        priority_str = str(priority).lower()

    display_map = {
        'low': 'Low Priority',
        'medium': 'Medium Priority',
        'high': 'High Priority'
    }

    return display_map.get(priority_str, 'Unknown Priority')