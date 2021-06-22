from gui import *

if __name__ == '__main__':
    # List of themes:
    # https://user-images.githubusercontent.com/46163555/70382042-796da500-1923-11ea-8432-80d08cd5f503.jpg
    sg.theme('DarkBlack1')

    layout = [
        [
            sg.Button(key=f"btn_load_webcam_{A}", button_text=TXT_LOAD_WEBCAM_A),
            sg.Button(key=f"btn_load_webcam_{B}", button_text=TXT_LOAD_WEBCAM_B),
            sg.Button(key="btn_load_model", button_text=TXT_LOAD_MODEL)
        ],
        [sg.HorizontalSeparator()],
        [sg.Text(key="txt_time", text=TXT_TIMER_START, font=('Consolas', 30),
                 size=(59, 1), justification='center')],
        [sg.HorizontalSeparator()],
        [
            sg.Text(key=f"txt_team_score_{A}", text=TXT_START_SCORE, font=('Consolas', 45),
                    size=(19, 1), justification='center'),
            sg.VerticalSeparator(),
            sg.Text(key=f"txt_team_score_{B}", text=TXT_START_SCORE, font=('Consolas', 45),
                    size=(19, 1), justification='center')
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Image(key=f"img_webcam_{A}", filename='', size=(640, 480), background_color='gray15'),
            # sg.VerticalSeparator(),
            sg.Image(key=f"img_webcam_{B}", filename='', size=(640, 480), background_color='gray15')
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button(key="btn_play_pause", button_text=TXT_PLAY),
            sg.Button(key="btn_reset_timer", button_text=TXT_RESET_TIMER, disabled=True),
            sg.Button(key="btn_reset_score", button_text=TXT_RESET_SCORE, disabled=True),
            sg.Button(key="btn_settings", button_text=TXT_SETTINGS)
        ]
    ]

    run_gui(layout)
