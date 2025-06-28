"""
PyInstaller build helper for MarkerGUI

Usage:
    python build_pyinstaller.py         # default (onedir)
    python build_pyinstaller.py --onefile
    python build_pyinstaller.py --name MyAppName --onefile

This script runs PyInstaller with recommended arguments for this project:
- On Windows it uses semicolon-separated add-data
- Includes `config/default.json` and `src/markergui/config` into the build
- Uses --onedir by default because the app expects a "config" directory next to the exe

Notes:
- Install PyInstaller first: pip install -r requirements.txt pyinstaller
- You can pass additional args (they are forwarded to PyInstaller)
"""

from pathlib import Path
import sys
import os
import shutil

try:
    import PyInstaller.__main__ as pyi
except Exception:
    print("PyInstaller not found. Install via: pip install pyinstaller")
    sys.exit(1)

ROOT = Path(__file__).parent
MAIN_FILE = ROOT / "main.py"
CONFIG_DIR = ROOT / "config"
SRC_MARKERGUI_CONFIG = ROOT / "src" / "markergui" / "config"

# Default settings
DEFAULT_NAME = "MarkerGUI"
DEFAULT_MODE = "onedir"  # change to onefile for single-file exe

# Use proper path separator for add-data on current OS (Windows uses ';')
DATA_SEP = ";" if os.name == "nt" else ":"


def build(name: str = DEFAULT_NAME, onefile: bool = False, extra_args=None):
    extra_args = extra_args or []

    # Common args
    args = [
        str(MAIN_FILE),
        "--noconfirm",
        "--clean",
        "--windowed",  # GUI app, don't show console
        "--name",
        name,
    ]

    # mode
    if onefile:
        args.append("--onefile")
    else:
        args.append("--onedir")

    # Ensure PyInstaller can import the package from src
    src_path = ROOT / "src"
    if src_path.exists():
        args += ["--paths", str(src_path)]

    # Include config folder root/config
    if CONFIG_DIR.exists():
        args += ["--add-data", f"{str(CONFIG_DIR)}{DATA_SEP}config"]

    # Also include the package config under src (safe-guard)
    if SRC_MARKERGUI_CONFIG.exists():
        args += ["--add-data", f"{str(SRC_MARKERGUI_CONFIG)}{DATA_SEP}markergui/config"]

    # Hide PyInstaller log if not verbose
    args += extra_args

    print("Running PyInstaller with arguments:")
    print(" ".join(args))

    # Run pyinstaller
    pyi.run(args)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build MarkerGUI using PyInstaller")
    parser.add_argument("--onefile", action="store_true", help="Build as a single-file executable")
    parser.add_argument("--name", type=str, default=DEFAULT_NAME, help="Name of executable")
    parser.add_argument("--extra", type=str, nargs="*", help="Extra args forwarded to pyinstaller")
    args = parser.parse_args()

    build(name=args.name, onefile=args.onefile, extra_args=args.extra)
