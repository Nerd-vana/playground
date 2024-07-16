#!/usr/bin/env python3

import json
import subprocess
import sys
import os
import termios
import atexit
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QShortcut
from PyQt5.QtGui import QKeySequence, QTextCursor, QTextCharFormat, QColor, QTextOption
from PyQt5.QtCore import Qt

subtitles_file = "subtitles.txt"
output_file = "timestamped_subtitles.txt"
mpv_socket = "/tmp/mpvsocket"
video_file = "video.mp4"

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

def start_mpv():
    mpv_width = 1000
    mpv_x = 1400
    mpv_y = 200
    mpv_command = [
        "mpv",
        "--osd-level=3",
        "--osd-fractions",
        "--osd-status-msg='${time-pos} / ${duration}'",
        f"--input-ipc-server={mpv_socket}",
        f"--geometry={mpv_width}+{mpv_x}+{mpv_y}",
        "--pause",
        video_file
    ]
    subprocess.Popen(mpv_command)

class SubtitleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.subtitles = open(subtitles_file).readlines()
        self.current_index = 0
        self.status = "Ready"

        self.initUI()
        self.setup_shortcuts()
        start_mpv()

    def initUI(self):
        self.setWindowTitle('Subtitle App')

        # Define the top-left corner coordinates
        top_left_x = 50
        top_left_y = 100

        # Calculate the width and height to occupy half of the screen from the top-left corner
        width = (screen_width // 2) - top_left_x - 50
        height = 500

        # Set the geometry to start at (100, 50) and adjust width and height
        self.setGeometry(top_left_x, top_left_y, width, height)

        self.layout = QVBoxLayout()

        self.subtitle_text = QTextEdit(self)
        self.subtitle_text.setReadOnly(True)
        self.subtitle_text.setText("".join(self.subtitles))
        self.subtitle_text.setWordWrapMode(QTextOption.NoWrap)  # Disable word wrapping
        self.subtitle_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Enable horizontal scrolling
        self.subtitle_text.setFixedHeight(height - 100)  # Adjust height to fit the window
        self.subtitle_text.setFixedWidth(width - 20)  # Adjust width to fit the window

        self.status_label = QLabel(f"Status: {self.status} | Press Q to quit", self)
        self.status_label.setWordWrap(True)  # Enable word wrapping for the status label
        self.status_label.setFixedWidth(width - 20)  # Adjust width to fit the window

        self.layout.addWidget(self.subtitle_text)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

        self.update_subtitle()

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
        return "".join(self.subtitles)

    def update_subtitle(self):
        self.subtitle_text.setText("".join(self.subtitles))

        # Clear formatting
        cursor = self.subtitle_text.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())

        # Highlight the current subtitle
        cursor = self.subtitle_text.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(self.current_index):
            cursor.movePosition(QTextCursor.Down)

        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor("yellow"))
        cursor.setCharFormat(fmt)

        self.subtitle_text.setTextCursor(cursor)

        # Reset horizontal scroll to left
        self.subtitle_text.horizontalScrollBar().setValue(0)

    def update_status(self):
        self.status_label.setText(f"Status: {self.status} | Press Q to quit")

if __name__ == "__main__":
    app = QApplication([])

    # Get screen dimensions
    screen_geometry = QApplication.desktop().screenGeometry()
    global screen_width, screen_height
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    ex = SubtitleApp()
    ex.show()
    # Reset horizontal scroll to left at startup
    ex.subtitle_text.horizontalScrollBar().setValue(0)
    app.exec_()
