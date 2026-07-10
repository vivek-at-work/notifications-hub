from __future__ import annotations

import re
from typing import Any

import jsonschema
from jsonschema import ValidationError

from notifications_common.errors import ErrorCode, PlatformError

_PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def validate_placeholders(schema: dict[str, Any], values: dict[str, Any]) -> None:
    """Validate placeholder values against a JSON Schema."""
    try:
        jsonschema.validate(instance=values, schema=schema)
    except ValidationError as exc:
        field = ".".join(str(part) for part in exc.absolute_path) or None
        raise PlatformError(
            ErrorCode.VALIDATION_ERROR,
            exc.message,
            field=field,
        ) from exc


class PlaceholderRenderer:
    """Template rendering engine with {{placeholder}} substitution."""

    def render(self, template: str, values: dict[str, str]) -> str:
        missing: set[str] = set()

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in values:
                missing.add(key)
                return match.group(0)
            return values[key]

        rendered = _PLACEHOLDER_PATTERN.sub(replace, template)
        if missing:
            raise PlatformError(
                ErrorCode.TEMPLATE_RENDER_ERROR,
                f"Missing placeholder values: {', '.join(sorted(missing))}",
            )
        return rendered
