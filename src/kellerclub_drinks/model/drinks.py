import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Drink:
    """A drink or bundle for purchase."""

    name: str
    display_name: str

    def __post_init__(self) -> None:
        if not Drink.valid_name(self.name):
            raise ValueError('Invalid drink name!')

    @staticmethod
    def valid_name(name: str) -> bool:
        """True if name is a valid internal name, false otherwise."""

        return bool(re.match('^[a-zA-Z0-9_]+$', name))
