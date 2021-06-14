import datetime
import cv2
from webcam import *
from model import *

import PySimpleGUI as sg

# Get screen height to choose size for canvas
# root = tk.Tk()
# screensize = root.winfo_screenheight()
# root.destroy()

APP_NAME = 'basketball-scorekeeper'

TXT_PLAY = 'Play'
TXT_PAUSE = 'Pause'
TXT_RESET_TIMER = 'Reset timer'
TXT_RESET_SCORE = 'Reset score'
TXT_SETTINGS = 'Settings'
TXT_LOAD_MODEL = 'Load Model'
TXT_LOAD_WEBCAM = 'Load Webcam'
TXT_TIMER_START = '00:00'
TXT_START_SCORE = '0'


def runGUI(layout: list) -> None:
    # Create the Window
    window = sg.Window(APP_NAME, layout)

    webcam_is_loaded = False
    model_is_loaded = False

    clock_is_running = False
    current_time = datetime.datetime.now().second
    seconds = 0
    minutes = 0

    score_team_a = 0
    score_team_a = 0

    # Event Loop to process 'events' and get the 'values' of the inputs
    while True:
        event, values = window.read(timeout=1)

        # Video handling
        if webcam_is_loaded:
            # Read image from capture device (camera)
            frame = capture_image(cam)
            # Convert the image to PNG Bytes
            image_bytes = cv2.imencode('.png', frame)[1].tobytes()
            # Show in app
            window["img_webcam"].update(data=image_bytes)

        # Time handling
        new_time = datetime.datetime.now().second
        if clock_is_running and new_time != current_time:
            current_time = new_time
            seconds += 1
            if seconds == 60:
                seconds = 0
                minutes += 1
            window["txt_time"].update(f'{str(minutes).zfill(2)}:{str(seconds).zfill(2)}')

        if event == "btn_play_pause":
            clock_is_running = not clock_is_running
            window["btn_reset_timer"].update(disabled=clock_is_running)
            if clock_is_running:
                window["btn_play_pause"].update(TXT_PAUSE)
            else:
                window["btn_play_pause"].update(TXT_PLAY)

        elif event == "btn_reset_timer":
            window["txt_time"].update(TXT_TIMER_START)
            window["btn_play_pause"].update(TXT_PLAY)

            clock_is_running = False
            current_time = datetime.datetime.now().second
            seconds = 0
            minutes = 0

        # Webcam handling
        elif event == "btn_load_webcam":
            cam = load_camera('http://192.168.1.164:4747/video?640x480')
            window["btn_load_model"].update(disabled=False)
            window["btn_load_webcam"].update(disabled=True)
            webcam_is_loaded = True

        # Model handling
        elif event == "btn_load_model":

            trained_model = load_model(PEN_MODEL)
            window["btn_play_pause"].update(disabled=False)
            window["btn_load_model"].update(disabled=True)
            model_is_loaded = True

        # Close the program
        elif event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    # List of themes:
    # https://user-images.githubusercontent.com/46163555/70382042-796da500-1923-11ea-8432-80d08cd5f503.jpg
    sg.theme('DarkBlack1')

    layout = [
        [
            sg.Button(key="btn_load_webcam", button_text=TXT_LOAD_WEBCAM),
            sg.Button(key="btn_load_model", button_text=TXT_LOAD_MODEL, disabled=True)
        ],
        [sg.HorizontalSeparator()],
        [sg.Text(key="txt_time", text=TXT_TIMER_START, font=('Consolas', 30),
                 size=(29, 1), justification='center')],
        [sg.HorizontalSeparator()],
        [
            sg.Text(key="txt_team_a_score", text=TXT_START_SCORE, font=('Consolas', 45),
                    size=(9, 1), justification='center'),
            sg.VerticalSeparator(),
            sg.Text(key="txt_team_b_score", text=TXT_START_SCORE, font=('Consolas', 45),
                    size=(9, 1), justification='center')
        ],
        [sg.HorizontalSeparator()],
        [sg.Image(filename='', key='img_webcam', size=(640, 480))],
        [sg.HorizontalSeparator()],
        [
            sg.Button(key="btn_play_pause", button_text=TXT_PLAY),  # , disabled=True),
            sg.Button(key="btn_reset_timer", button_text=TXT_RESET_TIMER, disabled=True),
            sg.Button(key="btn_reset_score", button_text=TXT_RESET_SCORE, disabled=True),
            sg.Button(key="btn_settings", button_text=TXT_SETTINGS)
        ]
    ]

    runGUI(layout)
