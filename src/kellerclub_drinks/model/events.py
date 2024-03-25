from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Event:
    """
    Unit by which orders are grouped. Usually corresponds to one opening of the
    venue.
    """

    name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
