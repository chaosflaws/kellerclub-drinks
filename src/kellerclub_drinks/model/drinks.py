from dataclasses import dataclass


@dataclass(frozen=True)
class Drink:
    name: str
    display_name: str
