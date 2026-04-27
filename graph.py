from typing import Dict, List, Optional

from models import Zone, Connection  # مهم بدل "Zone"


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.adjacency: Dict[str, List[Connection]] = {}

        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None

        self.nb_drones: int = 0

    # -------------------------
    # ZONES
    # -------------------------
    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone: {zone.name}")

        if zone.max_drones <= 0:
            raise ValueError(f"Invalid max_drones for zone {zone.name}")

        if zone.zone_type not in {"normal", "restricted", "priority", "blocked"}:
            raise ValueError(f"Invalid zone type: {zone.zone_type}")

        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    # -------------------------
    # CONNECTIONS
    # -------------------------
    def add_connection(self, connection: Connection) -> None:
        if connection.from_zone not in self.zones:
            raise ValueError(f"Unknown zone: {connection.from_zone}")

        if connection.to_zone not in self.zones:
            raise ValueError(f"Unknown zone: {connection.to_zone}")

        if connection.max_capacity <= 0:
            raise ValueError("Connection capacity must be positive")

        # منع duplicate (A-B و B-A)
        for conn in self.adjacency[connection.from_zone]:
            if conn.to_zone == connection.to_zone:
                raise ValueError(
                    f"Duplicate connection: {connection.from_zone}-{connection.to_zone}"
                )

        # إضافة connection
        self.adjacency[connection.from_zone].append(connection)

        # reverse connection (bidirectional)
        reverse = Connection(
            from_zone=connection.to_zone,
            to_zone=connection.from_zone,
            max_capacity=connection.max_capacity,
        )
        self.adjacency[connection.to_zone].append(reverse)

    # -------------------------
    # START / END
    # -------------------------
    def set_start(self, zone: Zone) -> None:
        if self.start is not None:
            raise ValueError("Multiple start zones")
        self.start = zone

    def set_end(self, zone: Zone) -> None:
        if self.end is not None:
            raise ValueError("Multiple end zones")
        self.end = zone

    # -------------------------
    # HELPERS
    # -------------------------
    def get_neighbors(self, zone_name: str) -> List[Connection]:
        if zone_name not in self.adjacency:
            raise ValueError(f"Zone not found: {zone_name}")
        return self.adjacency[zone_name]

    def is_valid_zone(self, name: str) -> bool:
        return name in self.zones

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise ValueError(f"Zone not found: {name}")
        return self.zones[name]
