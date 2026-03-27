"""Utility functions for socratic-learning package."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional


def parse_iso_datetime(value: Any) -> Optional[datetime]:
    """
    Parse ISO format datetime string to datetime object.

    Args:
        value: Value to parse (datetime, ISO string, or None)

    Returns:
        datetime object or None
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return None


def parse_decimal(value: Any, default: str = "0.0") -> Decimal:
    """
    Parse value to Decimal.

    Args:
        value: Value to parse (Decimal, float, str, int, or None)
        default: Default value if input is None

    Returns:
        Decimal value
    """
    if value is None:
        return Decimal(default)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def ensure_iso_datetime(data: Dict[str, Any], *date_fields: str) -> Dict[str, Any]:
    """
    Convert ISO datetime strings in dict to datetime objects.

    Args:
        data: Dictionary potentially containing datetime strings
        *date_fields: Field names to parse as datetimes

    Returns:
        Updated dictionary with parsed datetimes
    """
    result = dict(data)
    for field in date_fields:
        if field in result:
            result[field] = parse_iso_datetime(result[field])
    return result


def ensure_decimals(data: Dict[str, Any], decimal_fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert float/string values in dict to Decimal objects.

    Args:
        data: Dictionary potentially containing float values
        decimal_fields: Dict mapping field names to default values
                       Example: {"score": "0.5", "confidence": "0.0"}

    Returns:
        Updated dictionary with Decimal values
    """
    result = dict(data)
    for field, default in decimal_fields.items():
        if field in result:
            result[field] = parse_decimal(result[field], default)
    return result
