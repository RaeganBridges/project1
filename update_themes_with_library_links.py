#!/usr/bin/env python3
"""
Update theme HTML files: link theme-box2 items that match library sets to their
library pages, using box images. Use library filename as image name (.jpg or .png).
"""
import re
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent
LIBRARY_DIR = PROJECT_ROOT / "library"
THEMES_DIR = PROJECT_ROOT / "themes"
IMAGES_DIR = PROJECT_ROOT / "images"

# Library filename -> set name (from headers)
LIBRARY_SET_NAMES = {
    "titanic": "Titanic",
    "colosseum": "Colosseum",
    "concorde": "Concorde",
    "statue-of-liberty": "Statue of Liberty",
    "taj-mahal": "Taj Mahal",
    "the-white-house": "The White House",
    "great-pyramid-of-giza": "Great Pyramid of Giza",
    "empire-state-building": "Empire State Building",
    "trevi-fountain": "Trevi Fountain",
    "singapore": "Singapore",
    "las-vegas": "Las Vegas",
    "new-york-city": "New York City",
    "san-francisco": "San Francisco",
    "tokyo": "Tokyo",
    "london": "London",
    "vespa": "Vespa",
    "yellow-taxi": "Yellow Taxi",
    "ponte-vecchio": "Ponte Vecchio",
    "tranquil-garden": "Tranquil Garden",
    "daffodils": "Daffodils",
    "lotus-flowers": "Lotus Flowers",
    "sunflowers": "Sunflowers",
    "cherry-blossoms": "Cherry Blossoms",
    "roses": "Roses",
    "bouquet-of-roses": "Bouquet of Roses",
    "flower-bouquet": "Flower Bouquet",
    "pretty-pink-flower-bouquet": "Pretty Pink Flower Bouquet",
    "flower-arrangement": "Flower Arrangement",
    "orchid": "Orchid",
    "mini-orchid": "Mini Orchid",
    "plum-blossom": "Plum Blossom",
    "lucky-bamboo": "Lucky Bamboo",
    "chrysanthemum": "Chrysanthemum",
    "succulents": "Succulents",
    "tiny-plants": "Tiny Plants",
    "bonsai-tree": "Bonsai Tree",
    "poinsettia": "Poinsettia",
    "wreath": "Wreath",
    "christmas-tree": "Christmas Tree",
    "family-christmas-tree-decoration": "Family Christmas Tree Decoration",
    "northern-lights-diorama": "Northern Lights Diorama",
    "nutcracker": "Nutcracker",
    "christmas-decor-set": "Christmas Decor Set",
    "santa's-workshop": "Santa's Workshop",
    "winter-holiday-train": "Winter Holiday Train",
    "moving-truck": "Moving Truck",
    "decorative-easter-egg": "Decorative Easter Egg",
    "easter-bunny-and-chick-egg-hunt": "Easter Bunny and Chick Egg Hunt",
    "cute-bunny": "Cute Bunny",
    "exotic-peacock": "Exotic Peacock",
    "sea-animals": "Sea Animals",
    "the-insect-collection": "The Insect Collection",
    "auspicious-dragon": "Auspicious Dragon",
    "year-of-the-dragon": "Year of the Dragon",
    "tales-of-the-space-age": "Tales of the Space Age",
    "vincent-van-gogh-the-starry-night": "Vincent Van Gogh - The Starry Night",
    "vincent-van-gogh-sunflowers": "Vincent Van Gogh - Sunflowers",
    "hokusai-the-great-wave": "Hokusai - The Great Wave",
    "mona-lisa": "Mona Lisa",
    "andy-warhol's-marilyn-monroe": "Andy Warhol's Marilyn Monroe",
    "love": "LOVE",
    "retro-record-player": "Retro Record Player",
    "monkey-d-luffy-figure": "Monkey D. Luffy Figure",
    "buggy-the-clown-figure": "Buggy the Clown Figure",
    "the-going-merry-pirate-ship": "The Going Merry Pirate Ship",
}

# Reverse: set name (normalized) -> (library_filename, display_name)
# Handle variations: "Vespa 125" -> vespa, "Bouquet of Roses" -> bouquet-of-roses
def build_name_to_library():
    result = {}
    for filename, name in LIBRARY_SET_NAMES.items():
        if filename == "no-review":
            continue
        # Exact match
        result[name.lower().strip()] = (filename, name)
        # Common variations
        result[name.lower().replace("'", "'").replace("'", "'")] = (filename, name)
    return result

NAME_TO_LIBRARY = build_name_to_library()

def get_image_ext(filename_base: str) -> str:
    """Return .jpg or .png if image exists, else None."""
    for ext in (".jpg", ".jpeg", ".png"):
        if (IMAGES_DIR / f"{filename_base}{ext}").exists():
            return ext
    return ".jpg"  # default, user can add later

def normalize_theme_name(text: str) -> str:
    """Normalize set name for matching (handle &amp; etc)."""
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    t = t.replace("&amp;", "&").replace("&#39;", "'")
    return t

def match_library_set(theme_text: str) -> Optional[tuple[str, str]]:
    """Return (library_filename, image_ext) if theme text matches a library set, else None."""
    norm = normalize_theme_name(theme_text).lower()
    # Exact match first
    if norm in NAME_TO_LIBRARY:
        lib_filename, _ = NAME_TO_LIBRARY[norm]
        return lib_filename, get_image_ext(lib_filename)
    # Prefix match: "Vespa 125" -> Vespa; prefer longest match
    best = None
    best_len = 0
    for lib_name_lower, (lib_filename, _) in NAME_TO_LIBRARY.items():
        if norm.startswith(lib_name_lower) and len(lib_name_lower) > best_len:
            best = (lib_filename, get_image_ext(lib_filename))
            best_len = len(lib_name_lower)
    return best

def process_theme_file(path: Path) -> tuple[int, list[str]]:
    """Replace matching theme-box2 divs with links+images. Returns (count, missing_images)."""
    text = path.read_text(encoding="utf-8")
    counts = [0]  # use list for closure
    missing: list[str] = []

    # Match <div class="theme-box2">Set Name</div> (plain text, no img, no nested a)
    pattern = re.compile(
        r'<div class="theme-box2">([^<]+?)</div>',
        re.DOTALL,
    )

    def replacer(match):
        inner = match.group(1).strip()
        # Skip if already has img or link (shouldn't match due to [^<]+)
        if "<img" in inner or "<a" in inner:
            return match.group(0)
        matched = match_library_set(inner)
        if matched:
            lib_filename, img_ext = matched
            counts[0] += 1
            img_path = IMAGES_DIR / f"{lib_filename}{img_ext}"
            if not img_path.exists():
                missing.append(f"{lib_filename}{img_ext}")
            return f'<a href="../library/{lib_filename}.html" class="hidden-box-link"><div class="theme-box2"><img src="../images/{lib_filename}{img_ext}" alt="{inner}"></div></a>'
        return match.group(0)

    new_text = pattern.sub(replacer, text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return counts[0], missing

def main():
    total = 0
    all_missing = set()
    for path in sorted(THEMES_DIR.glob("*.html")):
        n, missing = process_theme_file(path)
        if n:
            total += n
            all_missing.update(missing)
            print(f"{path.name}: {n} links added")
    print(f"\nTotal: {total} theme items linked to library")
    if all_missing:
        print(f"\nMissing images ({len(all_missing)}): add these to images/")
        for m in sorted(all_missing):
            print(f"  {m}")

if __name__ == "__main__":
    main()
