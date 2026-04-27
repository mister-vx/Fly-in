from dataclasses import dataclass
from typing import Optional


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: Optional[str] = None
    max_drones: int = 1

    def is_blocked(self) -> bool:
        return self.zone_type == "blocked"

    def is_restricted(self) -> bool:
        return self.zone_type == "restricted"

    def is_priority(self) -> bool:
        return self.zone_type == "priority"


@dataclass
class Connection:
    from_zone: str
    to_zone: str
    max_capacity: int = 1

    def is_overloaded(self, current_usage: int) -> bool:
        return current_usage >= self.max_capacity
