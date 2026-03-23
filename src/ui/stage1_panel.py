"""
Çelikkubbe HMI — Aşama 1: Manuel Angajman Paneli
==================================================
Sol Panel : Kompakt hedef angajman seçimi + bilgi gösterimi
Sağ Panel : Taret yönlendirme ok tuşları + ARM/ATEŞ mekanizması
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class Stage1LeftPanel(QWidget):
    """
    Aşama 1 — Sol Panel
    Sabit düzen hedef seçim paneli. Butonlar seçildiğinde yerinde
    görsel durum değiştirir (sıra numarası + renk). Hiçbir widget
    gizlenmez veya yer değiştirmez.
    """

    MAX_TARGETS = 4

    # Hedef sırası değiştiğinde yayımlanır: list[str]
    target_order_changed = Signal(list)

    TARGET_TYPES = ["F-16", "Helikopter", "Mini IHA", "B. Fuze"]
    TARGET_CODES = ["F16", "HEL", "IHA", "BFZ"]

    # Buton durumlarına göre stiller
    _STYLE_IDLE = (
        "QPushButton#targetBtn {"
        "  background-color: #2A2A4A; color: #3399FF;"
        "  border: 2px solid #3399FF; border-radius: 4px;"
        "  font-size: 12px; font-weight: bold; padding: 4px 6px;"
        "  text-align: left;"
        "}"
        "QPushButton#targetBtn:hover {"
        "  background-color: #33336B; border: 2px solid #66BBFF;"
        "}"
    )
    _STYLE_SELECTED = (
        "QPushButton#targetBtn {"
        "  background-color: #1A2E1A; color: #33CC33;"
        "  border: 2px solid #33CC33; border-radius: 4px;"
        "  font-size: 12px; font-weight: bold; padding: 4px 6px;"
        "  text-align: left;"
        "}"
    )
    _STYLE_LOCKED = (
        "QPushButton#targetBtn {"
        "  background-color: #1E1E1E; color: #707070;"
        "  border: 2px solid #2A2A2A; border-radius: 4px;"
        "  font-size: 12px; font-weight: bold; padding: 4px 6px;"
        "  text-align: left;"
        "}"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_order: list[str] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        # ── Başlık ─────────────────────────────────────────
        self._title = QLabel("HEDEF SECIM")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 12px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #3A3A3A;"
            "margin-bottom: 4px;"
        )
        layout.addWidget(self._title)

        # ── Hedef butonları (dikey, sabit yerleşim) ─────────
        self._target_buttons: list[QPushButton] = []
        self._button_base_texts: list[str] = []

        for code, target_name in zip(self.TARGET_CODES, self.TARGET_TYPES):
            base_text = f"[{code}]  {target_name}"
            btn = QPushButton(base_text)
            btn.setObjectName("targetBtn")
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            btn.setFixedHeight(36)
            btn.setStyleSheet(self._STYLE_IDLE)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, idx=len(self._target_buttons): self._on_target_clicked(idx)
            )
            layout.addWidget(btn)
            self._target_buttons.append(btn)
            self._button_base_texts.append(base_text)

        layout.addSpacing(6)

        # ── Durum / Özet alanı (her zaman görünür) ──────────
        self._summary_label = QLabel("0 / 4  hedef secildi")
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet(
            "color: #707070; font-size: 11px; padding: 4px 2px;"
            "border-top: 1px solid #3A3A3A; margin-top: 2px;"
        )
        layout.addWidget(self._summary_label)

        # ── Boşluk doldurucu (paneli doldurur) ──────────────
        layout.addStretch(1)

        # ── SIFIRLA butonu (panelin altına sabitlenmiş) ─────
        self._reset_btn = QPushButton("SIFIRLA")
        self._reset_btn.setObjectName("resetBtn")
        self._reset_btn.setFixedHeight(28)
        self._reset_btn.setStyleSheet(
            "QPushButton#resetBtn {"
            "  font-size: 11px; padding: 2px 8px;"
            "  background-color: #2A2A2A; color: #A0A0A0;"
            "  border: 1px solid #3A3A3A; border-radius: 3px;"
            "}"
            "QPushButton#resetBtn:hover {"
            "  background-color: #3A3A3A; color: #E0E0E0;"
            "}"
        )
        self._reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self._reset_btn)

    def _on_target_clicked(self, btn_index: int):
        """Hedef butonuna tıklandığında sıraya ekle ve görsel durumu güncelle."""
        if len(self._target_order) >= self.MAX_TARGETS:
            return

        target_name = self.TARGET_TYPES[btn_index]
        order_num = len(self._target_order) + 1
        self._target_order.append(target_name)

        # Tıklanan butonu seçili olarak işaretle
        btn = self._target_buttons[btn_index]
        btn.setText(f"  {order_num}.  {self._button_base_texts[btn_index]}")
        btn.setStyleSheet(self._STYLE_SELECTED)
        btn.setEnabled(False)

        # Özet güncelle
        self._update_summary()
        self.target_order_changed.emit(self._target_order.copy())

        # 4 hedef tamamlandıysa kalan butonları kilitle
        if len(self._target_order) >= self.MAX_TARGETS:
            self._lock_remaining()

    def _lock_remaining(self):
        """Seçilmemiş butonları kilitli stile çevir."""
        for i, btn in enumerate(self._target_buttons):
            if btn.isEnabled():
                btn.setStyleSheet(self._STYLE_LOCKED)
                btn.setEnabled(False)

        self._title.setText("ANGAJMAN TAMAM")
        self._title.setStyleSheet(
            "color: #33CC33; font-size: 12px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #33CC33;"
            "margin-bottom: 4px;"
        )

    def _update_summary(self):
        """Durum özetini güncelle."""
        count = len(self._target_order)
        if count == 0:
            self._summary_label.setText("0 / 4  hedef secildi")
            self._summary_label.setStyleSheet(
                "color: #707070; font-size: 11px; padding: 4px 2px;"
                "border-top: 1px solid #3A3A3A; margin-top: 2px;"
            )
        elif count < self.MAX_TARGETS:
            order_str = " > ".join(
                self.TARGET_CODES[self.TARGET_TYPES.index(t)]
                for t in self._target_order
            )
            self._summary_label.setText(f"{count}/4  |  {order_str}")
            self._summary_label.setStyleSheet(
                "color: #3399FF; font-size: 11px; font-weight: bold;"
                "padding: 4px 2px; border-top: 1px solid #3A3A3A; margin-top: 2px;"
            )
        else:
            order_str = " > ".join(
                self.TARGET_CODES[self.TARGET_TYPES.index(t)]
                for t in self._target_order
            )
            self._summary_label.setText(f"4/4  |  {order_str}")
            self._summary_label.setStyleSheet(
                "color: #33CC33; font-size: 11px; font-weight: bold;"
                "padding: 4px 2px; border-top: 1px solid #33CC33; margin-top: 2px;"
            )

    def _on_reset(self):
        """Hedef sırasını sıfırla — tüm butonları başlangıç durumuna döndür."""
        self._target_order.clear()

        # Butonları sıfırla
        for i, btn in enumerate(self._target_buttons):
            btn.setText(self._button_base_texts[i])
            btn.setStyleSheet(self._STYLE_IDLE)
            btn.setEnabled(True)

        # Başlık ve özeti sıfırla
        self._title.setText("HEDEF SECIM")
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 12px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #3A3A3A;"
            "margin-bottom: 4px;"
        )
        self._update_summary()
        self.target_order_changed.emit([])

    def get_target_order(self) -> list[str]:
        """Mevcut hedef sırasını döndür."""
        return self._target_order.copy()


class Stage1RightPanel(QWidget):
    """
    Aşama 1 — Sağ Panel
    Taret yönlendirme ok tuşları ve MIL-STD uyumlu iki aşamalı
    ateşleme mekanizması (ARM / ATES).
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
        title = QLabel("TARET KONTROLU")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #3399FF; font-size: 14px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #3A3A3A;"
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

        # Merkez
        center_label = QLabel("+")
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_label.setStyleSheet("color: #707070; font-size: 22px; font-weight: bold;")
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
        layout.addSpacing(12)

        # ── Ateşleme Sistemi ───────────────────────────────
        fire_title = QLabel("ATESLEME SISTEMI")
        fire_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fire_title.setStyleSheet(
            "color: #FFCC00; font-size: 13px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(fire_title)

        # ARM butonu
        self._arm_btn = QPushButton("[SAFE]  ARM")
        self._arm_btn.setObjectName("armBtn")
        self._arm_btn.clicked.connect(self._on_arm)
        layout.addWidget(self._arm_btn)

        # ATEŞ butonu — başlangıçta devre dışı
        self._fire_btn = QPushButton(">>> ATES <<<")
        self._fire_btn.setObjectName("fireBtn")
        self._fire_btn.setEnabled(False)
        self._fire_btn.clicked.connect(self._on_fire)
        layout.addWidget(self._fire_btn)

        # Durum etiketi
        self._status_label = QLabel("DURUM: GUVENLI")
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
            self._arm_btn.setText("[!] ARMED")
            self._arm_btn.setProperty("armed", True)
            self._arm_btn.style().unpolish(self._arm_btn)
            self._arm_btn.style().polish(self._arm_btn)
            self._fire_btn.setEnabled(True)
            self._status_label.setText("DURUM: HAZIR (ARMED)")
            self._status_label.setStyleSheet(
                "color: #FFCC00; font-size: 13px; font-weight: bold; padding: 6px;"
            )
        else:
            self._arm_btn.setText("[SAFE]  ARM")
            self._arm_btn.setProperty("armed", False)
            self._arm_btn.style().unpolish(self._arm_btn)
            self._arm_btn.style().polish(self._arm_btn)
            self._fire_btn.setEnabled(False)
            self._status_label.setText("DURUM: GUVENLI")
            self._status_label.setStyleSheet(
                "color: #33CC33; font-size: 13px; font-weight: bold; padding: 6px;"
            )

    def _on_fire(self):
        """Ateş komutu. Ateş sonrası otomatik DISARM."""
        self.fire_command.emit()
        # Ateş sonrası güvenli moda dön
        self._is_armed = False
        self._arm_btn.setText("[SAFE]  ARM")
        self._arm_btn.setProperty("armed", False)
        self._arm_btn.style().unpolish(self._arm_btn)
        self._arm_btn.style().polish(self._arm_btn)
        self._fire_btn.setEnabled(False)
        self._status_label.setText("DURUM: ATES EDILDI")
        self._status_label.setStyleSheet(
            "color: #FF3333; font-size: 13px; font-weight: bold; padding: 6px;"
        )
