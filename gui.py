import PySimpleGUI as sg

from clock import *
from webcam import *

# ---- Params ---- #
APP_NAME = 'basketball-scorekeeper'

CAMERAS = {
    'local_0': 0,
    'local_1': 1,
    'Amit': 'http://192.168.1.164:4747/video?640x480',
    'HUJI_guests': 'http://172.29.96.149:4747/video?640x480',
    'Ben': 'http://192.168.31.113:4747/video?640x480'
}
SELECTED_CAMERAS = (CAMERAS['local_0'], CAMERAS['Amit'])

# ---- Machine States Enums ---- #
STATE_BALL_ABOVE_BASKET = 0
STATE_BALL_IN_BASKET = 1
STATE_BALL_MISSED_BASKET = 2
STATE_BALL_UNDER_BASKET = 3
STATE_NO_BALL = 4

# ---- Teams Enums ---- #
A = 0
B = 1
TEAMS = {A, B}

# ---- Messages ---- #
TXT_PLAY = 'Play'
TXT_PAUSE = 'Pause'
TXT_RESET_TIMER = 'Reset timer'
TXT_RESET_SCORE = 'Reset score'
TXT_SETTINGS = 'Settings'
TXT_LOAD_MODEL = 'Load Model'
TXT_LOAD_WEBCAM_A = 'Load Webcam A'
TXT_LOAD_WEBCAM_B = 'Load Webcam B'
TXT_TIMER_START = '00:00'
TXT_START_SCORE = '0'

# ---- Error Messages ---- #
ERROR_TXT_LOAD_WEBCAM_FAILED = "Failed to load camera!"
ERROR_TXT_LOAD_MODEL_FAILED = "Failed to load model!"


def run_gui(layout: list) -> None:
    # Create the Window
    window = sg.Window(APP_NAME, layout)

    cam = [None, None]
    trained_model = None

    webcam_is_loaded = [False, False]
    model_is_loaded = False

    clock_is_running = False
    board_clock = Clock()

    team_scores = [0, 0]
    cycles_in_basket = [0, 0]

    # Event Loop to process 'events' and get the 'values' of the inputs
    while True:
        event, values = window.read(timeout=10)

        # Video handling.
        for team in TEAMS:
            if webcam_is_loaded[team]:
                window[f"img_webcam_{team}"].update(data=cam[team].get_image_bytes())

                if model_is_loaded:
                    curr_prediction = predict(cam[team].get_frame_array(), trained_model)

                    if curr_prediction == STATE_BALL_IN_BASKET:
                        cycles_in_basket += 1
                    else:
                        if cycles_in_basket[team] >= 2:
                            team_scores[team] += 2
                            window[f"txt_team_score_{team}"].update(team_scores[0])
                        cycles_in_basket[team] = 0

        # Time handling. Expect update_time() to be called only if clock_is_running
        if clock_is_running and board_clock.update_time():
            window["txt_time"].update(board_clock.scoreboard_print())

        # GUI buttons
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
        elif event == f"btn_load_webcam_{A}":
            cam[A] = Webcam(SELECTED_CAMERAS[A])
            if cam[A].is_webcam_works():
                window[f"btn_load_webcam_{A}"].update(disabled=True)
                webcam_is_loaded[A] = True
            else:
                sg.popup(ERROR_TXT_LOAD_WEBCAM_FAILED, background_color='firebrick')

        # Webcam handling
        elif event == f"btn_load_webcam_{B}":
            cam[B] = Webcam(SELECTED_CAMERAS[B])
            if cam[B].is_webcam_works():
                window[f"btn_load_webcam_{B}"].update(disabled=True)
                webcam_is_loaded[B] = True
            else:
                sg.popup(ERROR_TXT_LOAD_WEBCAM_FAILED, background_color='firebrick')

        # Model handling
        elif event == "btn_load_model":
            trained_model = load_model()
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
