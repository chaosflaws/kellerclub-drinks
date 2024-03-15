from dataclasses import dataclass


@dataclass(frozen=True)
class Drink:
    display_name: str
