import PySimpleGUI as sg

from clock import *
from model import *
from webcam import *

# Get screen height to choose size for canvas
# root = tk.Tk()
# screensize = root.winfo_screenheight()
# root.destroy()


# ---- Params ---- #
APP_NAME = 'basketball-scorekeeper'
CAMERAS_INDEXES = ('http://192.168.1.164:4747/video?640x480', 0)
# CAMERA_IP = 'http://172.29.96.149:4747/video?640x480'
# CAMERA_INDEX = 0

SKIP = 10

# ---- Machine States Enums ---- #
STATE_BALL_ABOVE_BASKET = 0
STATE_BALL_IN_BASKET = 1
STATE_BALL_MISSED_BASKET = 2
STATE_BALL_UNDER_BASKET = 3
STATE_NO_BALL = 4

# ---- Messages ---- #
TXT_PLAY = 'Play'
TXT_PAUSE = 'Pause'
TXT_RESET_TIMER = 'Reset timer'
TXT_RESET_SCORE = 'Reset score'
TXT_SETTINGS = 'Settings'
TXT_LOAD_MODEL = 'Load Model'
TXT_LOAD_WEBCAM = 'Load Webcam'
TXT_TIMER_START = '00:00'
TXT_START_SCORE = '0'

# ---- Error Messages ---- #
ERROR_TXT_LOAD_WEBCAM_FAILED = "Failed to load camera!"
ERROR_TXT_LOAD_MODEL_FAILED = "Failed to load model!"


def runGUI(layout: list) -> None:
    # Create the Window
    window = sg.Window(APP_NAME, layout)

    cam = None
    trained_model = None

    webcam_is_loaded = False
    model_is_loaded = False

    clock_is_running = False
    board_clock = Clock()

    team_scores = [0, 0]
    in_basket = 0
    skip = 0

    # Event Loop to process 'events' and get the 'values' of the inputs
    while True:
        event, values = window.read(timeout=1)

        # Video handling. We only predict one every {SKIP} frames,
        # but still show every frame on the screen
        skip = (skip + 1) % SKIP
        if webcam_is_loaded:
            frame_array, image_bytes = capture_frame(cam)
            window["img_webcam"].update(data=image_bytes)

            if model_is_loaded and skip == 0:
                curr_prediction = predict(frame_array, trained_model)

                if curr_prediction == STATE_BALL_IN_BASKET:
                    in_basket += 1
                else:
                    if in_basket >= 2:
                        team_scores[0] += 2
                        window["txt_team_a_score"].update(team_scores[0])
                    in_basket = 0

        # Time handling. Expect update_time() to be called only if clock_is_running
        if clock_is_running and board_clock.update_time():
            window["txt_time"].update(board_clock.scoreboard_print())

        if event == "btn_play_pause":
            clock_is_running = not clock_is_running
            window["btn_reset_timer"].update(disabled=clock_is_running)
            window["btn_reset_score"].update(disabled=clock_is_running)
            window["btn_play_pause"].update(TXT_PAUSE if clock_is_running else TXT_PLAY)

        elif event == "btn_reset_timer":
            window["txt_time"].update(TXT_TIMER_START)
            window["btn_play_pause"].update(TXT_PLAY)
            window["btn_reset_timer"].update(disabled=True)

            clock_is_running = False
            board_clock = Clock()

        elif event == "btn_reset_score":
            window["btn_reset_score"].update(disabled=True)
            team_scores = [0, 0]

        # Webcam handling
        elif event == "btn_load_webcam":
            cam = load_webcam(CAMERAS_INDEXES[1])
            if cam is not None:
                window["btn_load_webcam"].update(disabled=True)
                webcam_is_loaded = True
            else:
                sg.popup(ERROR_TXT_LOAD_WEBCAM_FAILED, background_color='firebrick')

        # Model handling
        elif event == "btn_load_model":
            trained_model = load_model(PEN_MODEL)
            if trained_model is not None:
                window["btn_play_pause"].update(disabled=False)
                window["btn_load_model"].update(disabled=True)
                model_is_loaded = True
            else:
                sg.popup(ERROR_TXT_LOAD_MODEL_FAILED, background_color='firebrick')

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
            sg.Button(key="btn_load_model", button_text=TXT_LOAD_MODEL)
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
        [sg.Image(key='img_webcam', filename='', size=(640, 480))],
        [sg.HorizontalSeparator()],
        [
            sg.Button(key="btn_play_pause", button_text=TXT_PLAY),
            sg.Button(key="btn_reset_timer", button_text=TXT_RESET_TIMER, disabled=True),
            sg.Button(key="btn_reset_score", button_text=TXT_RESET_SCORE, disabled=True),
            sg.Button(key="btn_settings", button_text=TXT_SETTINGS)
        ]
    ]

    runGUI(layout)
