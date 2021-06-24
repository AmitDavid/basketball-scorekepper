import PySimpleGUI as sg

from basketmodel import BasketModel, load_model
from clock import Clock
from webcam import Webcam

# ---- Params ---- #
CAMERAS = {
    'local_0': 0,
    'local_1': 1,
    'Amit': 'http://192.168.1.164:4747/video?640x480',
    'HUJI_guests': 'http://172.29.113.83:4747/video?640x480',
    'Ben': 'http://192.168.31.113:4747/video?640x480'
}
SELECTED_CAMERAS = (CAMERAS['local_0'], CAMERAS['Ben'])

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


def run_gui(window: sg.Window) -> None:
    trained_model = None
    webcams = [None, None]
    model = [None, None]
    team_scores = [0, 0]

    clock_is_running = False
    board_clock = Clock()

    # Event Loop to process 'events' and get the 'values' of the inputs
    while True:
        event, values = window.read(timeout=10)

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
            board_clock.reset()

        elif event == "btn_reset_score":
            window["btn_reset_score"].update(disabled=True)
            window[f"txt_team_score_{A}"].update(TXT_START_SCORE)
            window[f"txt_team_score_{B}"].update(TXT_START_SCORE)
            team_scores = [0, 0]

        # Webcam handling
        elif event in {f"btn_load_webcam_{A}", f"btn_load_webcam_{B}"}:
            team = int(event[-1])
            webcams[team] = Webcam(SELECTED_CAMERAS[team])
            if webcams[team].is_webcam_works():
                window[f"btn_load_webcam_{team}"].update(disabled=True)
                model[team] = BasketModel(trained_model, webcams[team])
            else:
                webcams[team] = None
                sg.popup(ERROR_TXT_LOAD_WEBCAM_FAILED, background_color='firebrick')

        # Model handling
        elif event == "btn_load_model":
            trained_model = load_model()
            if trained_model is not None:
                window[f"btn_load_webcam_{A}"].update(disabled=False)
                window[f"btn_load_webcam_{B}"].update(disabled=False)
                window["btn_play_pause"].update(disabled=False)
                window["btn_load_model"].update(disabled=True)
            else:
                trained_model = None
                sg.popup(ERROR_TXT_LOAD_MODEL_FAILED, background_color='firebrick')

        # Close the program
        elif event == sg.WIN_CLOSED:
            return

        # Time handling. Expect update_time() to be called only if clock_is_running
        if clock_is_running and board_clock.update_time():
            window["txt_time"].update(board_clock.scoreboard_print())

        # Video handling.
        for team in TEAMS:
            if webcams[team] is not None:
                window[f"img_webcam_{team}"].update(data=webcams[team].get_image_bytes())
                score_buffer = model[team].get_score_buffer()
                if score_buffer:
                    team_scores[team] += score_buffer
                    window[f"txt_team_score_{team}"].update(team_scores[team])
