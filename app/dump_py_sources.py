#!/usr/bin/env python3
"""
Dump all .py files under a folder (default: ./app) in this format:

file name  - app/path/to/file.py
code
<contents of file>

----------------------------------------------------------------------

Usage:
  python dump_py_sources.py            # assumes ./app
  python dump_py_sources.py app        # explicit root
  python dump_py_sources.py app -o out.txt  # write to file

Notes:
- Skips common junk dirs: __pycache__, .git, venv/.venv, env, build, dist, caches
- Tries several encodings (utf-8, utf-8-sig, cp932, latin-1)
"""

from pathlib import Path
import argparse
import sys

SKIP_DIR_NAMES = {
    "__pycache__", ".git", "venv", ".venv", "env", ".env",
    "build", "dist", ".mypy_cache", ".pytest_cache", ".ruff_cache"
}

SEPARATOR = "\n\n----------------------------------------------------------------------\n\n"

def readable_text(p: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp932", "latin-1"):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    # Fallback: decode bytes with replacement to avoid crashing
    return p.read_bytes().decode("utf-8", errors="replace")

def iter_py_files(root: Path):
    for path in root.rglob("*.py"):
        # Skip files inside unwanted directories
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path

def dump_sources(root: Path, out_stream):
    root = root.resolve()
    base_label = root.name  # e.g., "app"

    files = sorted(
        (p for p in iter_py_files(root)),
        key=lambda p: f"{base_label}/{p.relative_to(root).as_posix()}"
    )

    for i, p in enumerate(files):
        rel = p.relative_to(root).as_posix()
        labeled_path = f"{base_label}/{rel}"  # e.g., app/dependencies/vector_database.py
        out_stream.write(f"file name  - {labeled_path}\n")
        out_stream.write("code\n")
        out_stream.write(readable_text(p))
        if i != len(files) - 1:
            out_stream.write(SEPARATOR)

def main():
    ap = argparse.ArgumentParser(description="Dump all .py files from a folder in a formatted, concatenated output.")
    ap.add_argument("root", nargs="?", default="/home/aisl/okadahd-quotation-app-phase1-backen_fatima/app", help="Root folder to scan (default: app)")
    ap.add_argument("-o", "--output", default="/home/aisl/okadahd-quotation-app-phase1-backen_fatima/app/all_py_sources.txt",  help="Write result to this file instead of stdout")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        print(f"Error: '{root}' is not a folder.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            dump_sources(root, f)
        print(f"Done. Wrote output to: {out_path}")
    else:
        dump_sources(root, sys.stdout)

if __name__ == "__main__":
    main()

