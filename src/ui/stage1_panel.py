"""
Çelikkubbe HMI — Aşama 1: Manuel Angajman Paneli
==================================================
Sol Panel : Hedef angajman seçimi + angajman kuyruğu + görev bilgisi
Sağ Panel : Taret yönlendirme ok tuşları + ARM/ATEŞ mekanizması

Tasarım Felsefesi (MIL-STD-1472H):
  - Anlık okuma: Kullanıcı periferik görüşle durumu kavrayabilmeli
  - Sabit düzen: hiçbir widget gizlenmez veya yer değiştirmez
  - Renk kodları: IMHA=kırmızı, AKTIF=amber, BEKLE=mavi soluk
  - Her hedef tipi benzersiz renk aksan ile ayrışır
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


# ── Hedef Durumları ────────────────────────────────────────────────
TARGET_STATUS_IDLE = "IDLE"
TARGET_STATUS_DESTROYED = "DESTROYED"
TARGET_STATUS_ACTIVE = "ACTIVE"
TARGET_STATUS_PENDING = "PENDING"

# ── Her hedef tipi için benzersiz aksan rengi ──────────────────────
TARGET_ACCENTS = {
    "F16": "#4DA6FF",   # Açık mavi
    "HEL": "#66CC66",   # Yeşil
    "IHA": "#CC66FF",   # Mor
    "BFZ": "#FF8844",   # Turuncu
}


class _EngagementRow(QFrame):
    """Angajman kuyruğundaki tek bir hedef satırı — yüksek okunabilirlik."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(34)
        self._status = TARGET_STATUS_IDLE

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(0)

        # Sol kenar renk çubuğu (durum göstergesi)
        self._side_bar = QFrame()
        self._side_bar.setFixedWidth(4)
        self._side_bar.setStyleSheet("background-color: #2A2A2A;")
        layout.addWidget(self._side_bar)

        # İç içerik
        inner = QHBoxLayout()
        inner.setContentsMargins(6, 0, 0, 0)
        inner.setSpacing(6)

        # Sıra numarası (büyük, bold)
        self._order_label = QLabel("--")
        self._order_label.setFixedWidth(20)
        self._order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_label.setStyleSheet(
            "color: #505050; font-size: 13px; font-weight: bold;"
        )
        inner.addWidget(self._order_label)

        # Hedef adı
        self._name_label = QLabel("---")
        self._name_label.setStyleSheet(
            "color: #505050; font-size: 12px;"
        )
        inner.addWidget(self._name_label, stretch=1)

        # Durum etiketi
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._status_label.setFixedWidth(44)
        self._status_label.setStyleSheet(
            "color: #505050; font-size: 9px; font-weight: bold;"
        )
        inner.addWidget(self._status_label)

        layout.addLayout(inner, stretch=1)
        self._apply_idle_style()

    def set_target(self, order: int, name: str, code: str, status: str):
        self._order_label.setText(f"{order}")
        self._name_label.setText(f"{name}")
        self._status = status
        self._apply_status_style(code)

    def clear(self):
        self._order_label.setText("--")
        self._name_label.setText("---")
        self._status_label.setText("")
        self._status = TARGET_STATUS_IDLE
        self._apply_idle_style()

    def _apply_idle_style(self):
        self.setStyleSheet(
            "QFrame { background-color: #1A1A1A; border: 1px solid #252525;"
            " border-radius: 3px; }"
        )
        self._side_bar.setStyleSheet("background-color: #2A2A2A; border-radius: 0px;")
        self._order_label.setStyleSheet("color: #505050; font-size: 13px; font-weight: bold;")
        self._name_label.setStyleSheet("color: #505050; font-size: 12px;")
        self._status_label.setText("")
        self._status_label.setStyleSheet("color: #505050; font-size: 9px; font-weight: bold;")

    def _apply_status_style(self, code: str):
        if self._status == TARGET_STATUS_DESTROYED:
            self.setStyleSheet(
                "QFrame { background-color: #1A1515; border: 1px solid #2A2020;"
                " border-radius: 3px; }"
            )
            self._side_bar.setStyleSheet("background-color: #FF3333; border-radius: 0px;")
            self._order_label.setStyleSheet(
                "color: #553333; font-size: 13px; font-weight: bold;"
                " text-decoration: line-through;"
            )
            self._name_label.setStyleSheet(
                "color: #553333; font-size: 12px; text-decoration: line-through;"
            )
            self._status_label.setText("IMHA")
            self._status_label.setStyleSheet(
                "color: #FF3333; font-size: 9px; font-weight: bold;"
            )

        elif self._status == TARGET_STATUS_ACTIVE:
            self.setStyleSheet(
                "QFrame { background-color: #2A2200; border: 2px solid #FFCC00;"
                " border-radius: 3px; }"
            )
            self._side_bar.setStyleSheet("background-color: #FFCC00; border-radius: 0px;")
            self._order_label.setStyleSheet(
                "color: #FFCC00; font-size: 13px; font-weight: bold;"
            )
            self._name_label.setStyleSheet(
                "color: #FFCC00; font-size: 12px; font-weight: bold;"
            )
            self._status_label.setText("AKTIF")
            self._status_label.setStyleSheet(
                "color: #FFCC00; font-size: 9px; font-weight: bold;"
            )

        elif self._status == TARGET_STATUS_PENDING:
            accent = TARGET_ACCENTS.get(code, "#3399FF")
            self.setStyleSheet(
                "QFrame { background-color: #181820; border: 1px solid #252535;"
                " border-radius: 3px; }"
            )
            self._side_bar.setStyleSheet(f"background-color: {accent}; border-radius: 0px;")
            self._order_label.setStyleSheet(
                f"color: {accent}; font-size: 13px; font-weight: bold;"
            )
            self._name_label.setStyleSheet(
                "color: #8899AA; font-size: 12px;"
            )
            self._status_label.setText("BEKLE")
            self._status_label.setStyleSheet(
                "color: #556677; font-size: 9px; font-weight: bold;"
            )


class _InfoRow(QFrame):
    """Görev bilgisi satırı — etiket : değer."""

    def __init__(self, label: str, value: str, color: str = "#A0A0A0", parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        self.setStyleSheet("QFrame { border: none; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(0)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #606060; font-size: 10px;")
        layout.addWidget(lbl)

        layout.addStretch()

        self._value_label = QLabel(value)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._value_label.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: bold;"
        )
        layout.addWidget(self._value_label)

    def set_value(self, value: str, color: str = None):
        if color:
            self._value_label.setStyleSheet(
                f"color: {color}; font-size: 10px; font-weight: bold;"
            )
        self._value_label.setText(value)


class Stage1LeftPanel(QWidget):
    """
    Aşama 1 — Sol Panel
    Sabit düzen: hedef seçim butonları + angajman kuyruğu +
    görev bilgi paneli. Anlık okunabilirlik için optimize edilmiş.
    """

    MAX_TARGETS = 4

    target_order_changed = Signal(list)

    TARGET_TYPES = ["F-16", "Helikopter", "Mini IHA", "B. Fuze"]
    TARGET_CODES = ["F16", "HEL", "IHA", "BFZ"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_order: list[str] = []
        self._mission_seconds = 0
        self._init_ui()
        self._start_mock_mission_timer()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        # ═══════════════════════════════════════════════════
        #  HEDEF SEÇİM BÖLÜMÜ
        # ═══════════════════════════════════════════════════
        self._title = QLabel("HEDEF SECIM")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 11px; font-weight: bold;"
            "padding: 2px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(self._title)

        # 4 hedef butonu — dikey, her biri benzersiz sol aksan ile
        self._target_buttons: list[QPushButton] = []
        for i, (code, name) in enumerate(zip(self.TARGET_CODES, self.TARGET_TYPES)):
            accent = TARGET_ACCENTS.get(code, "#3399FF")
            btn = QPushButton(f"  {name}")
            btn.setObjectName(f"targetBtn_{code}")
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton#{btn.objectName()} {{"
                f"  background-color: #222233; color: {accent};"
                f"  border: 1px solid #333344; border-left: 4px solid {accent};"
                f"  border-radius: 3px;"
                f"  font-size: 12px; font-weight: bold; padding: 2px 6px;"
                f"  text-align: left;"
                f"}}"
                f"QPushButton#{btn.objectName()}:hover {{"
                f"  background-color: #2A2A44; border: 1px solid {accent};"
                f"  border-left: 4px solid {accent};"
                f"}}"
            )
            btn.clicked.connect(
                lambda checked, idx=i: self._on_target_clicked(idx)
            )
            layout.addWidget(btn)
            self._target_buttons.append(btn)

        layout.addSpacing(2)

        # ═══════════════════════════════════════════════════
        #  ANGAJMAN KUYRUĞU
        # ═══════════════════════════════════════════════════
        queue_header = QLabel("ANGAJMAN KUYRUGU")
        queue_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        queue_header.setStyleSheet(
            "color: #FFCC00; font-size: 10px; font-weight: bold;"
            "padding: 2px; border-top: 1px solid #3A3A3A;"
            "border-bottom: 1px solid #2A2A2A;"
        )
        layout.addWidget(queue_header)

        self._queue_rows: list[_EngagementRow] = []
        for i in range(self.MAX_TARGETS):
            row = _EngagementRow()
            layout.addWidget(row)
            self._queue_rows.append(row)

        layout.addSpacing(2)

        # ═══════════════════════════════════════════════════
        #  GÖREV BİLGİ PANELİ
        # ═══════════════════════════════════════════════════
        info_header = QLabel("GOREV DURUMU")
        info_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_header.setStyleSheet(
            "color: #606060; font-size: 10px; font-weight: bold;"
            "padding: 2px; border-top: 1px solid #3A3A3A;"
        )
        layout.addWidget(info_header)

        self._info_time = _InfoRow("SURE", "00:00", "#A0A0A0")
        layout.addWidget(self._info_time)

        self._info_hit = _InfoRow("ISABET", "-- / --", "#707070")
        layout.addWidget(self._info_hit)

        self._info_nfa = _InfoRow("NFA", "TEMIZ", "#33CC33")
        layout.addWidget(self._info_nfa)

        self._info_sys = _InfoRow("SENSOR", "HAZIR", "#33CC33")
        layout.addWidget(self._info_sys)

        self._info_ammo = _InfoRow("MERMI", "DOLU", "#33CC33")
        layout.addWidget(self._info_ammo)

        # ═══════════════════════════════════════════════════
        #  SIFIRLA (en alt, sabit)
        # ═══════════════════════════════════════════════════
        layout.addStretch(1)

        self._reset_btn = QPushButton("SIFIRLA")
        self._reset_btn.setObjectName("resetBtn")
        self._reset_btn.setFixedHeight(26)
        self._reset_btn.setStyleSheet(
            "QPushButton#resetBtn {"
            "  font-size: 10px; padding: 4px 8px;"
            "  background-color: #222222; color: #606060;"
            "  border: 1px solid #333333; border-radius: 3px;"
            "}"
            "QPushButton#resetBtn:hover {"
            "  background-color: #2A2A2A; color: #A0A0A0;"
            "  border: 1px solid #555555;"
            "}"
        )
        self._reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self._reset_btn)

    # ── Görev sayacı ───────────────────────────────────────
    def _start_mock_mission_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self):
        self._mission_seconds += 1
        m, s = divmod(self._mission_seconds, 60)
        self._info_time.set_value(f"{m:02d}:{s:02d}", "#A0A0A0")

    # ── Hedef seçim mantığı ────────────────────────────────
    def _on_target_clicked(self, idx: int):
        if len(self._target_order) >= self.MAX_TARGETS:
            return

        name = self.TARGET_TYPES[idx]
        code = self.TARGET_CODES[idx]
        self._target_order.append(name)

        # Butonu soluk/devre dışı yap
        btn = self._target_buttons[idx]
        btn.setStyleSheet(
            f"QPushButton#{btn.objectName()} {{"
            f"  background-color: #1A1A1A; color: #404040;"
            f"  border: 1px solid #252525; border-left: 4px solid #333333;"
            f"  border-radius: 3px;"
            f"  font-size: 12px; padding: 2px 6px;"
            f"  text-align: left;"
            f"}}"
        )
        btn.setEnabled(False)

        self._update_queue()
        self.target_order_changed.emit(self._target_order.copy())

        if len(self._target_order) >= self.MAX_TARGETS:
            self._finalize_selection()

    def _finalize_selection(self):
        for btn in self._target_buttons:
            if btn.isEnabled():
                btn.setStyleSheet(
                    f"QPushButton#{btn.objectName()} {{"
                    f"  background-color: #1A1A1A; color: #404040;"
                    f"  border: 1px solid #252525; border-left: 4px solid #333333;"
                    f"  border-radius: 3px;"
                    f"  font-size: 12px; padding: 2px 6px;"
                    f"  text-align: left;"
                    f"}}"
                )
                btn.setEnabled(False)

        self._title.setText("ANGAJMAN AKTIF")
        self._title.setStyleSheet(
            "color: #FFCC00; font-size: 11px; font-weight: bold;"
            "padding: 2px; border-bottom: 1px solid #FFCC00;"
        )

        # Mock: ilk 2 IMHA, 3. AKTIF, 4. BEKLE
        self._apply_mock_statuses()

    def _update_queue(self):
        for i in range(self.MAX_TARGETS):
            if i < len(self._target_order):
                name = self._target_order[i]
                code = self.TARGET_CODES[self.TARGET_TYPES.index(name)]
                self._queue_rows[i].set_target(i + 1, name, code, TARGET_STATUS_PENDING)
            else:
                self._queue_rows[i].clear()

    def _apply_mock_statuses(self):
        for i in range(self.MAX_TARGETS):
            if i < len(self._target_order):
                name = self._target_order[i]
                code = self.TARGET_CODES[self.TARGET_TYPES.index(name)]
                if i < 2:
                    status = TARGET_STATUS_DESTROYED
                elif i == 2:
                    status = TARGET_STATUS_ACTIVE
                else:
                    status = TARGET_STATUS_PENDING
                self._queue_rows[i].set_target(i + 1, name, code, status)
        self._info_hit.set_value("2 / 4", "#FFCC00")

    def _on_reset(self):
        self._target_order.clear()
        self._mission_seconds = 0

        for i, btn in enumerate(self._target_buttons):
            code = self.TARGET_CODES[i]
            name = self.TARGET_TYPES[i]
            accent = TARGET_ACCENTS.get(code, "#3399FF")
            btn.setStyleSheet(
                f"QPushButton#{btn.objectName()} {{"
                f"  background-color: #222233; color: {accent};"
                f"  border: 1px solid #333344; border-left: 4px solid {accent};"
                f"  border-radius: 3px;"
                f"  font-size: 12px; font-weight: bold; padding: 2px 6px;"
                f"  text-align: left;"
                f"}}"
                f"QPushButton#{btn.objectName()}:hover {{"
                f"  background-color: #2A2A44; border: 1px solid {accent};"
                f"  border-left: 4px solid {accent};"
                f"}}"
            )
            btn.setEnabled(True)

        for row in self._queue_rows:
            row.clear()

        self._title.setText("HEDEF SECIM")
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 11px; font-weight: bold;"
            "padding: 2px; border-bottom: 1px solid #3A3A3A;"
        )

        self._info_time.set_value("00:00", "#A0A0A0")
        self._info_hit.set_value("-- / --", "#707070")
        self._info_nfa.set_value("TEMIZ", "#33CC33")
        self._info_sys.set_value("HAZIR", "#33CC33")
        self._info_ammo.set_value("DOLU", "#33CC33")

        self.target_order_changed.emit([])

    def get_target_order(self) -> list[str]:
        return self._target_order.copy()


class Stage1RightPanel(QWidget):
    """
    Aşama 1 — Sağ Panel
    Taret yönlendirme ok tuşları ve MIL-STD uyumlu iki aşamalı
    ateşleme mekanizması (ARM / ATES).
    """

    turret_command = Signal(str)
    fire_command = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_armed = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("TARET KONTROLU")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #3399FF; font-size: 14px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(title)

        arrow_frame = QFrame()
        arrow_layout = QGridLayout(arrow_frame)
        arrow_layout.setSpacing(4)

        btn_up = QPushButton("▲")
        btn_up.setObjectName("arrowBtn")
        btn_up.clicked.connect(lambda: self._on_direction("UP"))
        arrow_layout.addWidget(btn_up, 0, 1)

        btn_left = QPushButton("◀")
        btn_left.setObjectName("arrowBtn")
        btn_left.clicked.connect(lambda: self._on_direction("LEFT"))
        arrow_layout.addWidget(btn_left, 1, 0)

        center_label = QLabel("+")
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_label.setStyleSheet("color: #707070; font-size: 22px; font-weight: bold;")
        arrow_layout.addWidget(center_label, 1, 1)

        btn_right = QPushButton("▶")
        btn_right.setObjectName("arrowBtn")
        btn_right.clicked.connect(lambda: self._on_direction("RIGHT"))
        arrow_layout.addWidget(btn_right, 1, 2)

        btn_down = QPushButton("▼")
        btn_down.setObjectName("arrowBtn")
        btn_down.clicked.connect(lambda: self._on_direction("DOWN"))
        arrow_layout.addWidget(btn_down, 2, 1)

        layout.addWidget(arrow_frame)
        layout.addSpacing(12)

        fire_title = QLabel("ATESLEME SISTEMI")
        fire_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fire_title.setStyleSheet(
            "color: #FFCC00; font-size: 13px; font-weight: bold; "
            "padding: 4px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(fire_title)

        self._arm_btn = QPushButton("[SAFE]  ARM")
        self._arm_btn.setObjectName("armBtn")
        self._arm_btn.clicked.connect(self._on_arm)
        layout.addWidget(self._arm_btn)

        self._fire_btn = QPushButton(">>> ATES <<<")
        self._fire_btn.setObjectName("fireBtn")
        self._fire_btn.setEnabled(False)
        self._fire_btn.clicked.connect(self._on_fire)
        layout.addWidget(self._fire_btn)

        self._status_label = QLabel("DURUM: GUVENLI")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(
            "color: #33CC33; font-size: 13px; font-weight: bold; padding: 6px;"
        )
        layout.addWidget(self._status_label)

        layout.addStretch()

    def _on_direction(self, direction: str):
        self.turret_command.emit(direction)

    def _on_arm(self):
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
        self.fire_command.emit()
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
