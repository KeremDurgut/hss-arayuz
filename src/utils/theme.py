"""
Çelikkubbe HMI — MIL-STD-1472H Uyumlu Taktiksel Tema
=====================================================
Tüm renk kodları, font ayarları ve QSS stil tanımları bu modülde
merkezi olarak yönetilir. Gece modu / NVG uyumlu karanlık tema.
"""

# ─── MIL-STD Renk Kodları ──────────────────────────────────────────
COLOR_ENEMY_RED = "#FF3333"       # Düşman / Ateşleme
COLOR_FRIENDLY_BLUE = "#3399FF"   # Dost Unsur
COLOR_WARNING_AMBER = "#FFCC00"   # Uyarı / ARM (Hazırlık)
COLOR_SAFE_GREEN = "#33CC33"      # Güvenli / Sistem OK

COLOR_BG_DARK = "#1A1A1A"         # Ana arka plan
COLOR_BG_PANEL = "#242424"        # Panel arka planı
COLOR_BG_HEADER = "#1E1E1E"       # Üst çubuk arka planı
COLOR_BG_INPUT = "#2E2E2E"        # Input/ComboBox arka planı
COLOR_BORDER = "#3A3A3A"          # Kenarlık rengi
COLOR_TEXT_PRIMARY = "#E0E0E0"    # Ana metin
COLOR_TEXT_SECONDARY = "#A0A0A0"  # İkincil metin
COLOR_TEXT_DIM = "#707070"        # Soluk metin

FONT_FAMILY = "Consolas, 'Courier New', monospace"
FONT_SIZE_NORMAL = "13px"
FONT_SIZE_LARGE = "15px"
FONT_SIZE_HEADER = "16px"
FONT_SIZE_TITLE = "20px"
FONT_SIZE_HUGE = "28px"


def get_global_stylesheet() -> str:
    """Tüm uygulamaya uygulanacak global QSS stil sayfasını döndürür."""
    return f"""
    /* ── Genel Uygulama Teması ─────────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {COLOR_BG_DARK};
        color: {COLOR_TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_NORMAL};
    }}

    /* ── Üst Durum Çubuğu ──────────────────────────────────── */
    QFrame#headerFrame {{
        background-color: {COLOR_BG_HEADER};
        border-bottom: 2px solid {COLOR_BORDER};
        padding: 4px 8px;
    }}

    /* ── Alt Günlük Konsolu ─────────────────────────────────── */
    QFrame#footerFrame {{
        background-color: {COLOR_BG_HEADER};
        border-top: 2px solid {COLOR_BORDER};
    }}
    QTextEdit#logConsole {{
        background-color: #111111;
        color: {COLOR_SAFE_GREEN};
        font-family: {FONT_FAMILY};
        font-size: 12px;
        border: 1px solid {COLOR_BORDER};
        padding: 4px;
    }}

    /* ── QLabel ─────────────────────────────────────────────── */
    QLabel {{
        color: {COLOR_TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
    }}
    QLabel#headerLabel {{
        font-size: {FONT_SIZE_HEADER};
        font-weight: bold;
        color: {COLOR_FRIENDLY_BLUE};
    }}
    QLabel#telemetryLabel {{
        font-size: {FONT_SIZE_NORMAL};
        color: {COLOR_TEXT_SECONDARY};
    }}
    QLabel#stageIndicator {{
        font-size: {FONT_SIZE_TITLE};
        font-weight: bold;
        color: {COLOR_WARNING_AMBER};
        padding: 2px 10px;
    }}
    QLabel#videoPlaceholder {{
        background-color: #0D0D0D;
        border: 2px solid {COLOR_BORDER};
        color: {COLOR_TEXT_DIM};
        font-size: {FONT_SIZE_LARGE};
        qproperty-alignment: AlignCenter;
    }}
    QLabel#statusGreen {{
        color: {COLOR_SAFE_GREEN};
        font-size: {FONT_SIZE_HUGE};
        font-weight: bold;
    }}
    QLabel#statusAmber {{
        color: {COLOR_WARNING_AMBER};
        font-size: {FONT_SIZE_HUGE};
        font-weight: bold;
    }}
    QLabel#statusRed {{
        color: {COLOR_ENEMY_RED};
        font-size: {FONT_SIZE_HUGE};
        font-weight: bold;
    }}

    /* ── QComboBox (Aşama Seçici) ──────────────────────────── */
    QComboBox {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 3px;
        padding: 4px 8px;
        font-size: {FONT_SIZE_NORMAL};
        min-width: 140px;
    }}
    QComboBox::drop-down {{
        border-left: 1px solid {COLOR_BORDER};
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        selection-background-color: {COLOR_FRIENDLY_BLUE};
        selection-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
    }}

    /* ── QPushButton — Genel ───────────────────────────────── */
    QPushButton {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 8px 12px;
        font-size: {FONT_SIZE_NORMAL};
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #3A3A3A;
        border: 1px solid {COLOR_TEXT_SECONDARY};
    }}
    QPushButton:pressed {{
        background-color: #454545;
    }}
    QPushButton:disabled {{
        background-color: #1E1E1E;
        color: {COLOR_TEXT_DIM};
        border: 1px solid #2A2A2A;
    }}

    /* ── Hedef Seçim Butonları ──────────────────────────────── */
    QPushButton#targetBtn {{
        background-color: #2A2A4A;
        color: {COLOR_FRIENDLY_BLUE};
        border: 2px solid {COLOR_FRIENDLY_BLUE};
        border-radius: 6px;
        font-size: {FONT_SIZE_LARGE};
        font-weight: bold;
        padding: 16px 8px;
        min-height: 50px;
    }}
    QPushButton#targetBtn:hover {{
        background-color: #33336B;
        border: 2px solid #66BBFF;
    }}
    QPushButton#targetBtn:pressed {{
        background-color: {COLOR_FRIENDLY_BLUE};
        color: #FFFFFF;
    }}

    /* ── Sıfırla Butonu ────────────────────────────────────── */
    QPushButton#resetBtn {{
        background-color: #2A2A2A;
        color: {COLOR_TEXT_SECONDARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        font-size: {FONT_SIZE_NORMAL};
        padding: 6px 12px;
    }}
    QPushButton#resetBtn:hover {{
        background-color: #3A3A3A;
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* ── Yön Ok Tuşları ────────────────────────────────────── */
    QPushButton#arrowBtn {{
        background-color: #2A2A2A;
        color: {COLOR_TEXT_PRIMARY};
        border: 2px solid {COLOR_BORDER};
        border-radius: 6px;
        font-size: 22px;
        font-weight: bold;
        min-width: 60px;
        min-height: 50px;
    }}
    QPushButton#arrowBtn:hover {{
        background-color: #3A3A3A;
        border: 2px solid {COLOR_TEXT_SECONDARY};
    }}
    QPushButton#arrowBtn:pressed {{
        background-color: #505050;
    }}

    /* ── ARM Butonu (Sarı / Amber) ─────────────────────────── */
    QPushButton#armBtn {{
        background-color: #3D3200;
        color: {COLOR_WARNING_AMBER};
        border: 2px solid {COLOR_WARNING_AMBER};
        border-radius: 6px;
        font-size: {FONT_SIZE_TITLE};
        font-weight: bold;
        min-height: 55px;
        padding: 8px;
    }}
    QPushButton#armBtn:hover {{
        background-color: #4D4200;
    }}
    QPushButton#armBtn:pressed {{
        background-color: {COLOR_WARNING_AMBER};
        color: #000000;
    }}
    QPushButton#armBtn:disabled {{
        background-color: #1E1E1E;
        color: {COLOR_TEXT_DIM};
        border: 2px solid #2A2A2A;
    }}
    QPushButton#armBtn[armed="true"] {{
        background-color: {COLOR_WARNING_AMBER};
        color: #000000;
    }}

    /* ── ATEŞ Butonu (Kırmızı) ─────────────────────────────── */
    QPushButton#fireBtn {{
        background-color: #3D0000;
        color: {COLOR_ENEMY_RED};
        border: 2px solid {COLOR_ENEMY_RED};
        border-radius: 6px;
        font-size: {FONT_SIZE_TITLE};
        font-weight: bold;
        min-height: 55px;
        padding: 8px;
    }}
    QPushButton#fireBtn:hover:!disabled {{
        background-color: #5D0000;
    }}
    QPushButton#fireBtn:pressed {{
        background-color: {COLOR_ENEMY_RED};
        color: #FFFFFF;
    }}
    QPushButton#fireBtn:disabled {{
        background-color: #1E1E1E;
        color: {COLOR_TEXT_DIM};
        border: 2px solid #2A2A2A;
    }}

    /* ── QListWidget (Hedef Sırası) ────────────────────────── */
    QListWidget {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        font-size: {FONT_SIZE_NORMAL};
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 4px 8px;
        border-bottom: 1px solid #333333;
    }}
    QListWidget::item:selected {{
        background-color: {COLOR_FRIENDLY_BLUE};
        color: #FFFFFF;
    }}

    /* ── QTableWidget (Tehdit Tablosu) ─────────────────────── */
    QTableWidget {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        gridline-color: #333333;
        font-size: {FONT_SIZE_NORMAL};
    }}
    QTableWidget::item {{
        padding: 4px;
    }}
    QHeaderView::section {{
        background-color: {COLOR_BG_HEADER};
        color: {COLOR_WARNING_AMBER};
        border: 1px solid {COLOR_BORDER};
        padding: 6px;
        font-weight: bold;
        font-size: {FONT_SIZE_NORMAL};
    }}

    /* ── QScrollBar ────────────────────────────────────────── */
    QScrollBar:vertical {{
        background-color: {COLOR_BG_DARK};
        width: 10px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLOR_BORDER};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ── Panel Çerçeveleri ─────────────────────────────────── */
    QFrame#sidePanel {{
        background-color: {COLOR_BG_PANEL};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
    }}
    """
