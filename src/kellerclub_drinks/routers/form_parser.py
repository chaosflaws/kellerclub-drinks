from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Optional, TypeVar, Generic, Callable, Any
from urllib.parse import parse_qs


class FormParser:
    """Parser for a query string formatted as HTML form data."""

    def __init__(self, *valid_params: Param[Any]):
        self.valid_params = valid_params

    def parse(self, query: str, /, content_type: Optional[str] = None) -> dict[str, Any]:
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
                payload[param.key] = param.default or []

            values = payload[param.key]
            if (length := len(values)) < param.min_values:
                raise ValueError(f'Param {param.key} does not have enough values '
                                 f'({length}<{param.min_values})!')
            if param.max_values and (length := len(values)) > param.max_values:
                raise ValueError(f'Param {param.key} has too many values '
                                 f'({length}>{param.max_values})!')
            if param.allowed:
                for value in values:
                    if not param.allowed(value):
                        raise ValueError(f'Value {value} for key {param.key} not '
                                         f'in allowed values ({param.allowed})!')
            if param.cnv:
                payload[param.key] = [param.cnv(value) for value in values]

        return payload


T = TypeVar('T')


@dataclass(frozen=True)
class Param(Generic[T]):
    """Describes a single valid parameter in HTML form data."""

    key: str
    min_values: int = 0
    max_values: Optional[int] = None
    _: dataclasses.KW_ONLY = None
    default: Optional[list[str]] = None
    allowed: Optional[Callable[[str], bool]] = None
    cnv: Optional[Callable[[str], T]] = None


def values_from(*args: str) -> Callable[[str], bool]:
    return lambda v: v in args


@dataclass(frozen=True)
class SingleValueParam(Param[T], Generic[T]):
    """Describes a parameter that can take exactly one value."""

    min_values: int = field(default=1, init=False, repr=False)
    max_values: Optional[int] = field(default=1, init=False, repr=False)


def _get_bool_value(val: str) -> bool:
    normalized = val.strip().lower()
    if normalized == 'true':
        return True
    if normalized == 'false':
        return False
    raise ValueError(f'Boolean value {val} is neither "true" nor "false"!')


@dataclass(frozen=True)
class BooleanParam(SingleValueParam[bool]):
    """Describes a boolean parameter."""

    allowed: Callable[[str], bool] = field(default=lambda v: v in {'true', 'false'})

    cnv: Callable[[str], bool] = field(default=_get_bool_value)


@dataclass(frozen=True)
class IntParam(SingleValueParam[int]):
    """Describes a parameter with integer values."""

    allowed: Callable[[str], bool] = field(default=lambda v: v.isdigit())

    cnv: Callable[[str], int] = field(default=int)


@dataclass(frozen=True)
class CheckboxParam(Param[bool]):
    """Describes an encoded HTML form checkbox value."""

    min_values: int = field(default=0,
                            init=False,
                            repr=False)

    max_values: int = field(default=1,
                            init=False,
                            repr=False)

    default: list[str] = field(default_factory=lambda: ['off'],
                               init=False,
                               repr=False)

    allowed: Callable[[str], bool] = field(default=lambda v: v in {'on', 'off'})

    cnv: Callable[[str], T] = field(default=lambda val: val == 'on')
