#!/usr/bin/env python3

import json
import subprocess
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

subtitles_file = "subtitles.txt"
output_file = "timestamped_subtitles.txt"
mpv_socket = "/tmp/mpvsocket"

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

class SubtitleApp:
    def __init__(self):
        self.subtitles = open(subtitles_file).readlines()
        self.current_index = 0
        self.status = "Ready"

        self.kb = KeyBindings()
        self.setup_keybindings()

        self.layout = Layout(
            HSplit([
                Window(FormattedTextControl(self.get_subtitle_text), height=1),
                Window(FormattedTextControl(self.get_status_text), height=1),
            ])
        )

        self.app = Application(layout=self.layout, key_bindings=self.kb, full_screen=True)

    def setup_keybindings(self):
        @self.kb.add('q')
        def _(event):
            send_mpv_command({"command": ["quit"]})            
            event.app.exit()

        @self.kb.add('p')
        def _(event):
            send_mpv_command({"command": ["cycle", "pause"]})
            self.status = "Toggled pause"

        @self.kb.add('t')
        def _(event):
            timestamp_subtitle(self.subtitles[self.current_index].strip())
            self.status = f"Timestamped: {self.subtitles[self.current_index].strip()}"
            self.current_index = min(len(self.subtitles) - 1, self.current_index + 1)

        @self.kb.add('b')
        def _(event):
            send_mpv_command({"command": ["seek", -3]})
            self.status = "Seeked back 3 seconds"

        @self.kb.add('f')
        def _(event):
            send_mpv_command({"command": ["seek", 3]})
            self.status = "Seeked forward 3 seconds"

        @self.kb.add('up')
        def _(event):
            self.current_index = max(0, self.current_index - 1)

        @self.kb.add('down')
        def _(event):
            self.current_index = min(len(self.subtitles) - 1, self.current_index + 1)

    def get_subtitle_text(self):
        return self.subtitles[self.current_index]

    def get_status_text(self):
        return f"Status: {self.status} | Press q to quit"

    def run(self):
        self.app.run()

if __name__ == "__main__":
    SubtitleApp().run()