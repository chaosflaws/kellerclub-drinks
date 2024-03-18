from dataclasses import dataclass


@dataclass(frozen=True)
class Drink:
    """A drink or bundle for purchase."""

    name: str
    display_name: str
