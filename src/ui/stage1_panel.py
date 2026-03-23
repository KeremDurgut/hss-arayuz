"""
Çelikkubbe HMI — Aşama 1: Manuel Angajman Paneli
==================================================
Sol Panel : Hedef angajman seçimi + angajman kuyruğu + görev bilgisi
Sağ Panel : Taret yönlendirme ok tuşları + ARM/ATEŞ mekanizması

Tasarım Felsefesi (MIL-STD-1472H):
  - Sabit düzen: hiçbir widget gizlenmez veya yer değiştirmez
  - Duruma göre renk kodları: IMHA=kırmızı üstü çizili, AKTIF=amber,
    BEKLEMEDE=mavi soluk
  - Alt alanda görev bilgisi: süre, isabet, NFA, sistem hazırlığı
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


# ── Hedef Durumları ────────────────────────────────────────────────
TARGET_STATUS_IDLE = "IDLE"           # Henüz seçilmedi
TARGET_STATUS_DESTROYED = "DESTROYED" # İmha edildi
TARGET_STATUS_ACTIVE = "ACTIVE"       # Şu an hedeflenen
TARGET_STATUS_PENDING = "PENDING"     # Sırada bekleyen


class _EngagementRow(QFrame):
    """Angajman kuyruğundaki tek bir hedef satırı."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self._status = TARGET_STATUS_IDLE

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        # Sıra numarası
        self._order_label = QLabel("--")
        self._order_label.setFixedWidth(22)
        self._order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_label.setStyleSheet(
            "color: #707070; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(self._order_label)

        # Durum göstergesi (küçük kare)
        self._indicator = QLabel()
        self._indicator.setFixedSize(8, 8)
        self._indicator.setStyleSheet(
            "background-color: #3A3A3A; border-radius: 4px;"
        )
        layout.addWidget(self._indicator)

        # Hedef adı
        self._name_label = QLabel("---")
        self._name_label.setStyleSheet(
            "color: #707070; font-size: 11px;"
        )
        layout.addWidget(self._name_label, stretch=1)

        # Durum metni
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._status_label.setStyleSheet(
            "color: #707070; font-size: 10px;"
        )
        layout.addWidget(self._status_label)

        self._apply_idle_style()

    def set_target(self, order: int, name: str, code: str, status: str):
        """Satırı hedef bilgisiyle doldur."""
        self._order_label.setText(f"{order}")
        self._name_label.setText(f"[{code}] {name}")
        self._status = status
        self._apply_status_style()

    def clear(self):
        """Satırı boş duruma döndür."""
        self._order_label.setText("--")
        self._name_label.setText("---")
        self._status_label.setText("")
        self._status = TARGET_STATUS_IDLE
        self._apply_idle_style()

    def _apply_idle_style(self):
        self.setStyleSheet(
            "QFrame { background-color: #1E1E1E; border: 1px solid #2A2A2A;"
            " border-radius: 3px; }"
        )
        self._order_label.setStyleSheet("color: #707070; font-size: 11px; font-weight: bold;")
        self._name_label.setStyleSheet("color: #707070; font-size: 11px;")
        self._indicator.setStyleSheet("background-color: #3A3A3A; border-radius: 4px;")
        self._status_label.setText("")

    def _apply_status_style(self):
        if self._status == TARGET_STATUS_DESTROYED:
            self.setStyleSheet(
                "QFrame { background-color: #1A1A1A; border: 1px solid #3A2020;"
                " border-radius: 3px; }"
            )
            self._order_label.setStyleSheet(
                "color: #663333; font-size: 11px; font-weight: bold;"
                " text-decoration: line-through;"
            )
            self._name_label.setStyleSheet(
                "color: #663333; font-size: 11px; text-decoration: line-through;"
            )
            self._indicator.setStyleSheet(
                "background-color: #FF3333; border-radius: 4px;"
            )
            self._status_label.setText("IMHA")
            self._status_label.setStyleSheet(
                "color: #FF3333; font-size: 10px; font-weight: bold;"
            )

        elif self._status == TARGET_STATUS_ACTIVE:
            self.setStyleSheet(
                "QFrame { background-color: #2A2200; border: 2px solid #FFCC00;"
                " border-radius: 3px; }"
            )
            self._order_label.setStyleSheet(
                "color: #FFCC00; font-size: 11px; font-weight: bold;"
            )
            self._name_label.setStyleSheet(
                "color: #FFCC00; font-size: 11px; font-weight: bold;"
            )
            self._indicator.setStyleSheet(
                "background-color: #FFCC00; border-radius: 4px;"
            )
            self._status_label.setText("AKTIF")
            self._status_label.setStyleSheet(
                "color: #FFCC00; font-size: 10px; font-weight: bold;"
            )

        elif self._status == TARGET_STATUS_PENDING:
            self.setStyleSheet(
                "QFrame { background-color: #1A1A2A; border: 1px solid #2A2A4A;"
                " border-radius: 3px; }"
            )
            self._order_label.setStyleSheet(
                "color: #3399FF; font-size: 11px; font-weight: bold;"
            )
            self._name_label.setStyleSheet(
                "color: #6699CC; font-size: 11px;"
            )
            self._indicator.setStyleSheet(
                "background-color: #3399FF; border-radius: 4px;"
            )
            self._status_label.setText("BEKLE")
            self._status_label.setStyleSheet(
                "color: #3399FF; font-size: 10px;"
            )


class _InfoRow(QFrame):
    """Görev bilgisi satırı (etiket + değer)."""

    def __init__(self, label: str, value: str, color: str = "#A0A0A0", parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setStyleSheet("QFrame { border: none; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: #707070; font-size: 10px;")
        layout.addWidget(lbl)

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
    Sabit düzen: Hedef seçim butonları + angajman kuyruğu +
    görev bilgi paneli. Hiçbir şey gizlenmez, her şey yerinde.
    """

    MAX_TARGETS = 4

    target_order_changed = Signal(list)

    TARGET_TYPES = ["F-16", "Helikopter", "Mini IHA", "B. Fuze"]
    TARGET_CODES = ["F16", "HEL", "IHA", "BFZ"]

    # Buton stili
    _STYLE_IDLE = (
        "QPushButton#targetBtn {"
        "  background-color: #2A2A4A; color: #3399FF;"
        "  border: 2px solid #3399FF; border-radius: 4px;"
        "  font-size: 11px; font-weight: bold; padding: 3px 6px;"
        "  text-align: left;"
        "}"
        "QPushButton#targetBtn:hover {"
        "  background-color: #33336B; border: 2px solid #66BBFF;"
        "}"
    )
    _STYLE_DISABLED = (
        "QPushButton#targetBtn {"
        "  background-color: #1E1E1E; color: #505050;"
        "  border: 1px solid #2A2A2A; border-radius: 4px;"
        "  font-size: 11px; padding: 3px 6px;"
        "  text-align: left;"
        "}"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_order: list[str] = []
        self._mission_seconds = 0
        self._init_ui()
        self._start_mock_mission_timer()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)

        # ── BAŞLIK ─────────────────────────────────────────
        self._title = QLabel("HEDEF SECIM")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 11px; font-weight: bold;"
            "padding: 3px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(self._title)

        # ── HEDEF BUTONLARI (2x2 grid, kompakt) ───────────
        grid = QGridLayout()
        grid.setSpacing(3)
        self._target_buttons: list[QPushButton] = []
        for i, (code, name) in enumerate(zip(self.TARGET_CODES, self.TARGET_TYPES)):
            btn = QPushButton(f"[{code}] {name}")
            btn.setObjectName("targetBtn")
            btn.setFixedHeight(30)
            btn.setStyleSheet(self._STYLE_IDLE)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, idx=i: self._on_target_clicked(idx)
            )
            grid.addWidget(btn, i // 2, i % 2)
            self._target_buttons.append(btn)
        layout.addLayout(grid)

        # ── ARA ÇIZGI ─────────────────────────────────────
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #3A3A3A;")
        sep1.setFixedHeight(1)
        layout.addWidget(sep1)

        # ── ANGAJMAN KUYRUĞU BAŞLIĞI ──────────────────────
        queue_header = QLabel("ANGAJMAN KUYRUGU")
        queue_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        queue_header.setStyleSheet(
            "color: #FFCC00; font-size: 10px; font-weight: bold; padding: 2px;"
        )
        layout.addWidget(queue_header)

        # ── ANGAJMAN KUYRUK SATIRLARI (4 adet, sabit) ─────
        self._queue_rows: list[_EngagementRow] = []
        for i in range(self.MAX_TARGETS):
            row = _EngagementRow()
            layout.addWidget(row)
            self._queue_rows.append(row)

        # ── ARA ÇIZGI ─────────────────────────────────────
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #3A3A3A;")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)

        # ── GÖREV BİLGİ PANELİ ────────────────────────────
        info_header = QLabel("GOREV BILGISI")
        info_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_header.setStyleSheet(
            "color: #707070; font-size: 10px; font-weight: bold; padding: 2px;"
        )
        layout.addWidget(info_header)

        self._info_time = _InfoRow("GOREV SURESI", "00:00", "#A0A0A0")
        layout.addWidget(self._info_time)

        self._info_hit = _InfoRow("ISABET", "0 / 0", "#A0A0A0")
        layout.addWidget(self._info_hit)

        self._info_nfa = _InfoRow("NFA DURUMU", "TEMIZ", "#33CC33")
        layout.addWidget(self._info_nfa)

        self._info_sys = _InfoRow("SENSOR", "HAZIR", "#33CC33")
        layout.addWidget(self._info_sys)

        self._info_ammo = _InfoRow("MERMI", "DOLU", "#33CC33")
        layout.addWidget(self._info_ammo)

        # ── Boşluk doldurucu ──────────────────────────────
        layout.addStretch(1)

        # ── SIFIRLA butonu (en alt) ───────────────────────
        self._reset_btn = QPushButton("SIFIRLA")
        self._reset_btn.setObjectName("resetBtn")
        self._reset_btn.setFixedHeight(24)
        self._reset_btn.setStyleSheet(
            "QPushButton#resetBtn {"
            "  font-size: 10px; padding: 2px 8px;"
            "  background-color: #2A2A2A; color: #707070;"
            "  border: 1px solid #3A3A3A; border-radius: 3px;"
            "}"
            "QPushButton#resetBtn:hover {"
            "  background-color: #3A3A3A; color: #A0A0A0;"
            "}"
        )
        self._reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self._reset_btn)

    # ── Görev süresi sayacı (mock) ─────────────────────────
    def _start_mock_mission_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_mission_time)
        self._timer.start(1000)

    def _tick_mission_time(self):
        self._mission_seconds += 1
        mins = self._mission_seconds // 60
        secs = self._mission_seconds % 60
        self._info_time.set_value(f"{mins:02d}:{secs:02d}", "#A0A0A0")

    # ── Hedef seçim mantığı ────────────────────────────────
    def _on_target_clicked(self, btn_index: int):
        if len(self._target_order) >= self.MAX_TARGETS:
            return

        target_name = self.TARGET_TYPES[btn_index]
        target_code = self.TARGET_CODES[btn_index]
        self._target_order.append(target_name)

        # Butonu devre dışı bırak
        btn = self._target_buttons[btn_index]
        btn.setStyleSheet(self._STYLE_DISABLED)
        btn.setEnabled(False)

        # Kuyruğu güncelle
        self._update_queue()
        self.target_order_changed.emit(self._target_order.copy())

        # 4 hedef tamamlandıysa
        if len(self._target_order) >= self.MAX_TARGETS:
            self._finalize_selection()

    def _finalize_selection(self):
        """Tüm butonları kilitle, başlığı güncelle, mock durumları uygula."""
        for btn in self._target_buttons:
            if btn.isEnabled():
                btn.setStyleSheet(self._STYLE_DISABLED)
                btn.setEnabled(False)

        self._title.setText("ANGAJMAN AKTIF")
        self._title.setStyleSheet(
            "color: #FFCC00; font-size: 11px; font-weight: bold;"
            "padding: 3px; border-bottom: 1px solid #FFCC00;"
        )

        # Mock: ilk 2 hedef IMHA, 3. AKTIF, 4. BEKLEMEDE
        self._apply_mock_statuses()

    def _update_queue(self):
        """Kuyruk satırlarını mevcut seçime göre güncelle."""
        for i in range(self.MAX_TARGETS):
            if i < len(self._target_order):
                name = self._target_order[i]
                code = self.TARGET_CODES[self.TARGET_TYPES.index(name)]
                # Seçim aşamasında hepsi PENDING
                self._queue_rows[i].set_target(i + 1, name, code, TARGET_STATUS_PENDING)
            else:
                self._queue_rows[i].clear()

    def _apply_mock_statuses(self):
        """Mock: ilk 2 hedef IMHA, 3. AKTIF, son BEKLEMEDE."""
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

        # İsabet bilgisini güncelle
        self._info_hit.set_value("2 / 4", "#FFCC00")

    def _on_reset(self):
        """Tüm seçimi sıfırla."""
        self._target_order.clear()
        self._mission_seconds = 0

        for btn in self._target_buttons:
            btn.setStyleSheet(self._STYLE_IDLE)
            btn.setEnabled(True)

        for row in self._queue_rows:
            row.clear()

        self._title.setText("HEDEF SECIM")
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 11px; font-weight: bold;"
            "padding: 3px; border-bottom: 1px solid #3A3A3A;"
        )

        self._info_time.set_value("00:00", "#A0A0A0")
        self._info_hit.set_value("0 / 0", "#A0A0A0")
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

        # ATEŞ butonu
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
