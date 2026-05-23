#!/usr/bin/env python3

import sys

from PySide6.QtWidgets import QApplication

from weather_app.ui import WeatherWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Checkitout Weather")
    app.setApplicationDisplayName("Checkitout Weather")

    window = WeatherWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
