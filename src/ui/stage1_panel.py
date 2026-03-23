"""
Celikkubbe HMI -- Asama 1: Manuel Angajman Paneli
Sol Panel : Hedef angajman secimi + angajman kuyrugu + gorev bilgisi
Sag Panel : Taret yonlendirme ok tuslari + ARM/ATES mekanizmasi

MIL-STD-2525D renk kodlari, MIL-STD-1472H ergonomi standartlari.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

C_HOSTILE = "#FF3333"
C_SUSPECT = "#FFCC00"
C_FRIENDLY = "#3399FF"
C_NEUTRAL = "#33CC33"
C_DIM = "#505050"
C_BG = "#1A1A1A"

TARGET_STATUS_IDLE = "IDLE"
TARGET_STATUS_DESTROYED = "DESTROYED"
TARGET_STATUS_ACTIVE = "ACTIVE"
TARGET_STATUS_PENDING = "PENDING"

ROW_H = 58
ROW_H_ACTIVE = 64


class _EngagementRow(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(ROW_H)
        self._status = TARGET_STATUS_IDLE

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 2, 0)
        layout.setSpacing(0)

        self._side_bar = QFrame()
        self._side_bar.setFixedWidth(5)
        self._side_bar.setStyleSheet("background-color: #252525;")
        layout.addWidget(self._side_bar)

        inner = QHBoxLayout()
        inner.setContentsMargins(4, 0, 2, 0)
        inner.setSpacing(3)

        self._order_label = QLabel("--")
        self._order_label.setFixedWidth(20)
        self._order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_label.setStyleSheet(
            "color: #404040; font-size: 22px; font-weight: bold;"
        )
        inner.addWidget(self._order_label)

        self._name_label = QLabel("---")
        self._name_label.setStyleSheet("color: #404040; font-size: 22px;")
        inner.addWidget(self._name_label, stretch=1)

        self._status_label = QLabel("")
        self._status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self._status_label.setStyleSheet(
            "color: #404040; font-size: 14px; font-weight: bold;"
        )
        inner.addWidget(self._status_label)

        layout.addLayout(inner, stretch=1)
        self._apply_idle_style()

    def set_target(self, order, name, code, status):
        self._order_label.setText(str(order))
        self._name_label.setText(name)
        self._status = status
        self._apply_status_style()

    def clear(self):
        self._order_label.setText("--")
        self._name_label.setText("---")
        self._status_label.setText("")
        self._status = TARGET_STATUS_IDLE
        self.setFixedHeight(ROW_H)
        self._apply_idle_style()

    def _apply_idle_style(self):
        self.setStyleSheet(
            "QFrame { background-color: " + C_BG + "; border: none; }"
        )
        self._side_bar.setStyleSheet("background-color: #252525;")
        self._order_label.setStyleSheet(
            "color: #404040; font-size: 22px; font-weight: bold;"
        )
        self._name_label.setStyleSheet("color: #404040; font-size: 22px;")
        self._status_label.setText("")
        self._status_label.setStyleSheet(
            "color: #404040; font-size: 14px; font-weight: bold;"
        )

    def _apply_status_style(self):
        if self._status == TARGET_STATUS_DESTROYED:
            self.setFixedHeight(ROW_H)
            self.setStyleSheet(
                "QFrame { background-color: #1C1616; border: none; }"
            )
            self._side_bar.setStyleSheet(
                "background-color: " + C_HOSTILE + ";"
            )
            self._order_label.setStyleSheet(
                "color: #5A3030; font-size: 22px; font-weight: bold;"
                " text-decoration: line-through;"
            )
            self._name_label.setStyleSheet(
                "color: #5A3030; font-size: 22px;"
                " text-decoration: line-through;"
            )
            self._status_label.setText("IMHA")
            self._status_label.setStyleSheet(
                "color: " + C_HOSTILE + ";"
                " font-size: 14px; font-weight: bold;"
            )

        elif self._status == TARGET_STATUS_ACTIVE:
            self.setFixedHeight(ROW_H_ACTIVE)
            self.setStyleSheet(
                "QFrame { background-color: #242000; border: none; }"
            )
            self._side_bar.setStyleSheet(
                "background-color: " + C_SUSPECT + ";"
            )
            self._order_label.setStyleSheet(
                "color: " + C_SUSPECT + ";"
                " font-size: 24px; font-weight: bold;"
            )
            self._name_label.setStyleSheet(
                "color: " + C_SUSPECT + ";"
                " font-size: 24px; font-weight: bold;"
            )
            self._status_label.setText("AKTIF")
            self._status_label.setStyleSheet(
                "color: " + C_SUSPECT + ";"
                " font-size: 14px; font-weight: bold;"
            )

        elif self._status == TARGET_STATUS_PENDING:
            self.setFixedHeight(ROW_H)
            self.setStyleSheet(
                "QFrame { background-color: #181820; border: none; }"
            )
            self._side_bar.setStyleSheet(
                "background-color: " + C_FRIENDLY + ";"
            )
            self._order_label.setStyleSheet(
                "color: " + C_FRIENDLY + ";"
                " font-size: 22px; font-weight: bold;"
            )
            self._name_label.setStyleSheet(
                "color: #7799BB; font-size: 22px;"
            )
            self._status_label.setText("BEKLE")
            self._status_label.setStyleSheet(
                "color: #556677; font-size: 14px; font-weight: bold;"
            )


class _InfoRow(QFrame):

    def __init__(self, label, value, color="#A0A0A0", parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setStyleSheet("QFrame { border: none; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(0)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #606060; font-size: 20px;")
        layout.addWidget(lbl)

        layout.addStretch()

        self._value_label = QLabel(value)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._value_label.setStyleSheet(
            "color: " + color + "; font-size: 20px; font-weight: bold;"
        )
        layout.addWidget(self._value_label)

    def set_value(self, value, color=None):
        if color:
            self._value_label.setStyleSheet(
                "color: " + color + ";"
                " font-size: 20px; font-weight: bold;"
            )
        self._value_label.setText(value)


class Stage1LeftPanel(QWidget):

    MAX_TARGETS = 4
    target_order_changed = Signal(list)

    TARGET_TYPES = ["F-16", "Helikopter", "İHA", "Füze"]
    TARGET_CODES = ["F16", "HEL", "IHA", "FUZE"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_order = []
        self._mission_seconds = 0
        self._init_ui()
        self._start_mock_mission_timer()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._title = QLabel("HEDEF SECIM")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            "color: " + C_FRIENDLY + ";"
            " font-size: 20px; font-weight: bold;"
            " padding: 3px; border-bottom: 1px solid #333333;"
        )
        layout.addWidget(self._title)

        grid = QGridLayout()
        grid.setSpacing(3)
        self._target_buttons = []
        for i in range(self.MAX_TARGETS):
            code = self.TARGET_CODES[i]
            name = self.TARGET_TYPES[i]
            btn = QPushButton(name)
            btn.setObjectName("tgt_" + code)
            btn.setFixedHeight(52)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._apply_btn_idle(btn)
            btn.clicked.connect(
                lambda checked, idx=i: self._on_target_clicked(idx)
            )
            grid.addWidget(btn, i // 2, i % 2)
            self._target_buttons.append(btn)
        layout.addLayout(grid)

        queue_lbl = QLabel("ANGAJMAN KUYRUGU")
        queue_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        queue_lbl.setStyleSheet(
            "color: " + C_SUSPECT + ";"
            " font-size: 18px; font-weight: bold;"
            " padding: 3px; margin-top: 2px;"
            " border-top: 1px solid #333333;"
        )
        layout.addWidget(queue_lbl)

        self._queue_rows = []
        for _ in range(self.MAX_TARGETS):
            row = _EngagementRow()
            layout.addWidget(row)
            self._queue_rows.append(row)

        info_lbl = QLabel("GOREV DURUMU")
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_lbl.setStyleSheet(
            "color: #505050; font-size: 18px; font-weight: bold;"
            " padding: 3px; margin-top: 2px;"
            " border-top: 1px solid #333333;"
        )
        layout.addWidget(info_lbl)

        self._info_time = _InfoRow("SURE", "00:00", "#A0A0A0")
        layout.addWidget(self._info_time)
        self._info_hit = _InfoRow("ISABET", "-- / --", "#707070")
        layout.addWidget(self._info_hit)
        self._info_nfa = _InfoRow("NFA", "TEMIZ", C_NEUTRAL)
        layout.addWidget(self._info_nfa)
        self._info_sys = _InfoRow("SENSOR", "HAZIR", C_NEUTRAL)
        layout.addWidget(self._info_sys)
        self._info_ammo = _InfoRow("MERMI", "DOLU", C_NEUTRAL)
        layout.addWidget(self._info_ammo)

        layout.addStretch(1)

        self._reset_btn = QPushButton("SIFIRLA")
        self._reset_btn.setObjectName("resetBtn")
        self._reset_btn.setFixedHeight(42)
        self._reset_btn.setStyleSheet(
            "QPushButton#resetBtn {"
            "  font-size: 20px; padding: 4px 8px;"
            "  background-color: #1E1E1E; color: #606060;"
            "  border: 1px solid #333333; border-radius: 3px;"
            "}"
            "QPushButton#resetBtn:hover {"
            "  background-color: #2A2A2A; color: #A0A0A0;"
            "  border: 1px solid #555555;"
            "}"
        )
        self._reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self._reset_btn)

    @staticmethod
    def _apply_btn_idle(btn):
        obj = btn.objectName()
        btn.setStyleSheet(
            "QPushButton#" + obj + " {"
            "  background-color: #1E2233; color: " + C_FRIENDLY + ";"
            "  border: 1px solid #2A3355; border-radius: 3px;"
            "  font-size: 22px; font-weight: bold; padding: 2px 4px;"
            "}"
            "QPushButton#" + obj + ":hover {"
            "  background-color: #253060;"
            "  border: 1px solid " + C_FRIENDLY + ";"
            "}"
        )

    @staticmethod
    def _apply_btn_used(btn):
        obj = btn.objectName()
        btn.setStyleSheet(
            "QPushButton#" + obj + " {"
            "  background-color: #1A1A1A; color: #404040;"
            "  border: 1px solid #252525; border-radius: 3px;"
            "  font-size: 22px; padding: 2px 4px;"
            "}"
        )
        btn.setEnabled(False)

    def _start_mock_mission_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self):
        self._mission_seconds += 1
        m = self._mission_seconds // 60
        s = self._mission_seconds % 60
        self._info_time.set_value(
            str(m).zfill(2) + ":" + str(s).zfill(2)
        )

    def _on_target_clicked(self, idx):
        if len(self._target_order) >= self.MAX_TARGETS:
            return
        self._target_order.append(self.TARGET_TYPES[idx])
        self._apply_btn_used(self._target_buttons[idx])
        self._update_queue()
        self.target_order_changed.emit(list(self._target_order))
        if len(self._target_order) >= self.MAX_TARGETS:
            self._finalize()

    def _finalize(self):
        for btn in self._target_buttons:
            if btn.isEnabled():
                self._apply_btn_used(btn)
        self._title.setText("ANGAJMAN AKTIF")
        self._title.setStyleSheet(
            "color: " + C_SUSPECT + ";"
            " font-size: 22px; font-weight: bold;"
            " padding: 4px;"
            " border-bottom: 1px solid " + C_SUSPECT + ";"
        )
        self._apply_mock_statuses()

    def _update_queue(self):
        for i in range(self.MAX_TARGETS):
            if i < len(self._target_order):
                name = self._target_order[i]
                code = self.TARGET_CODES[self.TARGET_TYPES.index(name)]
                self._queue_rows[i].set_target(
                    i + 1, name, code, TARGET_STATUS_PENDING
                )
            else:
                self._queue_rows[i].clear()

    def _apply_mock_statuses(self):
        for i in range(len(self._target_order)):
            name = self._target_order[i]
            code = self.TARGET_CODES[self.TARGET_TYPES.index(name)]
            if i < 2:
                st = TARGET_STATUS_DESTROYED
            elif i == 2:
                st = TARGET_STATUS_ACTIVE
            else:
                st = TARGET_STATUS_PENDING
            self._queue_rows[i].set_target(i + 1, name, code, st)
        self._info_hit.set_value("2 / 4", C_SUSPECT)

    def _on_reset(self):
        self._target_order = []
        self._mission_seconds = 0
        for i, btn in enumerate(self._target_buttons):
            self._apply_btn_idle(btn)
            btn.setEnabled(True)
        for row in self._queue_rows:
            row.clear()
        self._title.setText("HEDEF SECIM")
        self._title.setStyleSheet(
            "color: " + C_FRIENDLY + ";"
            " font-size: 22px; font-weight: bold;"
            " padding: 4px; border-bottom: 1px solid #333333;"
        )
        self._info_time.set_value("00:00", "#A0A0A0")
        self._info_hit.set_value("-- / --", "#707070")
        self._info_nfa.set_value("TEMIZ", C_NEUTRAL)
        self._info_sys.set_value("HAZIR", C_NEUTRAL)
        self._info_ammo.set_value("DOLU", C_NEUTRAL)
        self.target_order_changed.emit([])

    def get_target_order(self):
        return list(self._target_order)


class Stage1RightPanel(QWidget):

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
            "color: " + C_FRIENDLY + ";"
            " font-size: 14px; font-weight: bold;"
            " padding: 4px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(title)

        arrow_frame = QFrame()
        al = QGridLayout(arrow_frame)
        al.setSpacing(4)

        btn_up = QPushButton("^")
        btn_up.setObjectName("arrowBtn")
        btn_up.clicked.connect(lambda: self._on_direction("UP"))
        al.addWidget(btn_up, 0, 1)

        btn_left = QPushButton("<")
        btn_left.setObjectName("arrowBtn")
        btn_left.clicked.connect(lambda: self._on_direction("LEFT"))
        al.addWidget(btn_left, 1, 0)

        center = QLabel("+")
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.setStyleSheet(
            "color: #505050; font-size: 22px; font-weight: bold;"
        )
        al.addWidget(center, 1, 1)

        btn_right = QPushButton(">")
        btn_right.setObjectName("arrowBtn")
        btn_right.clicked.connect(lambda: self._on_direction("RIGHT"))
        al.addWidget(btn_right, 1, 2)

        btn_down = QPushButton("v")
        btn_down.setObjectName("arrowBtn")
        btn_down.clicked.connect(lambda: self._on_direction("DOWN"))
        al.addWidget(btn_down, 2, 1)

        layout.addWidget(arrow_frame)
        layout.addSpacing(12)

        fire_title = QLabel("ATESLEME SISTEMI")
        fire_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fire_title.setStyleSheet(
            "color: " + C_SUSPECT + ";"
            " font-size: 13px; font-weight: bold;"
            " padding: 4px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(fire_title)

        self._arm_btn = QPushButton("ATIŞ İZNİ")
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
            "color: " + C_NEUTRAL + ";"
            " font-size: 13px; font-weight: bold; padding: 6px;"
        )
        layout.addWidget(self._status_label)
        layout.addStretch()

    def _on_direction(self, d):
        self.turret_command.emit(d)

    def _on_arm(self):
        self._is_armed = not self._is_armed
        if self._is_armed:
            self._arm_btn.setText("ATIŞ İZNİ VERİLDİ")
            self._arm_btn.setProperty("armed", True)
            self._arm_btn.style().unpolish(self._arm_btn)
            self._arm_btn.style().polish(self._arm_btn)
            self._fire_btn.setEnabled(True)
            self._status_label.setText("DURUM: HAZIR")
            self._status_label.setStyleSheet(
                "color: " + C_SUSPECT + ";"
                " font-size: 13px; font-weight: bold; padding: 6px;"
            )
        else:
            self._arm_btn.setText("ATIŞ İZNİ")
            self._arm_btn.setProperty("armed", False)
            self._arm_btn.style().unpolish(self._arm_btn)
            self._arm_btn.style().polish(self._arm_btn)
            self._fire_btn.setEnabled(False)
            self._status_label.setText("DURUM: GUVENLI")
            self._status_label.setStyleSheet(
                "color: " + C_NEUTRAL + ";"
                " font-size: 13px; font-weight: bold; padding: 6px;"
            )

    def _on_fire(self):
        self.fire_command.emit()
        self._is_armed = False
        self._arm_btn.setText("ATIŞ İZNİ")
        self._arm_btn.setProperty("armed", False)
        self._arm_btn.style().unpolish(self._arm_btn)
        self._arm_btn.style().polish(self._arm_btn)
        self._fire_btn.setEnabled(False)
        self._status_label.setText("DURUM: ATES EDILDI")
        self._status_label.setStyleSheet(
            "color: " + C_HOSTILE + ";"
            " font-size: 13px; font-weight: bold; padding: 6px;"
        )
