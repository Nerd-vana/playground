#!/usr/bin/env python3

import json
import subprocess
import sys
import os
import termios
import atexit
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, QEvent

subtitles_file = "subtitles.txt"
output_file = "timestamped_subtitles.txt"
mpv_socket = "/tmp/mpvsocket"

# Save the terminal settings
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

def reset_terminal():
    # Restore the terminal settings
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Register the reset_terminal function to be called when the script exits
atexit.register(reset_terminal)

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

class SubtitleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.subtitles = open(subtitles_file).readlines()
        self.current_index = 0
        self.status = "Ready"
        self.initUI()
        self.start_mpv()

    def initUI(self):
        self.setWindowTitle('Subtitle Timestamper')
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.subtitle_text = QTextEdit()
        self.subtitle_text.setReadOnly(True)
        layout.addWidget(self.subtitle_text)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        central_widget.setLayout(layout)

        self.update_display()

        self.installEventFilter(self)

        self.show()

    def start_mpv(self):
        mpv_command = "mpv --osd-level=3 --osd-fractions --osd-status-msg='${time-pos} / ${duration}' --input-ipc-server=/tmp/mpvsocket --geometry=1200+100+50 --osd-fractions --pause video.mp4"
        subprocess.Popen(mpv_command, shell=True)

    def update_display(self):
        self.subtitle_text.setText(self.subtitles[self.current_index])
        self.status_label.setText(f"Status: {self.status} | Press Q to quit")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            self.handle_key_press(event)
            return True
        return super().eventFilter(obj, event)

    def handle_key_press(self, event):
        key = event.key()
        if key == Qt.Key_Q:
            send_mpv_command({"command": ["quit"]})
            self.close()
        elif key == Qt.Key_P:
            send_mpv_command({"command": ["cycle", "pause"]})
            self.status = "Toggled pause"
        elif key == Qt.Key_T:
            timestamp_subtitle(self.subtitles[self.current_index].strip())
            self.status = f"Timestamped: {self.subtitles[self.current_index].strip()}"
            self.current_index = min(len(self.subtitles) - 1, self.current_index + 1)
        elif key == Qt.Key_B:
            send_mpv_command({"command": ["seek", -3]})
            self.status = "Seeked back 3 seconds"
        elif key == Qt.Key_F:
            send_mpv_command({"command": ["seek", 3]})
            self.status = "Seeked forward 3 seconds"
        elif key == Qt.Key_Up:
            self.current_index = max(0, self.current_index - 1)
        elif key == Qt.Key_Down:
            self.current_index = min(len(self.subtitles) - 1, self.current_index + 1)
        
        self.update_display()

    def closeEvent(self, event):
        reset_terminal()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SubtitleApp()
    sys.exit(app.exec_())