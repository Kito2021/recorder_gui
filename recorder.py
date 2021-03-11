import pyaudio
import sys
import math
import wave
from pathlib import Path
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import numpy as np
import sip

#--------------------------------------------#
time = 5            # 計測時間[s]
samplerate = 44100  # サンプリングレート
fs = 1024           # フレームサイズ
index = 1           # マイクのチャンネル指標
#--------------------------------------------#


class Tab1Widget(QMainWindow):
    def __init__(self, parent=None):
        super(Tab1Widget, self).__init__()
        self.initUI()

    def initUI(self):
        self.flag = True
        self.data = []
        self.output = []
        setGraph(self)
        self.setWidget()

    def setWidget(self):
        self.button = QPushButton("録音開始")
        self.button.clicked.connect(self.clickButton)
        self.w = QWidget()
        layout = QHBoxLayout()
        layright = QVBoxLayout()
        layright.addWidget(self.button)
        layout.addWidget(self.pw)
        layout.addLayout(layright)
        self.w.setLayout(layout)
        self.setCentralWidget(self.w)

    def clickButton(self):
        recorde(self)

    def saveFile(self):
        file_name, _ = QFileDialog.getSaveFileName(self)
        if len(file_name) == 0:
            return
        print(file_name)
        file_name = str(Path(file_name).with_suffix(".wav"))
        wavFile = wave.open(file_name, 'wb')
        wavFile.setnchannels(1)
        wavFile.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wavFile.setframerate(samplerate)
        wfm = b"".join(self.output)
        wav = np.frombuffer(wfm, dtype="int16")
        wavFile.writeframes(wav)

    def recording(self):
        self.button.setText("録音中...")
        self.button.setEnabled(False)
        self.button.repaint()

    def recorded(self):
        self.button.setText("録音開始")
        self.button.setEnabled(True)
        self.button.repaint()


class Tab2Widget(QMainWindow):
    def __init__(self, parent=None):
        self.initUI()

    def initUI(self):
        self.flag = False
        self.data = []
        self.un = None
        self.on = None
        super(Tab2Widget, self).__init__()
        self.setAcceptDrops(True)
        self.w = QWidget()
        label = QLabel(self.w)
        label.setText('波形を表示するファイルをドロップしてください')
        label.setFont(QFont("ＭＳ ゴシック", 12, QFont.Black))
        label.setAlignment(Qt.AlignCenter)
        box = QVBoxLayout()
        box.addWidget(label)
        self.w.setLayout(box)
        self.setCentralWidget(self.w)

    def setWidget(self):
        label01 = QLabel(self.w)
        label01.setText('表示する下限周波数[Hz]')
        label02 = QLabel(self.w)
        label02.setText('表示する上限周波数[Hz]')
        underNum = QLineEdit()
        underNum.setValidator(QIntValidator())
        overNum = QLineEdit()
        overNum.setValidator(QIntValidator())
        underNum.textChanged.connect(self.textchangedUN)
        overNum.textChanged.connect(self.textchangedON)
        self.w = QWidget()
        layout = QHBoxLayout()
        under = QVBoxLayout()
        over = QVBoxLayout()
        layr = QVBoxLayout()
        under.addWidget(label01)
        under.addWidget(underNum)
        under.setContentsMargins(0, 0, 0, 20)
        over.addWidget(label02)
        over.addWidget(overNum)
        layr.addLayout(under)
        layr.addLayout(over)
        layr.addStretch(1)
        layout.addWidget(self.pw)
        layout.addLayout(layr)
        self.w.setLayout(layout)
        self.setCentralWidget(self.w)

    def dropEvent(self, event):
        event.accept()
        mimeData = event.mimeData()
        for url in mimeData.urls():
            self.path = url.toLocalFile()
            print(self.path)
        self.readWav()
        setGraph(self)
        self.setWidget()
        setData(self)

    def dragEnterEvent(self, event):
        event.accept()
        mimeData = event.mimeData()

    def textchangedUN(self, text):
        print(text)
        if text == "":
            self.un = None
        else:
            self.un = int(text)
        setData(self)

    def textchangedON(self, text):
        if text == "":
            self.on = None
        else:
            self.on = int(text)
        setData(self)

    def readWav(self):
        try:
            wr = wave.open(self.path, "r")
        except FileNotFoundError:  # ファイルが存在しなかった場合
            print("[Error 404] No such file or directory: " + FileName)
            return 0
        self.data = wr.readframes(wr.getnframes())
        wr.close()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()

    def initUI(self):
        tab = QTabWidget()
        tab.addTab(Tab1Widget(parent=self), '音声録音')
        tab.addTab(Tab2Widget(parent=self), '波形表示')
        self.w = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(tab)
        self.w.setLayout(hbox)
        self.setCentralWidget(self.w)

        self.setGeometry(300, 150, 800, 600)
        self.setWindowTitle('Recorder')
        self.setWindowIcon(QIcon('icon.png'))
        self.setMenu()
        self.show()

    def setWindow(self):
        QMessageBox.information(
            None, "Version", "Version 1.0\t\nMade by Kito", QMessageBox.Yes)

    def setMenu(self):
        exitAction = QAction(QIcon(''), '&Version', self)
        exitAction.triggered.connect(self.setWindow)
        menu = self.menuBar()
        fileMenu = menu.addMenu('&File')
        AboutMenu = menu.addMenu('&About')
        AboutMenu.addAction(exitAction)


def setGraph(self):
    self.pw = pg.PlotWidget(background=[0, 0, 0, 0])
    self.pw.showGrid(x=True, y=True)
    self.p1 = self.pw.plotItem
    self.p1.setLabels(bottom="時間[sec]",
                      left="音声強度[-]")
    self.setCentralWidget(self.pw)


def recorde(self):
    self.pa = pyaudio.PyAudio()
    self.stream = self.pa.open(format=pyaudio.paInt16, channels=index, rate=samplerate,
                               input=True, input_device_index=0, frames_per_buffer=fs)
    self.recording()

    self.prog = QProgressDialog('録音中...', 'キャンセル', 0, 100, self)
    self.prog.show()
    QApplication.processEvents()

    for i in range(0, int(samplerate / fs * time) + 1):
        frame = self.stream.read(fs)
        if i % 5 == 0:
            self.prog.setValue(
                math.ceil(i * 100 / (int(samplerate / fs * time) + 1)))
        self.data.append(frame)
        self.output.append(frame)

    self.recorded()
    self.prog.close()
    setData(self)
    self.stream.stop_stream()
    self.stream.close()
    self.pa.terminate()
    self.saveFile()
    self.data = []
    self.output = []


def setData(self):
    if self.flag:
        wfm = b"".join(self.data)
        wave = np.frombuffer(wfm, dtype="int16") / \
            float((np.power(2, 16) / 2) - 1)
        t = np.arange(0, len(wave))
        t = t * (fs / samplerate) / 1000
    else:
        wfm = self.data
        wave = np.fft.fft(np.frombuffer(wfm, dtype="int16") /
                          float((np.power(2, 16) / 2) - 1))
        wave = wave.real[:int(len(wave)/2)]
        size = len(wave)
        if self.un is None or self.on is None:
            for i in reversed(range(0, size)):
                if abs(wave[i]) > 1.0:
                    delete = i
                    break
            wave = np.delete(wave, np.s_[delete + 1:])
            t = np.arange(0, len(wave))
        elif self.un >= self.on:
            return
        else:

            wave = wave[self.un:self.on + 1]
            t = np.arange(self.un, self.on + 1)

    self.pw.clear()
    self.p1.addItem(pg.PlotCurveItem(x=t, y=wave,
                                     pen=pg.mkPen(
                                         color="r", style=Qt.SolidLine),
                                     antialias=True))
    self.pw.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
