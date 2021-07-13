from PyQt5 import QtCore, QtMultimedia, QtMultimediaWidgets, QtWidgets, QtGui

import sys


class PlayerWindow(QtWidgets.QMainWindow):
    def __init__(self, filepath=None, parent=None):
        super(PlayerWindow, self).__init__(parent)
        self.setWindowTitle('Видео-плеер')

        self.mediaPlayer = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)

        videoWidget = QtMultimediaWidgets.QVideoWidget()

        self.playButton = QtWidgets.QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QtWidgets.QLabel()
        self.errorLabel.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

        openAction = QtWidgets.QAction(QtGui.QIcon('open.png'), '&Открыть', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Отркыть видео')
        openAction.triggered.connect(self.openFile)

        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Закрыть', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из приложения')
        exitAction.triggered.connect(self.exitCall)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&Файл')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)

        controlLayout = QtWidgets.QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        if filepath:
            self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(filepath)))
            self.playButton.setEnabled(True)
            self.play()

    def openFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Отркыть видео', QtCore.QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.play()

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText('Ошибка: {}'.format(self.mediaPlayer.errorString()))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = PlayerWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())
