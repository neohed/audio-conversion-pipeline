import shutil
import subprocess
import mimetypes

from pathlib import Path
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC, error as ID3Error
from mutagen import MutagenError

# Define formats known to work well on iPhone/Doppler
COMPATIBLE_EXTENSIONS = {".mp3", ".aac", ".alac", ".m4a", ".flac", ".wav"}


def is_compatible_audio(file_path: Path) -> bool:
    """Return True if the file has a compatible audio format for iPhone."""
    return file_path.suffix.lower() in COMPATIBLE_EXTENSIONS


def is_convertible_audio(file_path: Path) -> bool:
    return file_path.suffix.lower() in {".wmv", ".wma"}


def convert_to_flac(src_path: Path, dest_path: Path) -> None:
    """Convert a file to FLAC using ffmpeg."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-y", "-i", str(src_path), "-c:a", "flac", str(dest_path)]
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


def has_embedded_artwork(file_path: Path) -> bool:
    try:
        suffix = file_path.suffix.lower()

        if suffix == ".flac":
            audio = FLAC(file_path)
            return any(p.type == 3 for p in audio.pictures)  # type 3 = front cover

        elif suffix == ".mp3":
            audio = MP3(file_path)
            return "APIC:" in audio.tags if audio.tags else False

        elif suffix in {".m4a", ".mp4"}:
            audio = MP4(file_path)
            return "covr" in audio.tags if audio.tags else False

    except (MutagenError, ID3Error, Exception) as e:
        print(f"[WARN] Failed to check artwork in {file_path}: {e}")

    return False


def embed_album_art(file_path: Path, image_path: Path) -> None:
    try:
        suffix = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(image_path)
        image_data = image_path.read_bytes()

        if suffix == ".flac":
            audio = FLAC(file_path)
            picture = Picture()
            picture.data = image_data
            picture.type = 3  # front cover
            picture.mime = mime_type or "image/jpeg"
            picture.desc = "cover"
            audio.clear_pictures()
            audio.add_picture(picture)
            audio.save()
            print(f"[✔] Embedded artwork into {file_path.name}")

        elif suffix == ".mp3":
            audio = MP3(file_path, ID3=ID3)
            try:
                audio.add_tags()
            except ID3Error:
                pass
            audio.tags.delall("APIC")  # Remove existing
            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime=mime_type or "image/jpeg",
                    type=3,  # front cover
                    desc="cover",
                    data=image_data,
                )
            )
            audio.save()
            print(f"[✔] Embedded artwork into {file_path.name}")

        elif suffix in {".m4a", ".mp4"}:
            audio = MP4(file_path)
            covr_type = (
                MP4Cover.FORMAT_JPEG if image_path.suffix.lower() == ".jpg" else MP4Cover.FORMAT_PNG
            )
            audio["covr"] = [MP4Cover(image_data, imageformat=covr_type)]
            audio.save()
            print(f"[✔] Embedded artwork into {file_path.name}")

        else:
            print(f"[⚠] Unsupported file type: {file_path.name}")

    except Exception as e:
        print(f"[✘] Failed to embed artwork into {file_path.name}: {e}")


def apply_album_art_if_missing(dest_album_folder: Path) -> None:
    """Find the largest jpg in the folder and embed it into all audio files that lack artwork."""
    image_path = dest_album_folder / "folder.jpg"
    if not image_path.exists():
        print(f"[⚠] No folder.jpg in {dest_album_folder}, skipping embed.")
        return

    for file in dest_album_folder.glob("*"):
        if not file.is_file() or file.suffix.lower() not in {".flac", ".mp3", ".m4a"}:
            continue

        if has_embedded_artwork(file):
            continue

        embed_album_art(file, image_path)
