"""
Çelikkubbe HMI — Aşama 1: Manuel Angajman Paneli
==================================================
Sol Panel : Kompakt hedef angajman seçimi + bilgi gösterimi
Sağ Panel : Taret yönlendirme ok tuşları + ARM/ATEŞ mekanizması
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class Stage1LeftPanel(QWidget):
    """
    Aşama 1 — Sol Panel
    Dikey tek sütun hedef butonları ile dar profilli hızlı seçim.
    4 hedef girildikten sonra seçim alanı gizlenir, kompakt bilgi
    paneli gösterilir. Sıfırla ile tekrar seçime açılır.
    """

    MAX_TARGETS = 4

    # Hedef sırası değiştiğinde yayımlanır: list[str]
    target_order_changed = Signal(list)

    TARGET_TYPES = ["F-16", "Helikopter", "Mini IHA", "B. Fuze"]
    TARGET_CODES = ["F16", "HEL", "IHA", "BFZ"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_order: list[str] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # ── Başlık ─────────────────────────────────────────
        self._title = QLabel("HEDEF SECIM")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 12px; font-weight: bold; "
            "padding: 3px; border-bottom: 1px solid #3A3A3A;"
        )
        layout.addWidget(self._title)

        # ── SEÇİM ALANI (seçim tamamlanınca gizlenecek) ────
        self._selection_widget = QWidget()
        sel_layout = QVBoxLayout(self._selection_widget)
        sel_layout.setContentsMargins(0, 2, 0, 2)
        sel_layout.setSpacing(3)

        # Dikey tek sütun hedef butonları
        self._target_buttons: list[QPushButton] = []
        for code, target_name in zip(self.TARGET_CODES, self.TARGET_TYPES):
            btn = QPushButton(f"[{code}]  {target_name}")
            btn.setObjectName("targetBtn")
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            btn.setFixedHeight(34)
            btn.setStyleSheet(
                "QPushButton#targetBtn {"
                "  font-size: 12px; font-weight: bold; padding: 4px 6px;"
                "  text-align: left;"
                "}"
            )
            btn.clicked.connect(
                lambda checked, t=target_name: self._on_target_clicked(t)
            )
            sel_layout.addWidget(btn)
            self._target_buttons.append(btn)

        # Canlı sıralama listesi (seçim sırasında güncellenir)
        self._order_list = QListWidget()
        self._order_list.setMaximumHeight(90)
        self._order_list.setStyleSheet("font-size: 11px;")
        sel_layout.addWidget(self._order_list)

        layout.addWidget(self._selection_widget)

        # ── BİLGİ PANELİ (seçim tamamlanınca gösterilecek) ──
        self._info_widget = QWidget()
        self._info_widget.setVisible(False)
        info_layout = QVBoxLayout(self._info_widget)
        info_layout.setContentsMargins(0, 2, 0, 2)
        info_layout.setSpacing(3)

        # Durum göstergesi
        self._status_label = QLabel("ANGAJMAN TAMAM")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(
            "color: #33CC33; font-size: 12px; font-weight: bold; "
            "padding: 4px; border: 1px solid #33CC33; border-radius: 3px; "
            "background-color: #1A2E1A;"
        )
        info_layout.addWidget(self._status_label)

        # Sıralama özet satırları (4 adet QLabel)
        self._summary_labels: list[QLabel] = []
        for i in range(self.MAX_TARGETS):
            lbl = QLabel("")
            lbl.setStyleSheet(
                "color: #E0E0E0; font-size: 12px; font-weight: bold; "
                "padding: 3px 6px; background-color: #2A2A2A; "
                "border-left: 3px solid #3399FF; border-radius: 2px;"
            )
            info_layout.addWidget(lbl)
            self._summary_labels.append(lbl)

        info_layout.addStretch()
        layout.addWidget(self._info_widget)

        # ── SIFIRLA butonu (her zaman görünür) ──────────────
        self._reset_btn = QPushButton("SIFIRLA")
        self._reset_btn.setObjectName("resetBtn")
        self._reset_btn.setFixedHeight(26)
        self._reset_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self._reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self._reset_btn)

        layout.addStretch()

    def _on_target_clicked(self, target_name: str):
        """Hedef butonuna tıklandığında sıraya ekle."""
        if len(self._target_order) >= self.MAX_TARGETS:
            return

        order_num = len(self._target_order) + 1
        self._target_order.append(target_name)
        self._order_list.addItem(f"{order_num}. {target_name}")
        self.target_order_changed.emit(self._target_order.copy())

        # 4 hedef tamamlandıysa bilgi moduna geç
        if len(self._target_order) >= self.MAX_TARGETS:
            self._switch_to_info_mode()

    def _switch_to_info_mode(self):
        """Seçim alanını gizle, bilgi panelini göster."""
        self._title.setText("ANGAJMAN SIRASI")
        self._title.setStyleSheet(
            "color: #33CC33; font-size: 12px; font-weight: bold; "
            "padding: 3px; border-bottom: 1px solid #33CC33;"
        )
        self._selection_widget.setVisible(False)
        self._info_widget.setVisible(True)

        # Özet etiketlerini doldur
        code_map = dict(zip(self.TARGET_TYPES, self.TARGET_CODES))
        for i, target in enumerate(self._target_order):
            code = code_map.get(target, "---")
            self._summary_labels[i].setText(f" {i + 1}. [{code}] {target}")

    def _on_reset(self):
        """Hedef sırasını sıfırla, seçim moduna dön."""
        self._target_order.clear()
        self._order_list.clear()

        # Seçim moduna geri dön
        self._title.setText("HEDEF SECIM")
        self._title.setStyleSheet(
            "color: #3399FF; font-size: 12px; font-weight: bold; "
            "padding: 3px; border-bottom: 1px solid #3A3A3A;"
        )
        self._selection_widget.setVisible(True)
        self._info_widget.setVisible(False)

        for lbl in self._summary_labels:
            lbl.setText("")

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
