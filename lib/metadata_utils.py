from pathlib import Path
from mutagen import File
import re

NORMALIZATION_EXCEPTIONS = {
    "3t": "3T",
    "4voice": "4Voice",
    "a-ha": "A-ha",
    "aco": "ACO",
    "blyz": "BLYZ",
    "blink-182": "blink-182",
    "cc": "CC",
    "cj": "CJ",
    "das efx": "Das EFX",
    "deus": "dEUS",
    "difranco": "DiFranco",
    "d.j.": "D.J.",
    "dj": "DJ",
    "dr.": "Dr.",
    "efx": "EFX",
    "feat": "feat.",
    "feat.": "feat.",
    "id": "ID",
    "jc": "JC",
    "krs": "KRS",
    "la": "la",
    "le peuple de l'herbe": "Le Peuple de l'Herbe",
    "lsg": "LSG",
    "ltj bukem": "LTJ Bukem",
    "m.anifest": "M.anifest",
    "m3nsa": "M3NSA",
    "mc": "MC",
    "mc's": "MC's",
    "mf": "MF",
    "noe": "NOE",
    "outkast": "OutKast",
    "p!nk": "P!nk",
    "pj": "PJ",
    "rmf": "RMF",
    "rpm": "RPM",
    "rza": "RZA",
    "shack*shakers": "Shack*Shakers",
    "so": "SO",
    "synthi a": "Synthi A",
    "t. rex": "T. Rex",
    "tesseract": "TesseracT",
    "the klf": "The KLF",
    "tv": "TV",
    "tz": "TZ",
    "u2": "U2",
    "ub40": "UB40",
    "uk": "UK",
    "us69": "US69",
    "unkle": "UNKLE",
    "vdt.": "VDT.",
    "xtc": "XTC",
    "yage": "YAGE",
    "younotus": "YOUNOTUS",
}


LOWERCASE_ARTICLES = {
    "a",
    "an",
    "and",
    "at",
    "but",
    "by",
    "de",
    "for",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}


HACK_EXCEPTIONS = {
    "synthi a": "Synthi A",
}


ROMAN_PATTERN = re.compile(r"^(?=[ivxlcdm]+$)[ivxlcdm]{1,15}$", re.IGNORECASE)
INITIALS_PATTERN = re.compile(r"^(?:[A-Z]\.){2,}[A-Z]?$", re.IGNORECASE)


def smart_capitalize(token: str, index: int = 0) -> str:
    if not token:
        return ""

    key = token.lower()

    if index != 0 and key in LOWERCASE_ARTICLES:
        return key

    if key in NORMALIZATION_EXCEPTIONS:
        return NORMALIZATION_EXCEPTIONS[key]

    if INITIALS_PATTERN.match(token):
        return token.upper()

    if ROMAN_PATTERN.match(token):
        return token.upper()

    if token.lower().startswith("mc") and len(token) > 2:
        return "Mc" + token[2].upper() + token[3:]

    if "'" in token:
        parts = token.split("'")
        if len(parts) == 2 and all(parts):
            return parts[0].capitalize() + "'" + parts[1].capitalize()

    # Capitalize hyphenated parts separately (after other checks)
    if "-" in token:
        return "-".join(smart_capitalize(part, i) for i, part in enumerate(token.split("-")))

    return token.capitalize()


DELIMITER_PATTERN = r"([,/;\\]|\s+)"


def apply_to_entire_name(name: str) -> str:
    # print(f"[apply_to_entire_name] '{name}'")
    if not name:
        return ""

    # Handle content inside parentheses recursively
    match = re.match(r"(.*?)\((.*?)\)(.*)", name)
    if match:
        before, inside, after = match.groups()
        return (
            apply_to_entire_name(before)
            + "("
            + apply_to_entire_name(inside)
            + ")"
            + apply_to_entire_name(after)
        )

    # Split into tokens while preserving delimiters
    tokens = re.split(DELIMITER_PATTERN, name)

    result = []
    for i, token in enumerate(tokens):
        if re.match(DELIMITER_PATTERN, token):
            result.append(token)  # Keep the delimiter untouched
        else:
            result.append(smart_capitalize(token.strip(), i))

    return "".join(result)


def normalise_artist_name(raw_name: str) -> str:
    key = raw_name.lower().strip()
    if key in HACK_EXCEPTIONS:
        return HACK_EXCEPTIONS[key]

    if key.endswith(", the"):
        stripped = raw_name[:-5].strip()  # remove ", the"
        return "The " + apply_to_entire_name(stripped)

    return apply_to_entire_name(raw_name)


def process_audio_file(file_path: Path, dry_run: bool = True):
    audio = File(file_path, easy=True)
    if not audio:
        return

    changed = False
    for tag in ["artist", "albumartist"]:
        if tag in audio:
            original = audio[tag][0]
            normalised = normalise_artist_name(original)
            if normalised != original:
                print(f"[Fix] {file_path.name} | {tag}: '{original}' → '{normalised}'")
                if not dry_run:
                    audio[tag] = normalised
                    changed = True

    if changed:
        audio.save()


def walk_and_normalise(base_path: Path, dry_run: bool = True):
    for file in base_path.rglob("*"):
        if file.suffix.lower() in {".mp3", ".flac", ".m4a"}:
            process_audio_file(file, dry_run=dry_run)
