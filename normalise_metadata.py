import argparse
from pathlib import Path

from lib.metadata_utils import (
    walk_and_normalise,
)


def main():
    parser = argparse.ArgumentParser(description="Normalise artist names in music metadata.")
    parser.add_argument("path", type=str, help="Path to root of music folder")
    parser.add_argument("--dry-run", action="store_true", help="Only print changes, don't write")
    args = parser.parse_args()

    walk_and_normalise(Path(args.path), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
