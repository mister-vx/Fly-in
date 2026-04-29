from typing import Dict, List, Optional
from models import Connection, Zone

class Graph:
    """Represents the drone network as an adjacency list graph."""
    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.adjacency: Dict[str, List[Connection]] = {}
        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None
        self.nb_drones: Optional[int] = None

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph."""
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """Add a bidirectional connection between two zones."""
        self.connections.append(connection)
        self.adjacency[connection.from_zone].append(connection)
        reverse = Connection(
            from_zone=connection.to_zone,
            to_zone=connection.from_zone,
            max_capacity=connection.max_capacity
        )
        self.adjacency[connection.to_zone].append(reverse)

    def get_zone(self, name: str) -> Zone:
        """Return a Zone by name."""
        if name not in self.zones:
            raise ValueError(f"Zone not found: {name}")
        return self.zones[name]

    def is_valid_zone(self, name: str) -> bool:
        """Return True if zone exists in the graph."""
        return name in self.zones

    def get_neighbors(self, zone_name: str) -> List[Connection]:
        """Return all connections from a given zone."""
        return self.adjacency[zone_name]