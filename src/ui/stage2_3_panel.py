"""
Çelikkubbe HMI — Aşama 2 & 3: Otonom Kontrol Paneli
=====================================================
Sol Panel : Yapay Zeka Tehdit Tablosu (QTableWidget, mock veri)
Sağ Panel : Otonom Sistem Durum Göstergeleri (salt okunur)

NOT: Bu aşamalarda manuel yönlendirme ve ateşleme butonları
EKRANDAN TAMAMEN KALDIRILIR (Context-Aware / Decluttering).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


# ── Mock tehdit verileri ──────────────────────────────────────────
MOCK_THREATS = [
    {"id": 1, "tip": "F-16",           "mesafe": "12m",  "durum": "DÜŞMAN",  "oncelik": "KRİTİK"},
    {"id": 2, "tip": "Mini İHA",       "mesafe": "45m",  "durum": "DÜŞMAN",  "oncelik": "YÜKSEK"},
    {"id": 3, "tip": "Helikopter",     "mesafe": "78m",  "durum": "DÜŞMAN",  "oncelik": "ORTA"},
    {"id": 4, "tip": "Balistik Füze",  "mesafe": "120m", "durum": "DÜŞMAN",  "oncelik": "DÜŞÜK"},
    {"id": 5, "tip": "Mini İHA",       "mesafe": "200m", "durum": "BELİRSİZ","oncelik": "DÜŞÜK"},
]

# Öncelik renklerine göre renk haritası
PRIORITY_COLORS = {
    "KRİTİK": "#FF3333",
    "YÜKSEK": "#FF8833",
    "ORTA":   "#FFCC00",
    "DÜŞÜK":  "#33CC33",
}

STATUS_COLORS = {
    "DÜŞMAN":   "#FF3333",
    "BELİRSİZ": "#FFCC00",
    "DOST":     "#3399FF",
}


class Stage23LeftPanel(QWidget):
    """
    Aşama 2/3 — Sol Panel
    Yapay zekanın tespit ettiği hedefleri tehdit önceliğine göre
    sıralayan dinamik tehdit tablosu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._populate_mock_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Başlık
        title = QLabel("⎯ YZ TEHDİT TABLOSU ⎯")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #FF3333; font-size: 14px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(title)

        # Tablo
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["ID", "TİP", "MESAFE", "DURUM", "ÖNCELİK"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)

        # Sütun genişlikleri
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 70)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 80)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 80)

        layout.addWidget(self._table)

        # Özet satırı
        self._summary_label = QLabel()
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary_label.setStyleSheet(
            "color: #A0A0A0; font-size: 12px; padding: 4px;"
        )
        layout.addWidget(self._summary_label)

    def _populate_mock_data(self):
        """Mock tehdit verilerini tabloya yükle."""
        self._table.setRowCount(len(MOCK_THREATS))

        for row, threat in enumerate(MOCK_THREATS):
            # ID
            id_item = QTableWidgetItem(str(threat["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, id_item)

            # Tip
            tip_item = QTableWidgetItem(threat["tip"])
            self._table.setItem(row, 1, tip_item)

            # Mesafe
            mesafe_item = QTableWidgetItem(threat["mesafe"])
            mesafe_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, mesafe_item)

            # Durum (renkli)
            durum_item = QTableWidgetItem(threat["durum"])
            durum_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            durum_color = STATUS_COLORS.get(threat["durum"], "#E0E0E0")
            durum_item.setForeground(QColor(durum_color))
            self._table.setItem(row, 3, durum_item)

            # Öncelik (renkli)
            oncelik_item = QTableWidgetItem(threat["oncelik"])
            oncelik_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            oncelik_color = PRIORITY_COLORS.get(threat["oncelik"], "#E0E0E0")
            oncelik_item.setForeground(QColor(oncelik_color))
            self._table.setItem(row, 4, oncelik_item)

        # Satır yüksekliği
        for row in range(self._table.rowCount()):
            self._table.setRowHeight(row, 32)

        self._summary_label.setText(
            f"Toplam Tespit: {len(MOCK_THREATS)} | "
            f"Aktif Tehdit: {sum(1 for t in MOCK_THREATS if t['durum'] == 'DÜŞMAN')}"
        )

    def update_threats(self, threats: list[dict]):
        """
        Dış kaynaktan gelen tehdit listesini tabloda güncelle.
        Her sözlük: {id, tip, mesafe, durum, oncelik}
        """
        self._table.setRowCount(len(threats))
        for row, threat in enumerate(threats):
            self._table.setItem(row, 0, QTableWidgetItem(str(threat.get("id", ""))))
            self._table.setItem(row, 1, QTableWidgetItem(threat.get("tip", "")))
            self._table.setItem(row, 2, QTableWidgetItem(threat.get("mesafe", "")))

            durum_item = QTableWidgetItem(threat.get("durum", ""))
            durum_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            durum_item.setForeground(
                QColor(STATUS_COLORS.get(threat.get("durum", ""), "#E0E0E0"))
            )
            self._table.setItem(row, 3, durum_item)

            oncelik_item = QTableWidgetItem(threat.get("oncelik", ""))
            oncelik_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            oncelik_item.setForeground(
                QColor(PRIORITY_COLORS.get(threat.get("oncelik", ""), "#E0E0E0"))
            )
            self._table.setItem(row, 4, oncelik_item)


class Stage23RightPanel(QWidget):
    """
    Aşama 2/3 — Sağ Panel
    Salt okunur otonom sistem durum göstergeleri.
    Manuel kontrol yok — sadece büyük, net durum etiketleri.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Başlık
        title = QLabel("⎯ OTONOM SİSTEM DURUMU ⎯")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #3399FF; font-size: 14px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(title)

        # ── Durum göstergeleri ─────────────────────────────
        self._indicators: dict[str, QLabel] = {}

        indicators_data = [
            ("system_mode",   "SİSTEM OTONOM MODDA",     "#33CC33"),
            ("target_lock",   "HEDEF KİLİDİ: AKTİF",    "#FFCC00"),
            ("tracking",      "TAKİP: DEVAM EDİYOR",     "#3399FF"),
            ("ai_status",     "YZ MOTORU: ÇALIŞIYOR",    "#33CC33"),
            ("engagement",    "ANGAJMAN: OTOMATİK",      "#FFCC00"),
        ]

        for key, text, color in indicators_data:
            indicator_frame = QFrame()
            indicator_frame.setObjectName("sidePanel")
            indicator_frame.setStyleSheet(
                f"""
                QFrame#sidePanel {{
                    background-color: #1A1A1A;
                    border: 2px solid {color};
                    border-radius: 6px;
                    padding: 8px;
                }}
                """
            )
            indicator_layout = QVBoxLayout(indicator_frame)
            indicator_layout.setContentsMargins(12, 12, 12, 12)

            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                f"color: {color}; font-size: 16px; font-weight: bold;"
            )
            label.setWordWrap(True)
            indicator_layout.addWidget(label)

            layout.addWidget(indicator_frame)
            self._indicators[key] = label

        layout.addStretch()

        # Alt bilgi
        info_label = QLabel("Manuel kontrol bu modda devre dışıdır.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #707070; font-size: 11px; padding: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def set_indicator(self, key: str, text: str, color: str = None):
        """Belirli bir göstergenin metnini ve isteğe bağlı rengini güncelle."""
        if key in self._indicators:
            self._indicators[key].setText(text)
            if color:
                self._indicators[key].setStyleSheet(
                    f"color: {color}; font-size: 16px; font-weight: bold;"
                )
