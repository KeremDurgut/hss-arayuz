import sys
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QPixmap  # Görüntüyü label'a basmak için eklendi

from arayuz_ui import Ui_CelikkubbeUI
from kamera_modulu import KameraThread  # Yeni yazdığımız modülü içe aktarıyoruz


class CelikkubbeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CelikkubbeUI()
        self.ui.setupUi(self)

        self.sistem_kilitli = False
        self.lazer_aktif = False
        self.fan_aktif = False
        self.kamera_aktif = False

        # --- KAMERA KURULUMU ---
        self.kamera_thread = KameraThread(kamera_id=0)
        self.kamera_thread.kare_yakalandi.connect(self.kamera_guncelle)
        self.ui.btnKamera.clicked.connect(self.toggle_kamera)
        # -----------------------

        # Buton Bağlantıları
        self.ui.btnAcilDurdur.clicked.connect(self.acil_durdurma)
        self.ui.btnSistemRestart.clicked.connect(self.sistemi_baslat)
        self.ui.btnLazer.clicked.connect(self.toggle_lazer)
        self.ui.btnFan.clicked.connect(self.toggle_fan)

        self.ui.btnMod1.clicked.connect(lambda: self.mod_degistir(1))
        self.ui.btnMod2.clicked.connect(lambda: self.mod_degistir(2))
        self.ui.btnMod3.clicked.connect(lambda: self.mod_degistir(3))

        self.ui.btnYasakliToggle.clicked.connect(self.toggle_yasakli_alan)
        self.ui.btnYasakKaydet.clicked.connect(self.yasakli_alan_kaydet)

        self.ui.btnAtes.clicked.connect(self.ates_et)
        self.ui.radioManuel.toggled.connect(self.imha_modu_degisti)

        self.sistemi_baslat()

    def log_yaz(self, mesaj):
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        satir = f"[{zaman}] {mesaj}"
        self.ui.txtLogPanel.append(satir)
        scrollbar = self.ui.txtLogPanel.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def led_guncelle(self, led_objesi, durum):
        durum_metni = "aktif" if durum else "pasif"
        led_objesi.setProperty("ledDurum", durum_metni)
        led_objesi.style().unpolish(led_objesi)
        led_objesi.style().polish(led_objesi)

    # ================= YENİ EKLENEN KAMERA METOTLARI =================
    @Slot(QImage)
    def kamera_guncelle(self, qt_image):
        if self.sistem_kilitli: return

        # Kamera modülünden gelen resmi al, label boyutlarına göre (bozmadan) ölçeklendir
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(self.ui.lblKameraFeed.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.lblKameraFeed.setPixmap(pixmap)

    @Slot()
    def toggle_kamera(self):
        if self.sistem_kilitli: return
        self.kamera_aktif = not self.kamera_aktif

        if self.kamera_aktif:
            self.kamera_thread.start()
            self.ui.btnKamera.setText("KAMERAYI DURDUR")
            self.log_yaz("[OPTİK] Kamera sensörü devrede.")
        else:
            self.kamera_thread.durdur()
            self.ui.btnKamera.setText("KAMERAYI ÇALIŞTIR")
            self.ui.lblKameraFeed.clear()
            self.ui.lblKameraFeed.setText("KAMERA AKIŞI DURDURULDU")
            self.log_yaz("[OPTİK] Kamera sensörü devredışı bırakıldı.")

    # =================================================================

    @Slot()
    def toggle_yasakli_alan(self):
        su_an_acik = self.ui.grpYasakliAlan.isVisible()
        self.ui.grpYasakliAlan.setVisible(not su_an_acik)
        self.ui.btnYasakliToggle.setText(
            "ATIŞA YASAKLI ALAN TANIMLA ▼" if su_an_acik else "ATIŞA YASAKLI ALAN TANIMLA ▲")

    @Slot()
    def sistemi_baslat(self):
        self.sistem_kilitli = False
        self.ui.btnAtes.setEnabled(True)
        self.ui.btnAcilDurdur.setEnabled(True)

        self.ui.lblKameraFeed.setProperty("kameraDurum", "hazir")
        self.ui.lblKameraFeed.style().unpolish(self.ui.lblKameraFeed)
        self.ui.lblKameraFeed.style().polish(self.ui.lblKameraFeed)

        # Sistemi başlatınca kamerayı da otomatik aç
        if not self.kamera_aktif:
            self.toggle_kamera()

        self.led_guncelle(self.ui.lblLedKamera, True)
        self.log_yaz("[SYSTEM] Sistem başlatıldı. Donanım kontrolleri tamam.")
        self.mod_degistir(0)

    @Slot()
    def acil_durdurma(self):
        self.sistem_kilitli = True
        self.ui.btnAtes.setEnabled(False)
        self.led_guncelle(self.ui.lblLedLazer, False)
        self.led_guncelle(self.ui.lblLedFan, False)
        self.led_guncelle(self.ui.lblLedTakip, False)
        self.led_guncelle(self.ui.lblLedKamera, False)

        # Kamerayı arka planda da durdur
        if self.kamera_aktif:
            self.kamera_thread.durdur()
            self.kamera_aktif = False
            self.ui.btnKamera.setText("KAMERAYI ÇALIŞTIR")

        self.ui.lblKameraFeed.setProperty("kameraDurum", "estop")
        self.ui.lblKameraFeed.style().unpolish(self.ui.lblKameraFeed)
        self.ui.lblKameraFeed.style().polish(self.ui.lblKameraFeed)

        self.ui.lblKameraFeed.clear()  # Varsa ekrandaki son kareyi temizle
        self.ui.lblKameraFeed.setText("!!! E-STOP !!!\nSİSTEM KİLİTLİ")

        self.log_yaz("[CRITICAL] ACİL DURDURMA BUTONUNA BASILDI! TÜM SİLAH VE MOTOR GÜCÜ KESİLDİ.")

    @Slot()
    def toggle_lazer(self):
        if self.sistem_kilitli: return
        self.lazer_aktif = not self.lazer_aktif
        self.led_guncelle(self.ui.lblLedLazer, self.lazer_aktif)
        self.ui.btnLazer.setText("LAZERİ DURDUR" if self.lazer_aktif else "LAZERİ ÇALIŞTIR")
        self.log_yaz(f"[DONANIM] Hedefleme Lazeri {'Aktif' if self.lazer_aktif else 'Kapalı'}.")

    @Slot()
    def toggle_fan(self):
        if self.sistem_kilitli: return
        self.fan_aktif = not self.fan_aktif
        self.led_guncelle(self.ui.lblLedFan, self.fan_aktif)
        self.ui.btnFan.setText("FANLARI DURDUR" if self.fan_aktif else "FANLARI ÇALIŞTIR")
        self.log_yaz(f"[DONANIM] Soğutma Fanları {'Çalışıyor' if self.fan_aktif else 'Durduruldu'}.")

    @Slot()
    def imha_modu_degisti(self):
        if self.ui.radioOtomatik.isChecked():
            self.ui.btnAtes.setEnabled(False)
            self.ui.btnAtes.setText("OTOMATİK ATIŞ DEVREDE")
            self.log_yaz("[UYARI] İmha Modu: OTOMATİK. Manuel atış yetkisi devredışı bırakıldı.")
        else:
            self.ui.btnAtes.setEnabled(True)
            self.ui.btnAtes.setText("HEDEFİ İMHA ET")
            self.log_yaz("[UYARI] İmha Modu: MANUEL. Atış yetkisi operatöre verildi.")

    @Slot(int)
    def mod_degistir(self, mod_no):
        if self.sistem_kilitli: return
        mod_isimleri = {0: "SERBEST", 1: "MOD 1 (Aşama 1: Sabit Hedef)", 2: "MOD 2 (Aşama 2: Sürü Saldırısı)",
                        3: "MOD 3 (Aşama 3: Dost/Düşman Sınıflandırma)"}
        self.ui.lblCalismaModu.setText(f"Çalışma Modu: {mod_isimleri[mod_no]}")
        self.log_yaz(f"[KOMUTA] Sistem durumu {mod_isimleri[mod_no]} olarak güncellendi.")

        if mod_no in [2, 3]:
            self.ui.radioOtomatik.setChecked(True)
            self.led_guncelle(self.ui.lblLedTakip, True)
        else:
            self.ui.radioManuel.setChecked(True)
            self.led_guncelle(self.ui.lblLedTakip, False)

    @Slot()
    def yasakli_alan_kaydet(self):
        x1 = self.ui.txtX1.text()
        x2 = self.ui.txtX2.text()
        self.log_yaz(f"[GÜVENLİK] Atışa Yasaklı Alan güncellendi. Limitler: X1({x1}), X2({x2})")

    @Slot()
    def ates_et(self):
        if self.sistem_kilitli or self.ui.radioOtomatik.isChecked(): return
        self.log_yaz(">>> [ATIŞ KONTROL] Silah ateşlendi! Hedefin vurulduğu teyit ediliyor...")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    qss_yolu = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_yolu):
        with open(qss_yolu, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print("UYARI: style.qss dosyası bulunamadı, varsayılan tema kullanılacak.")

    uygulama = CelikkubbeApp()
    uygulama.show()
    sys.exit(app.exec())