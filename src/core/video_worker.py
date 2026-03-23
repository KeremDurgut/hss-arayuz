"""
Çelikkubbe HMI — Video İşçi Thread'i
=====================================
Kamera (cv2.VideoCapture) akışını ana GUI'yi dondurmadan QThread
üzerinden yürütür. Her kareyi QPixmap olarak Signal ile yayımlar.
Kamera bulunamazsa sentetik test görüntüsü üretir.
"""

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal, Slot, QMutex, QMutexLocker
from PySide6.QtGui import QImage, QPixmap


class VideoWorker(QThread):
    """Kamera akışını arka planda okuyan QThread sınıfı."""

    # Yeni kare hazır olduğunda yayımlanan sinyal
    frame_ready = Signal(QPixmap)

    def __init__(self, camera_index: int = 0, parent=None):
        super().__init__(parent)
        self._camera_index = camera_index
        self._running = False
        self._mutex = QMutex()

    @Slot()
    def stop(self):
        """Thread'i güvenli biçimde durdur."""
        with QMutexLocker(self._mutex):
            self._running = False

    def run(self):
        """
        Thread'in ana döngüsü. Kamerayı açar, kareleri okur ve
        frame_ready sinyali ile QPixmap olarak yayımlar. Kamera
        açılamazsa sentetik test görüntüsü (HUD simülasyonu) üretir.
        """
        self._running = True
        cap = cv2.VideoCapture(self._camera_index)
        use_camera = cap.isOpened()

        frame_counter = 0

        while True:
            # Thread durduruldu mu kontrol et
            with QMutexLocker(self._mutex):
                if not self._running:
                    break

            if use_camera:
                ret, frame = cap.read()
                if not ret:
                    # Kamera başarısız olduysa sentetik moda geç
                    use_camera = False
                    continue
            else:
                # ── Sentetik Test Görüntüsü Üret ──────────────
                frame = self._generate_synthetic_frame(frame_counter)
                frame_counter += 1

            # BGR → RGB dönüşümü
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w

            qt_image = QImage(
                frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(qt_image)
            self.frame_ready.emit(pixmap)

            # ~30 FPS hedefi
            self.msleep(33)

        if cap.isOpened():
            cap.release()

    @staticmethod
    def _generate_synthetic_frame(counter: int) -> np.ndarray:
        """
        Kamera yokken gösterilecek sentetik HUD test görüntüsü.
        Yeşil grid ve tarama çizgisi efekti ile taktiksel görünüm sağlar.
        """
        width, height = 640, 480
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Arka plan: çok koyu yeşil gradient
        for y in range(height):
            intensity = int(8 + (y / height) * 12)
            frame[y, :] = [0, intensity, 0]

        # Grid çizgileri
        grid_color = (0, 40, 0)
        for x in range(0, width, 40):
            cv2.line(frame, (x, 0), (x, height), grid_color, 1)
        for y in range(0, height, 40):
            cv2.line(frame, (0, y), (width, y), grid_color, 1)

        # Merkez artı (crosshair)
        cx, cy = width // 2, height // 2
        cross_color = (0, 200, 0)
        cv2.line(frame, (cx - 30, cy), (cx - 10, cy), cross_color, 2)
        cv2.line(frame, (cx + 10, cy), (cx + 30, cy), cross_color, 2)
        cv2.line(frame, (cx, cy - 30), (cx, cy - 10), cross_color, 2)
        cv2.line(frame, (cx, cy + 10), (cx, cy + 30), cross_color, 2)

        # İç daire
        cv2.circle(frame, (cx, cy), 60, (0, 100, 0), 1)
        cv2.circle(frame, (cx, cy), 120, (0, 60, 0), 1)

        # Tarama çizgisi efekti (sweep line)
        scan_y = (counter * 3) % height
        overlay = frame.copy()
        cv2.line(overlay, (0, scan_y), (width, scan_y), (0, 80, 0), 2)
        # Scan halo efekti
        for offset in range(1, 20):
            alpha = max(0, 80 - offset * 4)
            y_pos = scan_y - offset
            if 0 <= y_pos < height:
                cv2.line(overlay, (0, y_pos), (width, y_pos), (0, alpha // 2, 0), 1)
        frame = overlay

        # HUD metin bilgileri
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_color = (0, 200, 0)
        cv2.putText(frame, "CELIKKUBBE HMI", (20, 30), font, 0.6, text_color, 1)
        cv2.putText(frame, "KAMERA: SENTETIK MOD", (20, 55), font, 0.45, (0, 150, 0), 1)
        cv2.putText(
            frame,
            f"FRAME: {counter:06d}",
            (width - 200, 30),
            font, 0.45, text_color, 1,
        )
        cv2.putText(
            frame,
            "TRK: BEKLENIYOR",
            (width - 200, 55),
            font, 0.45, (0, 150, 0), 1,
        )

        # Alt bilgi çubuğu
        cv2.rectangle(frame, (0, height - 35), (width, height), (0, 20, 0), -1)
        cv2.putText(
            frame,
            "SYS OK | GPS LOCK | TARET HAZIR",
            (15, height - 12),
            font, 0.4, (0, 180, 0), 1,
        )

        return frame
