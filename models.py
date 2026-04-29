from dataclasses import dataclass
from typing import Optional


@dataclass
class Zone:
    """Represents a zone (node) in the drone network."""
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

    def is_full(self, current_usage: int) -> bool:
        """Return True if zone cannot accept more drones."""
        return current_usage >= self.max_drones

@dataclass
class Connection:
    """Represents a bidirectional edge between two zones."""
    from_zone: str
    to_zone: str
    max_capacity: int = 1

    def is_full(self, current_usage: int) -> bool:
        """Return True if connection cannot accept more drones."""
        return current_usage >= self.max_capacity
