import sys
from parser import Parser


def main():
    """Run the parser on a single file."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        graph = Parser(filepath).parse()
        print(f"✅ Parsed successfully")
        print(f"   nb_drones  : {graph.nb_drones}")
        print(f"   start      : {graph.start.name}")
        print(f"   end        : {graph.end.name}")
        print(f"   zones      : {list(graph.zones.keys())}")
        print(f"   connections: {[(c.from_zone, c.to_zone) for c in graph.connections]}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()