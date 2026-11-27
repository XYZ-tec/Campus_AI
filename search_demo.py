"""Run all nine search algorithms for a source/destination pair."""

from core.constants import LOCATIONS
from modules.search import compare_all
from modules.display import display_search_comparison


def main():
    """Ask for two campus locations and print the comparison results."""
    print("Campus locations:")
    print(", ".join(LOCATIONS))
    source = input("Enter source: ").strip()
    destination = input("Enter destination: ").strip()
    display_search_comparison(compare_all(source, destination))


if __name__ == "__main__":
    main()
