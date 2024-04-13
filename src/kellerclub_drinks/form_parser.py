from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qs


class FormParser:
    """Parser for a query string formatted as HTML form data."""

    def __init__(self, *valid_params: Param):
        self.valid_params = valid_params

    def parse(self, query: str, /, content_type: Optional[str] = None) -> dict[str, list[str]]:
        """Parses the given form data, validating it against expected parameters.

        Returns the parsed data as a dictionary of value lists.
        """

        if content_type not in [None, 'application/x-www-form-urlencoded']:
            raise ValueError('Wrong Content Type!')

        payload = parse_qs(query, strict_parsing=True)

        keys = {param.key for param in self.valid_params}
        if extra_fields := payload.keys() - keys:
            raise ValueError(f'Found extraneous keys {extra_fields}!')

        for param in self.valid_params:
            if param.key not in payload:
                payload[param.key] = param.default_value or []
            if (length := len(payload[param.key])) < param.min_values:
                raise ValueError(f'Param {param.key} does not have enough values '
                                 f'({length}<{param.min_values})!')
            if param.max_values and (length := len(payload[param.key])) > param.max_values:
                raise ValueError(f'Param {param.key} has too many values '
                                 f'({length}>{param.max_values})!')

        return payload


@dataclass(frozen=True)
class Param:
    """Describes a single valid parameter in HTML form data."""

    key: str
    min_values: int = 0
    max_values: Optional[int] = None
    default_value: Optional[list[str]] = None
