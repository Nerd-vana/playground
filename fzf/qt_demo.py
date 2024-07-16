#!/usr/bin/env python3

import json
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QShortcut, QMainWindow, QSizePolicy
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QProcess, QTimer

subtitles_file = "subtitles.txt"
output_file = "timestamped_subtitles.txt"
mpv_socket = "/tmp/mpvsocket"
video_file = "video.mp4"

def send_mpv_command(command):
    cmd = f"echo '{json.dumps(command)}' | nc -U -w 1 {mpv_socket}"
    return subprocess.getoutput(cmd)

def get_mpv_time():
    response = send_mpv_command({"command": ["get_property", "time-pos"]})
    return json.loads(response)["data"]

def timestamp_subtitle(subtitle):
    time = get_mpv_time()
    with open(output_file, "a") as f:
        f.write(f"{time}|{subtitle}\n")

class MpvWidget(QWidget):
    def __init__(self, parent=None):
        super(MpvWidget, self).__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors, True)
        self.process = None

    def start_mpv(self):
        self.process = QProcess()
        self.process.start('mpv', [
            '--input-ipc-server={}'.format(mpv_socket),
            '--wid={}'.format(self.winId()),
            '--geometry=600x400+100+100',
            '--pause',
            video_file
        ])

class SubtitleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.subtitles = open(subtitles_file).readlines()
        self.current_index = 0
        self.status = "Ready"

        self.initUI()
        self.setup_shortcuts()
        self.mpv_widget.start_mpv()

    def initUI(self):
        self.setWindowTitle('Subtitle App')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.mpv_widget = MpvWidget(self)
        self.mpv_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.mpv_widget)

        self.subtitle_label = QLabel(self.get_subtitle_text(), self)
        self.status_label = QLabel(f"Status: {self.status} | Press Q to quit", self)

        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.status_label)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Q"), self).activated.connect(self.quit_app)
        QShortcut(QKeySequence("P"), self).activated.connect(self.toggle_pause)
        QShortcut(QKeySequence("T"), self).activated.connect(self.timestamp_current_subtitle)
        QShortcut(QKeySequence("B"), self).activated.connect(self.seek_back)
        QShortcut(QKeySequence("F"), self).activated.connect(self.seek_forward)
        QShortcut(QKeySequence(Qt.Key_Up), self).activated.connect(self.previous_subtitle)
        QShortcut(QKeySequence(Qt.Key_Down), self).activated.connect(self.next_subtitle)

    def quit_app(self):
        send_mpv_command({"command": ["quit"]})
        QApplication.instance().quit()

    def toggle_pause(self):
        send_mpv_command({"command": ["cycle", "pause"]})
        self.status = "Toggled pause"
        self.update_status()

    def timestamp_current_subtitle(self):
        subtitle = self.subtitles[self.current_index].strip()
        timestamp_subtitle(subtitle)
        self.status = f"Timestamped: {subtitle}"
        self.current_index = min(len(self.subtitles) - 1, self.current_index + 1)
        self.update_subtitle()
        self.update_status()

    def seek_back(self):
        send_mpv_command({"command": ["seek", -3]})
        self.status = "Seeked back 3 seconds"
        self.update_status()

    def seek_forward(self):
        send_mpv_command({"command": ["seek", 3]})
        self.status = "Seeked forward 3 seconds"
        self.update_status()

    def previous_subtitle(self):
        self.current_index = max(0, self.current_index - 1)
        self.update_subtitle()

    def next_subtitle(self):
        self.current_index = min(len(self.subtitles) - 1, self.current_index + 1)
        self.update_subtitle()

    def get_subtitle_text(self):
        return self.subtitles[self.current_index]

    def update_subtitle(self):
        self.subtitle_label.setText(self.get_subtitle_text())

    def update_status(self):
        self.status_label.setText(f"Status: {self.status} | Press Q to quit")

if __name__ == "__main__":
    app = QApplication([])
    ex = SubtitleApp()
    ex.show()
    app.exec_()
