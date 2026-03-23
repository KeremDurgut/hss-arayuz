"""
Çelikkubbe HMI — Aşama 1: Manuel Angajman Paneli
==================================================
Sol Panel : Hızlı Hedef Seçim Matrisi + Sıralama Listesi
Sağ Panel : Taret Yönlendirme Ok Tuşları + ARM/ATEŞ Mekanizması
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class Stage1LeftPanel(QWidget):
    """
    Aşama 1 — Sol Panel
    Hakem zarfı hedef sırasını hızlıca girmek için 4 büyük hedef
    butonu, sıralama listesi ve sıfırlama butonu.
    """

    # Hedef sırası değiştiğinde yayımlanır: list[str]
    target_order_changed = Signal(list)

    TARGET_TYPES = ["F-16", "Helikopter", "Mini İHA", "Balistik Füze"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_order: list[str] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Başlık
        title = QLabel("⎯ HEDEF SEÇİM MATRİSİ ⎯")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #3399FF; font-size: 14px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(title)

        # Hedef seçim butonları (2x2 grid)
        grid = QGridLayout()
        grid.setSpacing(6)
        self._target_buttons: list[QPushButton] = []
        icons = ["✈️", "🚁", "🛸", "🚀"]
        for i, (target_name, icon) in enumerate(zip(self.TARGET_TYPES, icons)):
            btn = QPushButton(f"{icon}\n{target_name}")
            btn.setObjectName("targetBtn")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(65)
            btn.clicked.connect(lambda checked, t=target_name: self._on_target_clicked(t))
            grid.addWidget(btn, i // 2, i % 2)
            self._target_buttons.append(btn)
        layout.addLayout(grid)

        # Sıfırla butonu
        reset_btn = QPushButton("↻  SIFIRLA")
        reset_btn.setObjectName("resetBtn")
        reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(reset_btn)

        # Sıralama listesi
        order_label = QLabel("HEDEF SIRASI:")
        order_label.setStyleSheet("color: #A0A0A0; font-size: 12px; padding-top: 4px;")
        layout.addWidget(order_label)

        self._order_list = QListWidget()
        self._order_list.setMaximumHeight(150)
        layout.addWidget(self._order_list)

        layout.addStretch()

    def _on_target_clicked(self, target_name: str):
        """Hedef butonuna tıklandığında sıraya ekle."""
        order_num = len(self._target_order) + 1
        self._target_order.append(target_name)
        self._order_list.addItem(f"{order_num}. {target_name}")
        self.target_order_changed.emit(self._target_order.copy())

    def _on_reset(self):
        """Hedef sırasını sıfırla."""
        self._target_order.clear()
        self._order_list.clear()
        self.target_order_changed.emit([])

    def get_target_order(self) -> list[str]:
        """Mevcut hedef sırasını döndür."""
        return self._target_order.copy()


class Stage1RightPanel(QWidget):
    """
    Aşama 1 — Sağ Panel
    Taret yönlendirme ok tuşları ve MIL-STD uyumlu iki aşamalı
    ateşleme mekanizması (ARM → ATEŞ).
    """

    # Taret yönlendirme sinyalleri: direction string
    turret_command = Signal(str)
    # Ateşleme sinyali
    fire_command = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_armed = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Başlık
        title = QLabel("⎯ TARET KONTROLÜ ⎯")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #3399FF; font-size: 14px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(title)

        # Ok tuşları (D-Pad düzeni)
        arrow_frame = QFrame()
        arrow_layout = QGridLayout(arrow_frame)
        arrow_layout.setSpacing(4)

        # Yukarı
        btn_up = QPushButton("▲")
        btn_up.setObjectName("arrowBtn")
        btn_up.clicked.connect(lambda: self._on_direction("UP"))
        arrow_layout.addWidget(btn_up, 0, 1)

        # Sol
        btn_left = QPushButton("◀")
        btn_left.setObjectName("arrowBtn")
        btn_left.clicked.connect(lambda: self._on_direction("LEFT"))
        arrow_layout.addWidget(btn_left, 1, 0)

        # Merkez (boş alan veya gösterge)
        center_label = QLabel("◎")
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_label.setStyleSheet("color: #707070; font-size: 24px;")
        arrow_layout.addWidget(center_label, 1, 1)

        # Sağ
        btn_right = QPushButton("▶")
        btn_right.setObjectName("arrowBtn")
        btn_right.clicked.connect(lambda: self._on_direction("RIGHT"))
        arrow_layout.addWidget(btn_right, 1, 2)

        # Aşağı
        btn_down = QPushButton("▼")
        btn_down.setObjectName("arrowBtn")
        btn_down.clicked.connect(lambda: self._on_direction("DOWN"))
        arrow_layout.addWidget(btn_down, 2, 1)

        layout.addWidget(arrow_frame)
        layout.addSpacing(16)

        # ── İki Aşamalı Ateşleme Mekanizması ──────────────
        fire_title = QLabel("⎯ ATEŞLeme SİSTEMİ ⎯")
        fire_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fire_title.setStyleSheet(
            "color: #FFCC00; font-size: 13px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(fire_title)

        # ARM butonu
        self._arm_btn = QPushButton("🔒  ARM")
        self._arm_btn.setObjectName("armBtn")
        self._arm_btn.clicked.connect(self._on_arm)
        layout.addWidget(self._arm_btn)

        # ATEŞ butonu — başlangıçta devre dışı
        self._fire_btn = QPushButton("🔥  ATEŞ")
        self._fire_btn.setObjectName("fireBtn")
        self._fire_btn.setEnabled(False)
        self._fire_btn.clicked.connect(self._on_fire)
        layout.addWidget(self._fire_btn)

        # Durum etiketi
        self._status_label = QLabel("DURUM: GÜVENLİ")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(
            "color: #33CC33; font-size: 13px; font-weight: bold; padding: 6px;"
        )
        layout.addWidget(self._status_label)

        layout.addStretch()

    def _on_direction(self, direction: str):
        """Yön komutu yayımla."""
        self.turret_command.emit(direction)

    def _on_arm(self):
        """ARM/DISARM geçişi."""
        self._is_armed = not self._is_armed
        if self._is_armed:
            self._arm_btn.setText("🔓  ARMED")
            self._arm_btn.setProperty("armed", True)
            self._arm_btn.style().unpolish(self._arm_btn)
            self._arm_btn.style().polish(self._arm_btn)
            self._fire_btn.setEnabled(True)
            self._status_label.setText("DURUM: HAZIR (ARMED)")
            self._status_label.setStyleSheet(
                "color: #FFCC00; font-size: 13px; font-weight: bold; padding: 6px;"
            )
        else:
            self._arm_btn.setText("🔒  ARM")
            self._arm_btn.setProperty("armed", False)
            self._arm_btn.style().unpolish(self._arm_btn)
            self._arm_btn.style().polish(self._arm_btn)
            self._fire_btn.setEnabled(False)
            self._status_label.setText("DURUM: GÜVENLİ")
            self._status_label.setStyleSheet(
                "color: #33CC33; font-size: 13px; font-weight: bold; padding: 6px;"
            )

    def _on_fire(self):
        """Ateş komutu. Ateş sonrası otomatik DISARM."""
        self.fire_command.emit()
        # Ateş sonrası güvenli moda dön
        self._is_armed = False
        self._arm_btn.setText("🔒  ARM")
        self._arm_btn.setProperty("armed", False)
        self._arm_btn.style().unpolish(self._arm_btn)
        self._arm_btn.style().polish(self._arm_btn)
        self._fire_btn.setEnabled(False)
        self._status_label.setText("DURUM: ATEŞ EDİLDİ — GÜVENLİYE DÖNÜLDÜ")
        self._status_label.setStyleSheet(
            "color: #FF3333; font-size: 13px; font-weight: bold; padding: 6px;"
        )
