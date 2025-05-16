import shutil
import subprocess
from pathlib import Path

# Define formats known to work well on iPhone/Doppler
COMPATIBLE_EXTENSIONS = {".mp3", ".aac", ".alac", ".m4a", ".flac", ".wav"}


def is_compatible_audio(file_path: Path) -> bool:
    """Return True if the file has a compatible audio format for iPhone."""
    return file_path.suffix.lower() in COMPATIBLE_EXTENSIONS


def convert_to_flac(src_path: Path, dest_path: Path) -> None:
    """Convert a file to FLAC using ffmpeg."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y",
        "-i", str(src_path),
        "-c:a", "flac",
        str(dest_path)
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Converted: {src_path} -> {dest_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {src_path}: {e}")


def copy_file(src_path: Path, dest_path: Path) -> None:
    """Copy a file to the destination, preserving metadata."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest_path)
    print(f"Copied: {src_path} -> {dest_path}")


def copy_largest_jpg(source_album_folder: Path, dest_album_folder: Path) -> None:
    """Find and copy the largest .jpg file in a folder to the destination as 'folder.jpg'."""
    jpgs = list(source_album_folder.glob("*.jpg"))
    if not jpgs:
        return
    # Sort .jpg files by file size (descending)
    jpgs.sort(key=lambda f: f.stat().st_size, reverse=True)
    largest = jpgs[0]
    dest_album_folder.mkdir(parents=True, exist_ok=True)
    dest_path = dest_album_folder / "folder.jpg"
    try:
        shutil.copy2(largest, dest_path)
        print(f"Copied album art: {largest} -> {dest_path}")
    except Exception as e:
        print(f"Failed to copy album art from {largest}: {e}")
