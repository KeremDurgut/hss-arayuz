"""
Çelikkubbe HMI — Ana Pencere (MainWindow)
==========================================
Tüm arayüz bileşenlerini bir araya getirir:
  • Üst Durum Çubuğu (Header) — telemetri, aşama seçici
  • Merkez Alan — QThread ile kamera akışı (QLabel)
  • Sol/Sağ QStackedWidget — bağlama duyarlı paneller
  • Alt Panel — Sistem olay günlüğü konsolu (QTextEdit)
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit, QFrame, QStackedWidget,
    QSplitter, QSizePolicy,
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QPixmap, QFont

from core.video_worker import VideoWorker
from ui.stage1_panel import Stage1LeftPanel, Stage1RightPanel
from ui.stage2_3_panel import Stage23LeftPanel, Stage23RightPanel


class MainWindow(QMainWindow):
    """Çelikkubbe HMI ana pencere sınıfı."""

    STAGE_NAMES = ["Aşama 1 — Manuel", "Aşama 2 — Otonom Sürü", "Aşama 3 — Sınıflandırma"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÇELİKKUBBE — Taktiksel Komuta Kontrol HMI")
        self.setMinimumSize(1280, 800)
        self.showMaximized()

        # Telemetri simülasyon verileri
        self._pan_angle = 0.0
        self._tilt_angle = 0.0
        self._ai_fps = 30
        self._camera_ok = True

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── 1. HEADER ────────────────────────────────────────
        header = self._build_header()
        main_layout.addWidget(header)

        # ── 2. MERKEZ İÇERİK (Sol Panel | Video | Sağ Panel) ─
        content_widget = self._build_content()
        main_layout.addWidget(content_widget, stretch=1)

        # ── 3. FOOTER (Log Console) ──────────────────────────
        footer = self._build_footer()
        main_layout.addWidget(footer)

        # ── Video Worker ─────────────────────────────────────
        self._video_worker = VideoWorker(camera_index=0)
        self._video_worker.frame_ready.connect(self._on_frame_ready)
        self._video_worker.start()

        # ── Telemetri simülasyon zamanlayıcı ──────────────────
        self._telemetry_timer = QTimer(self)
        self._telemetry_timer.timeout.connect(self._update_telemetry)
        self._telemetry_timer.start(500)  # 500ms aralıkla güncelle

        # Başlangıç log mesajları
        self._log("SİSTEM BAŞLATILDI — Çelikkubbe HMI v1.0")
        self._log("Video akışı başlatılıyor...")
        self._log("Taret kalibrasyonu tamamlandı.")
        self._log("E-STOP DURUMU: GÜVENLİ")

        # Aşama 1 ile başla
        self._on_stage_changed(0)

    # ══════════════════════════════════════════════════════════
    #  HEADER
    # ══════════════════════════════════════════════════════════
    def _build_header(self) -> QFrame:
        """Üst durum çubuğunu oluşturur."""
        frame = QFrame()
        frame.setObjectName("headerFrame")
        frame.setFixedHeight(52)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(16)

        # Aşama seçici (test amaçlı QComboBox)
        stage_label = QLabel("AŞAMA:")
        stage_label.setStyleSheet("color: #A0A0A0; font-weight: bold;")
        layout.addWidget(stage_label)

        self._stage_combo = QComboBox()
        self._stage_combo.addItems(self.STAGE_NAMES)
        self._stage_combo.currentIndexChanged.connect(self._on_stage_changed)
        layout.addWidget(self._stage_combo)

        # Aşama gösterge etiketi
        self._stage_indicator = QLabel("AŞAMA 1")
        self._stage_indicator.setObjectName("stageIndicator")
        layout.addWidget(self._stage_indicator)

        layout.addStretch()

        # Telemetri verileri
        self._pan_tilt_label = QLabel("Pan: 0.0° / Tilt: 0.0°")
        self._pan_tilt_label.setObjectName("telemetryLabel")
        layout.addWidget(self._pan_tilt_label)

        self._add_separator(layout)

        self._ai_fps_label = QLabel("AI FPS: 30")
        self._ai_fps_label.setObjectName("telemetryLabel")
        layout.addWidget(self._ai_fps_label)

        self._add_separator(layout)

        self._camera_label = QLabel("📷 KAMERA: OK")
        self._camera_label.setStyleSheet(
            "color: #33CC33; font-weight: bold; font-size: 13px;"
        )
        layout.addWidget(self._camera_label)

        self._add_separator(layout)

        self._estop_label = QLabel("E-STOP: OK")
        self._estop_label.setStyleSheet(
            "color: #33CC33; font-weight: bold; font-size: 13px;"
        )
        layout.addWidget(self._estop_label)

        return frame

    @staticmethod
    def _add_separator(layout: QHBoxLayout):
        """Küçük dikey ayırıcı ekler."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #3A3A3A;")
        sep.setFixedWidth(2)
        layout.addWidget(sep)

    # ══════════════════════════════════════════════════════════
    #  MERKEZ İÇERİK
    # ══════════════════════════════════════════════════════════
    def _build_content(self) -> QWidget:
        """Sol panel | Video akışı | Sağ panel düzenini oluşturur."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # ── Sol QStackedWidget ─────────────────────────
        self._left_stack = QStackedWidget()
        self._left_stack.setFixedWidth(280)

        self._stage1_left = Stage1LeftPanel()
        self._stage23_left = Stage23LeftPanel()

        self._left_stack.addWidget(self._stage1_left)   # index 0
        self._left_stack.addWidget(self._stage23_left)   # index 1

        layout.addWidget(self._left_stack)

        # ── Merkez Video Alanı ─────────────────────────
        video_frame = QFrame()
        video_frame.setStyleSheet(
            "QFrame { background-color: #0D0D0D; border: 2px solid #3A3A3A; border-radius: 4px; }"
        )
        video_layout = QVBoxLayout(video_frame)
        video_layout.setContentsMargins(2, 2, 2, 2)

        self._video_label = QLabel("KAMERA AKIŞI BEKLENİYOR...")
        self._video_label.setObjectName("videoPlaceholder")
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._video_label.setMinimumSize(480, 360)
        video_layout.addWidget(self._video_label)

        layout.addWidget(video_frame, stretch=1)

        # ── Sağ QStackedWidget ─────────────────────────
        self._right_stack = QStackedWidget()
        self._right_stack.setFixedWidth(280)

        self._stage1_right = Stage1RightPanel()
        self._stage23_right = Stage23RightPanel()

        self._right_stack.addWidget(self._stage1_right)   # index 0
        self._right_stack.addWidget(self._stage23_right)   # index 1

        layout.addWidget(self._right_stack)

        # ── Panel sinyallerini bağla ───────────────────
        self._stage1_left.target_order_changed.connect(self._on_target_order_changed)
        self._stage1_right.turret_command.connect(self._on_turret_command)
        self._stage1_right.fire_command.connect(self._on_fire_command)

        return widget

    # ══════════════════════════════════════════════════════════
    #  FOOTER (Log Console)
    # ══════════════════════════════════════════════════════════
    def _build_footer(self) -> QFrame:
        """Alt sistem olay günlüğü konsolunu oluşturur."""
        frame = QFrame()
        frame.setObjectName("footerFrame")
        frame.setFixedHeight(140)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        header_layout = QHBoxLayout()
        log_icon = QLabel("⚠")
        log_icon.setStyleSheet("color: #FFCC00; font-size: 16px;")
        header_layout.addWidget(log_icon)

        log_title = QLabel("SİSTEM OLAY GÜNLÜĞÜ")
        log_title.setStyleSheet(
            "color: #A0A0A0; font-size: 12px; font-weight: bold;"
        )
        header_layout.addWidget(log_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self._log_console = QTextEdit()
        self._log_console.setObjectName("logConsole")
        self._log_console.setReadOnly(True)
        self._log_console.setFont(QFont("Consolas", 10))
        layout.addWidget(self._log_console)

        return frame

    # ══════════════════════════════════════════════════════════
    #  SLOT'LAR
    # ══════════════════════════════════════════════════════════
    @Slot(int)
    def _on_stage_changed(self, index: int):
        """Aşama değiştiğinde panelleri günceller."""
        if index == 0:
            # Aşama 1 — Manuel
            self._left_stack.setCurrentIndex(0)
            self._right_stack.setCurrentIndex(0)
            self._stage_indicator.setText("AŞAMA 1 — MANUEL")
            self._stage_indicator.setStyleSheet(
                "color: #3399FF; font-size: 20px; font-weight: bold; padding: 2px 10px;"
            )
            self._log("AŞAMA DEĞİŞTİ → Aşama 1 (Manuel Angajman)")
        elif index == 1:
            # Aşama 2 — Otonom Sürü
            self._left_stack.setCurrentIndex(1)
            self._right_stack.setCurrentIndex(1)
            self._stage_indicator.setText("AŞAMA 2 — OTONOM SÜRÜ")
            self._stage_indicator.setStyleSheet(
                "color: #FFCC00; font-size: 20px; font-weight: bold; padding: 2px 10px;"
            )
            self._log("AŞAMA DEĞİŞTİ → Aşama 2 (Otonom Sürü Modu)")
        elif index == 2:
            # Aşama 3 — Sınıflandırma
            self._left_stack.setCurrentIndex(1)
            self._right_stack.setCurrentIndex(1)
            self._stage_indicator.setText("AŞAMA 3 — SINIFLANDIRMA")
            self._stage_indicator.setStyleSheet(
                "color: #FF3333; font-size: 20px; font-weight: bold; padding: 2px 10px;"
            )
            self._log("AŞAMA DEĞİŞTİ → Aşama 3 (Sınıflandırma Modu)")

    @Slot(QPixmap)
    def _on_frame_ready(self, pixmap: QPixmap):
        """Yeni video karesi geldiğinde merkeze yansıt."""
        scaled = pixmap.scaled(
            self._video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._video_label.setPixmap(scaled)

    @Slot(list)
    def _on_target_order_changed(self, order: list):
        """Hedef sırası güncellendiğinde log yaz."""
        if order:
            target_str = ", ".join(f"{i+1}.{t}" for i, t in enumerate(order))
            self._log(f"HEDEF SIRASI GÜNCELLENDİ: {target_str}")
        else:
            self._log("HEDEF SIRASI SIFIRLANDI")

    @Slot(str)
    def _on_turret_command(self, direction: str):
        """Taret yönlendirme komutu geldiğinde açıyı güncelle ve logla."""
        step = 2.5
        if direction == "UP":
            self._tilt_angle = min(90.0, self._tilt_angle + step)
        elif direction == "DOWN":
            self._tilt_angle = max(-90.0, self._tilt_angle - step)
        elif direction == "LEFT":
            self._pan_angle = (self._pan_angle - step) % 360.0
        elif direction == "RIGHT":
            self._pan_angle = (self._pan_angle + step) % 360.0

        self._pan_tilt_label.setText(
            f"Pan: {self._pan_angle:.1f}° / Tilt: {self._tilt_angle:.1f}°"
        )
        self._log(
            f"TARET KOMUTU: {direction} → "
            f"Pan: {self._pan_angle:.1f}° / Tilt: {self._tilt_angle:.1f}°"
        )

    @Slot()
    def _on_fire_command(self):
        """Ateş komutu geldiğinde logla."""
        self._log(
            "🔥 ATEŞ KOMUTU VERİLDİ — "
            f"Pan: {self._pan_angle:.1f}° / Tilt: {self._tilt_angle:.1f}°"
        )

    @Slot()
    def _update_telemetry(self):
        """Telemetri verilerini periyodik olarak güncelle (simülasyon)."""
        self._pan_tilt_label.setText(
            f"Pan: {self._pan_angle:.1f}° / Tilt: {self._tilt_angle:.1f}°"
        )
        self._ai_fps_label.setText(f"AI FPS: {self._ai_fps}")

    # ══════════════════════════════════════════════════════════
    #  YARDIMCI METOTLAR
    # ══════════════════════════════════════════════════════════
    def _log(self, message: str):
        """Olay günlüğüne tarih-saat damgalı mesaj ekle."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._log_console.append(f"[{timestamp}]  {message}")
        # Otomatik en alta kaydır
        scrollbar = self._log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Pencere kapatılırken video thread'ini durdur."""
        self._video_worker.stop()
        self._video_worker.wait(3000)
        super().closeEvent(event)
