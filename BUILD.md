MarkerGUI build with PyInstaller

This file documents how to build MarkerGUI into an executable using PyInstaller.

Windows quick build (recommended is one-dir)

1. Install dependencies (use virtualenv):

   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt pyinstaller

2. Use helper script (one-dir by default):

   scripts\build_windows.bat    # on Windows; accepts "onefile" as first argument

3. Output will be in `dist\MarkerGUI` (onedir) or `dist\MarkerGUI.exe` (onefile)

Notes and tips
- config: The application expects a `config/default.json` file. The build script includes the `config` directory so it will be available in `dist`.
- PySide6: PyInstaller generally picks up Qt plugins; if your built GUI shows plugin errors (e.g., platforms plugin), reinstall PySide6 and re-run the build.
- One-file vs One-dir: onefile produces a single executable but extracts bundled files to a temporary folder at runtime; if you need persistent `config` next to exe after installation, prefer `--onedir`.
- If you need to include icons or other assets, use `--add-data "<path>;<dest>"` like the script does for the `config` dir.

Troubleshooting
- If the app fails to find `config/default.json` at runtime, the app will create it using default settings. If you want to ship a pre-configured file, edit `config/default.json` before building.
- For advanced PyInstaller configuration, edit `build_pyinstaller.py` or a spec file (pyinstaller will generate `<name>.spec` after first build).
