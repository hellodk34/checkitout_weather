#!/usr/bin/env python3

import os
import subprocess
import sys

from PySide6.QtWidgets import QApplication

from weather_app.ui import WeatherWindow


def _detect_im() -> str:
    for name in ("fcitx5", "ibus-daemon", "ibus"):
        try:
            r = subprocess.run(["pgrep", "-x", name], capture_output=True, timeout=1)
            if r.returncode == 0:
                return "fcitx" if name == "fcitx5" else "ibus"
        except Exception:
            continue
    return "fcitx"


def _setup_input_method():
    if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("XDG_SESSION_TYPE") == "wayland":
        os.environ.pop("QT_IM_MODULE", None)
        return

    im = _detect_im()
    os.environ.setdefault("QT_IM_MODULE", im)
    os.environ.setdefault("XMODIFIERS", f"@im={im}")
    os.environ.setdefault("GTK_IM_MODULE", im)


def main():
    _setup_input_method()
    app = QApplication(sys.argv)
    app.setApplicationName("Checkitout Weather")
    app.setApplicationDisplayName("Checkitout Weather")

    window = WeatherWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
