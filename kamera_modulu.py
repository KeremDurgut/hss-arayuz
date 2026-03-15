import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


class KameraThread(QThread):
    # Ana arayüze göndereceğimiz sinyal tanımlaması
    kare_yakalandi = Signal(QImage)

    def __init__(self, kamera_id=0):
        super().__init__()
        self.kamera_id = kamera_id  # 0 varsayılan dahili kameradır
        self.calisiyor = False

    def run(self):
        self.calisiyor = True
        cap = cv2.VideoCapture(self.kamera_id)

        while self.calisiyor:
            ret, frame = cap.read()
            if ret:
                # OpenCV varsayılan olarak BGR (Mavi-Yeşil-Kırmızı) okur.
                # Arayüzde doğru renkleri görmek için bunu RGB'ye çeviriyoruz.
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w

                # Resmi Qt'nin anlayacağı formata (QImage) dönüştür
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

                # Dönüşen resmi arayüze fırlat
                self.kare_yakalandi.emit(qt_image)
            else:
                break

        cap.release()

    def durdur(self):
        self.calisiyor = False
        self.wait()  # Güvenli kapanış için thread'in durmasını bekle