import json
from pathlib import Path
from lib.audio_utils import (
    is_compatible_audio,
    convert_to_flac,
    copy_file,
    copy_largest_jpg,
    apply_album_art_if_missing,
)

with open("config.json") as f:
    config = json.load(f)

# Base directories
SOURCE_DIR = Path(config["source_dir"]) # Music source directory
DEST_DIR = Path(config["dest_dir"])     # Where the converted/copied files go

# List of artist folder names to process
ARTISTS = config["artists"]

def main():
    for artist in ARTISTS:
        artist_src_path = SOURCE_DIR / artist
        if not artist_src_path.exists():
            print(f"Warning: Artist folder not found: {artist_src_path}")
            continue

        # Handle loose tracks in the artist root folder
        loose_files = [f for f in artist_src_path.glob("*") if f.is_file()]
        if any(f.suffix.lower() in [".mp3", ".wmv", ".m4a", ".jpg"] for f in loose_files):
            print(f"Processing: {artist} (root-level files)")
            loose_dest = DEST_DIR / artist / "Loose"
            for file in loose_files:
                if file.suffix.lower() == ".jpg":
                    # treat all jpgs as album art candidates here too
                    copy_largest_jpg(artist_src_path, loose_dest)
                elif is_compatible_audio(file):
                    copy_file(file, loose_dest / file.name)
                else:
                    dest_file = loose_dest / file.with_suffix(".flac").name
                    convert_to_flac(file, dest_file)

        # Handle albums in the artist folder
        for album in artist_src_path.iterdir():
            if not album.is_dir():
                continue

            print(f"Processing: {artist}/{album.name}")

            # Destination album path
            dest_album_path = DEST_DIR / artist / album.name

            for file in album.glob("*"):
                if not file.is_file():
                    continue

                if file.suffix.lower() == ".jpg":
                    continue  # We'll handle JPGs in bulk later

                rel_path = file.relative_to(SOURCE_DIR)
                dest_file = DEST_DIR / rel_path

                if is_compatible_audio(file):
                    copy_file(file, dest_file)
                else:
                    dest_file = dest_file.with_suffix(".flac")
                    convert_to_flac(file, dest_file)

            # After processing audio files, copy best album art
            copy_largest_jpg(album, dest_album_path)
            apply_album_art_if_missing(dest_album_path)


if __name__ == "__main__":
    main()
