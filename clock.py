import datetime


class Clock:
    def __init__(self):
        self._current_time = datetime.datetime.now().second
        self._seconds = 0
        self._minutes = 0

    def update_time(self):
        new_time = datetime.datetime.now().second
        if new_time != self._current_time:
            self._current_time = new_time
            self._seconds += 1
            if self._seconds == 60:
                self._seconds = 0
                self._minutes += 1
            return True
        return False

    def scoreboard_print(self) -> str:
        return f'{str(self._minutes).zfill(2)}:{str(self._seconds).zfill(2)}'
