import os
import tkinter as tk
from time import time

import PySimpleGUI as sg

# Get screen height to choose size for canvas
root = tk.Tk()
screensize = root.winfo_screenheight()
root.destroy()
GRAPH_SIZE = screensize - 300

APP_NAME = 'basketball-scorekeeper'

def runGUI(layout):
    """
    Runs the GUI.
    :param layout:
    """
    # Create the Window
    window = sg.Window(APP_NAME, layout)

    # Event Loop to process 'events' and get the 'values' of the inputs
    while True:
        event, values = window.read()

        # If user closes window, close the program
        if event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    # List of themes:
    # https://user-images.githubusercontent.com/46163555/70382042-796da500-1923-11ea-8432-80d08cd5f503.jpg

    # Needs to be first line of code for all elements to get this theme
    sg.theme('DarkBlack1')

    # Current GUI layout

    # ----------------
    # |   | time |   |
    # |--------------|
    # |      ||      |
    # |  0   ||   0  |
    # |      ||      |
    # ----------------
    # | play || sett |
    # ----------------

    layout = [
        [sg.Text(key='txt_time', text='00:00')],
        [sg.HorizontalSeparator()],
        [
            sg.Text(key='txt_team_a_score', text='0'),
            sg.VerticalSeparator(),
            sg.Text(key='txt_team_b_score', text='0')
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button(key='btn_play_pause', button_text='Play'),
            sg.Button(key='btn_settings', button_text='Pause')
        ]
    ]

    runGUI(layout)
