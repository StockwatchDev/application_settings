"""Utilities for file operations"""

from typing import Any


def deep_update(
    mapping: dict[str, Any], *updating_mappings: dict[str, Any]
) -> dict[str, Any]:
    """Update a nested dictionary or similar mapping."""
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping
