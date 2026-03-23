"""
Çelikkubbe HMI — Uygulama Giriş Noktası
=========================================
QApplication oluşturur, MIL-STD taktiksel temayı uygular
ve MainWindow'u başlatır.

Kullanım:
    cd /home/kerman/Projeler/hss-arayuz
    python src/main.py
"""

import sys
import os

# src/ dizinini Python modül arama yoluna ekle
# (from core.xxx, from ui.xxx, from utils.xxx import'ları çalışsın diye)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from utils.theme import get_global_stylesheet
from ui.main_window import MainWindow


def main():
    """Uygulamayı başlatır."""
    app = QApplication(sys.argv)

    # Uygulama geneli varsayılan font
    default_font = QFont("Consolas", 11)
    default_font.setStyleHint(QFont.StyleHint.Monospace)
    app.setFont(default_font)

    # MIL-STD taktiksel gece modu temasını uygula
    app.setStyleSheet(get_global_stylesheet())

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
