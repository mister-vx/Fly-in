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
        with open(self.file_name, 'r') as f:
            for nb, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    self.parse_line(line)
                except Exception as er:
                    raise ValueError(f"Error on line {nb}: {er}")
        return self.graph

    def parse_line(self, line: str):
        if line.startswith("nb_drones:"):
            self.parse_drones(line)
        elif line.startswith("start_hub:"):
            self.parse_zone(line, start=True)
        elif line.startswith("end_hub:"):
            self.parse_zone(line, end=True)
        elif line.startswith("hub:"):
            self.parse_zone(line)
        elif line.startswith("connection:"):
            self.parse_connection(line)
        else:
            raise ValueError("Invalid line format")

    def parse_drones(self, line: str):
        try:
            nb = int(line.split(":")[1].strip())
        except Exception:
            raise ValueError("nb_drones must be a number")
        if nb <= 0:
            raise ValueError("nb_drones must be > 0")
        self.graph.nb_drones = nb

    def parse_zone(self, line: str, start: bool = False, end: bool = False):
        lst = line.split()
        name = lst[1]
        if "-" in name or " " in name:
            raise ValueError("Zone name cannot contain '-' or spaces")
        try:
            x = int(lst[2])
            y = int(lst[3])
        except Exception:
            raise ValueError("coordinates must be integers")
        metadata = self.parse_metadata(line)
        try:
            max_drones = int(metadata.get("max_drones", 1))
        except Exception:
            raise ValueError("max_drones must be integer")
        zone_type = metadata.get("zone", "normal")
        valid_types = {"normal", "blocked", "restricted", "priority"}
        if zone_type not in valid_types:
            raise ValueError(f"Invalid zone type '{zone_type}'")
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
        content = line.split(":")[1].strip()
        main_part = content.split()[0]
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
        metadata = re.search(r"\[(.*?)\]", line)
        if not metadata:
            return {}
        data = metadata.group(1)
        items = data.split()
        metadata = {}
        for item in items:
            if "=" not in item:
                raise ValueError("Invalid metadata format")
            key, value = item.split("=")
            metadata[key] = value
        return metadata
