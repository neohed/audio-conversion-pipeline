import json
from pathlib import Path
from lib.audio_utils import (
    is_compatible_audio,
    is_convertible_audio,
    convert_to_flac,
    copy_file,
    copy_largest_jpg,
    apply_album_art_if_missing,
)
from lib.metadata_utils import walk_and_normalise

with open("config.json") as f:
    config = json.load(f)

# Base directories
SOURCE_DIR = Path(config["source_dir"])  # Music source directory
DEST_DIR = Path(config["dest_dir"])  # Where the converted/copied files go

# List of artist folder names to process
ARTISTS = config["artists"]


def process_album_folder(source_folder: Path, dest_folder: Path):
    """Copy/convert audio files and embed album art from source to dest."""
    print(f"Processing album folder: {source_folder} -> {dest_folder}")
    dest_folder.mkdir(parents=True, exist_ok=True)

    for file in source_folder.glob("*"):
        if not file.is_file():
            continue

        if is_compatible_audio(file):
            copy_file(file, dest_folder / file.name)
        elif is_convertible_audio(file):
            dest_file = dest_folder / file.with_suffix(".flac").name
            convert_to_flac(file, dest_file)
        else:
            print(f"[Skip] Ignored: {file.name}")

    # Copy best album art and embed if needed
    copy_largest_jpg(source_folder, dest_folder)
    apply_album_art_if_missing(dest_folder)


def main():
    for artist_path in ARTISTS:
        artist_src_path = SOURCE_DIR / artist_path
        artist_dest_path = DEST_DIR / artist_path

        if not artist_src_path.exists():
            print(f"Warning: Artist folder not found: {artist_src_path}")
            continue

        # Handle loose tracks in artist root folder
        loose_files = [f for f in artist_src_path.glob("*") if f.is_file()]
        if any(is_compatible_audio(f) or f.suffix.lower() == ".wmv" for f in loose_files):
            process_album_folder(artist_src_path, artist_dest_path)

        # Handle albums in artist folder
        for album in artist_src_path.iterdir():
            if not album.is_dir():
                continue
            dest_album_path = artist_dest_path / album.name
            process_album_folder(album, dest_album_path)

    walk_and_normalise(DEST_DIR, dry_run=False)


if __name__ == "__main__":
    main()
