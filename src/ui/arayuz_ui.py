from PySide6.QtCore import QMetaObject, QSize, Qt
from PySide6.QtWidgets import (QGridLayout, QGroupBox, QHBoxLayout,
                               QLabel, QPushButton, QSizePolicy, QLineEdit,
                               QSpacerItem, QTextEdit, QVBoxLayout, QWidget, QFrame, QRadioButton)


class Ui_CelikkubbeUI(object):
    def setupUi(self, CelikkubbeUI):
        if not CelikkubbeUI.objectName():
            CelikkubbeUI.setObjectName(u"CelikkubbeUI")
        CelikkubbeUI.resize(1280, 720)
        CelikkubbeUI.setWindowTitle(u"ERGENEKON HSS - TAKTİK KONTROL ARAYÜZÜ")

        self.centralwidget = QWidget(CelikkubbeUI)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(10)

        # ================= SOL/ANA PANEL =================
        self.panelAna = QFrame(self.centralwidget)
        self.panelAna.setObjectName("panelAna")
        self.layoutAna = QVBoxLayout(self.panelAna)

        self.lblCalismaModu = QLabel("Çalışma Modu: SERBEST")
        self.lblCalismaModu.setObjectName("lblCalismaModu")
        self.layoutAna.addWidget(self.lblCalismaModu)

        self.lblKameraFeed = QLabel("KAMERA AKIŞI\n(SİNYAL BEKLENİYOR)")
        self.lblKameraFeed.setObjectName("lblKameraFeed")
        self.lblKameraFeed.setAlignment(Qt.AlignCenter)
        self.lblKameraFeed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layoutAna.addWidget(self.lblKameraFeed, stretch=3)

        self.txtLogPanel = QTextEdit()
        self.txtLogPanel.setObjectName("txtLogPanel")
        self.txtLogPanel.setReadOnly(True)
        self.txtLogPanel.setPlaceholderText("LOG PANELİ BAŞLATILIYOR...")
        self.layoutAna.addWidget(self.txtLogPanel, stretch=1)

        self.horizontalLayout.addWidget(self.panelAna)

        # ================= SAĞ PANEL =================
        self.panelSag = QFrame(self.centralwidget)
        self.panelSag.setObjectName("panelSag")  # QSS tarafında yakalamak için ID verildi
        self.panelSag.setMinimumWidth(320)
        self.panelSag.setMaximumWidth(380)
        self.layoutSag = QVBoxLayout(self.panelSag)
        self.layoutSag.setSpacing(8)

        self.layoutSicaklik = QHBoxLayout()
        self.lblSicaklikBaslik = QLabel("Sistem Sıcaklığı:")
        self.lblSicaklikDeger = QLabel("27°C / İDEAL")
        self.lblSicaklikDeger.setObjectName("lblSicaklikDeger")
        self.lblSicaklikDeger.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.layoutSicaklik.addWidget(self.lblSicaklikBaslik)
        self.layoutSicaklik.addWidget(self.lblSicaklikDeger)
        self.layoutSag.addLayout(self.layoutSicaklik)

        self.gridLeds = QGridLayout()
        self.lblLedLazer = QLabel()
        self.lblLedKamera = QLabel()
        self.lblLedFan = QLabel()
        self.lblLedTakip = QLabel()

        # Ledlere ortak sınıf ve başlangıç durumu verelim
        for led in [self.lblLedLazer, self.lblLedKamera, self.lblLedFan, self.lblLedTakip]:
            led.setProperty("ledDurum", "pasif")

        self.gridLeds.addWidget(QLabel("LAZER:"), 0, 0)
        self.gridLeds.addWidget(self.lblLedLazer, 0, 1)
        self.gridLeds.addWidget(QLabel("KAMERA:"), 0, 2)
        self.gridLeds.addWidget(self.lblLedKamera, 0, 3)
        self.gridLeds.addWidget(QLabel("FANLAR:"), 1, 0)
        self.gridLeds.addWidget(self.lblLedFan, 1, 1)
        self.gridLeds.addWidget(QLabel("TAKİP:"), 1, 2)
        self.gridLeds.addWidget(self.lblLedTakip, 1, 3)
        self.layoutSag.addLayout(self.gridLeds)

        self.layoutMod = QHBoxLayout()
        self.lblModSecim = QLabel("İmha Modu:")
        self.radioManuel = QRadioButton("MANUEL")
        self.radioOtomatik = QRadioButton("OTOMATİK")
        self.radioManuel.setChecked(True)
        self.layoutMod.addWidget(self.lblModSecim)
        self.layoutMod.addWidget(self.radioManuel)
        self.layoutMod.addWidget(self.radioOtomatik)
        self.layoutSag.addLayout(self.layoutMod)

        cizgi1 = QFrame()
        cizgi1.setFrameShape(QFrame.HLine)
        cizgi1.setObjectName("ayiriciCizgi")  # QSS için
        self.layoutSag.addWidget(cizgi1)

        self.btnLazer = QPushButton("LAZERİ ÇALIŞTIR")
        self.btnKamera = QPushButton("KAMERAYI DURDUR")
        self.btnFan = QPushButton("FANLARI ÇALIŞTIR")
        self.layoutSag.addWidget(self.btnLazer)
        self.layoutSag.addWidget(self.btnKamera)
        self.layoutSag.addWidget(self.btnFan)

        cizgi2 = QFrame()
        cizgi2.setFrameShape(QFrame.HLine)
        cizgi2.setObjectName("ayiriciCizgi")  # QSS için
        self.layoutSag.addWidget(cizgi2)

        self.btnMod1 = QPushButton("MOD 1'E GEÇ (Aşama 1)")
        self.btnMod2 = QPushButton("MOD 2'YE GEÇ (Aşama 2)")
        self.btnMod3 = QPushButton("MOD 3'E GEÇ (Aşama 3)")
        self.layoutSag.addWidget(self.btnMod1)
        self.layoutSag.addWidget(self.btnMod2)
        self.layoutSag.addWidget(self.btnMod3)

        self.btnYasakliToggle = QPushButton("ATIŞA YASAKLI ALAN TANIMLA ▼")
        self.btnYasakliToggle.setObjectName("btnYasakliToggle")
        self.layoutSag.addWidget(self.btnYasakliToggle)

        self.grpYasakliAlan = QGroupBox()
        self.grpYasakliAlan.setVisible(False)
        self.layoutYasakli = QGridLayout(self.grpYasakliAlan)
        self.layoutYasakli.addWidget(QLabel("X1 (Min):"), 0, 0)
        self.txtX1 = QLineEdit("-45")
        self.layoutYasakli.addWidget(self.txtX1, 0, 1)
        self.layoutYasakli.addWidget(QLabel("X2 (Max):"), 1, 0)
        self.txtX2 = QLineEdit("45")
        self.layoutYasakli.addWidget(self.txtX2, 1, 1)
        self.btnYasakKaydet = QPushButton("KAYDET")
        self.layoutYasakli.addWidget(self.btnYasakKaydet, 2, 0, 1, 2)
        self.layoutSag.addWidget(self.grpYasakliAlan)

        self.layoutSag.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.btnAtes = QPushButton("HEDEFİ İMHA ET")
        self.btnAtes.setObjectName("btnAtes")
        self.layoutSag.addWidget(self.btnAtes)

        self.btnSistemRestart = QPushButton("SİSTEMİ YENİDEN BAŞLAT")
        self.btnAcilDurdur = QPushButton("ACİL DURDURMA (E-STOP)")
        self.btnAcilDurdur.setObjectName("btnAcilDurdur")
        self.layoutSag.addWidget(self.btnSistemRestart)
        self.layoutSag.addWidget(self.btnAcilDurdur)

        self.horizontalLayout.addWidget(self.panelSag)
        CelikkubbeUI.setCentralWidget(self.centralwidget)
        QMetaObject.connectSlotsByName(CelikkubbeUI)