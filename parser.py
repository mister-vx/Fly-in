from graph import Graph
from models import Connection, Zone
import re


class Parser:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.graph = Graph()
        self.first_line = True
        self.connections_started = False
        self.seen_connections = set[frozenset[set]] = set()

    def parse(self):
        """Parse the file and return a populated Graph."""
        with open(self.file_name, 'r') as f:
            for nb, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    self.parse_line(line)
                except Exception as er:
                    raise ValueError(f"Error on line {nb}: {er}")
        self.validate_completeness()
        return self.graph

    def validate_completeness(self) -> None:
        """Ensure all required declarations were present."""
        if self.graph.nb_drones is None:
            raise ValueError("Missing 'nb_drones' declaration")
        if self.graph.start is None:
            raise ValueError("Missing 'start_hub' declaration")
        if self.graph.end is None:
            raise ValueError("Missing 'end_hub' declaration")
        if not self.graph.connection:
            raise ValueError("Map has no connections — drones can never reach the end")


    def parse_line(self, line: str):
        if self.first_line:
            self.first_line = False
            if not line.startswith("nb_drones")
                raise ValueError("'nb_drones' must be the first line")
            self.parse_drones(line)
            return
        if line.startswith("nb_drones:"):
            raise ValueError("'nb_drones' can only appear once")
        elif line.startswith("start_hub:"):
            self.ensure_no_connections_yet(line)
            self.parse_zone(line, start=True)
        elif line.startswith("end_hub:"):
            self.ensure_no_connections_yet(line)
            self.parse_zone(line, end=True)
        elif line.startswith("hub:"):
            self.ensure_no_connections_yet(line)
            self.parse_zone(line)
        elif line.startswith("connection:"):
            self.connections_started = True
            self.parse_connection(line)
        else:
            raise ValueError(f"Unrecognized line format: '{line}'")

    def ensure_no_connections_yet(self, line: str) -> None:
        if self.connections_started:
            raise ValueError(
                f"Zone definitions must come before connections: '{line}'"
            )

    def parse_drones(self, line: str):
        """Parse the nb_drones declaration."""
        _, _, d = line.partition(":")
        try:
            nb = int(d.strip())
        except Exception:
            raise ValueError("nb_drones must be an integer")
        if nb <= 0:
            raise ValueError("nb_drones must be > 0")
        self.graph.nb_drones = nb

    def parse_zone(self, line: str, start: bool = False, end: bool = False):
        """Parse a hub / start_hub / end_hub line."""
        if start and self.graph.start is not None:
            raise ValueError("Duplicate 'start_hub'")
        if end and self.graph.end is not None:
            raise ValueError("Duplicate 'end_hub'")
        lst = line.split()
        if len(lst) < 4:
            raise ValueError("Zone line must have: <prefix> <name> <x> <y>")
        name = lst[1]
        if "-" in name:
            raise ValueError("Zone name cannot contain '-'")
        try:
            x = int(lst[2])
            y = int(lst[3])
        except Exception:
            raise ValueError("Zone coordinates must be integers")
        if name in self.graph.zones:
            raise ValueError(f"Duplicate zone name '{name}'")
        metadata = self.parse_metadata(line)
        zone_type = metadata.get("zone", "normal")
        valid_types = {"normal", "blocked", "restricted", "priority"}
        if zone_type not in valid_types:
            raise ValueError(f"Invalid zone type '{zone_type}'")
        try:
            max_drones = int(metadata.get("max_drones", 1))
            if max_drones <= 0:
                raise ValueError()
        except Exception:
            raise ValueError("max_drones must be a positive integer")
        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=metadata.get("color"),
            max_drones=max_drones
        )
        self.graph.add_zone(zone)
        if start:
            self.graph.start = zone
        if end:
            self.graph.end = zone

    def parse_connection(self, line: str):
        """Parse a connection line."""
        _, _, c = line.partition(":")
        content = c.strip()
        main_part = content.split()[0].strip()
        from_zone, to_zone = main_part.split("-")
        if from_zone not in self.graph.zones or to_zone not in self.graph.zones:
            raise ValueError("Connection references unknown zone")
        metadata = self.parse_metadata(line)
        try:
            max_link_capacity = int(metadata.get("max_link_capacity", 1))
        except Exception:
            raise ValueError("max_link_capacity must be integer")
        connection = Connection(
            from_zone=from_zone,
            to_zone=to_zone,
            max_capacity=max_link_capacity
        )
        self.graph.add_connection(connection)

    def parse_metadata(self, line: str):
                """Extract key=value pairs from the [...] block, if present."""
        metadata = re.search(r"\[(.*?)\]", line)
        if not metadata:
            return {}
        data = metadata.group(1)
        items = data.split()
        metadata = {}
        for item in items:
            if "=" not in item:
                raise ValueError(f"Invalid metadata token '{item}'")
            key, _, value = item.partition("=")
            metadata[key.strip()] = value.strip()
        return metadata
