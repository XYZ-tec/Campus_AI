"""Run all nine search algorithms for a source/destination pair."""

import json

from core.constants import LOCATIONS
from modules.search import compare_all


def main():
    """Ask for two campus locations and print the comparison results."""
    print("Campus locations:")
    print(", ".join(LOCATIONS))
    source = input("Enter source: ").strip()
    destination = input("Enter destination: ").strip()
    print(json.dumps(compare_all(source, destination), indent=2))


if __name__ == "__main__":
    main()
