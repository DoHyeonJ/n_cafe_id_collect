from PyQt5.QtCore import QThread, pyqtSignal
from util_log import UtilLog
from api import Api
import time, traceback
import logging

class TaskThread(QThread):
    progress_update = pyqtSignal(int)  # 프로그레스바 업데이트를 위한 시그널
    task_finished = pyqtSignal()       # 작업 완료 시그널
    error_occurred = pyqtSignal(str)   # 에러 발생 시그널

    def __init__(self, api: Api, util_log: UtilLog, collect_params):
        super().__init__()
        self.api = api
        self.util_log = util_log
        self.collect_params = collect_params

    def run(self):
        try:
            self.util_log.add_log("계정 수집을 실행합니다.", "blue")

            # 수집할 게시글 수에 비례한 시간 계산
            board_collect_count = int(self.collect_params["board_collect_count"])
            total_steps = board_collect_count
            sleep_time_per_step = 0.3

            # 작업을 실행하며 진행 상태 업데이트
            for i in range(1, total_steps + 1):
                time.sleep(sleep_time_per_step)  # 가상의 작업을 위해 대기 시간 추가
                progress = int((i / total_steps) * 100)
                self.progress_update.emit(progress)  # 프로그레스 업데이트

            # API 초기화
            cafe_id = self.collect_params["cafe_id"]
            board_id = self.collect_params["board_id"]
            self.api.cafe_id = cafe_id
            self.api.board_id = board_id
            self.api.board_collect_count = board_collect_count

            self.api.run(**self.collect_params["options"])
            self.progress_update.emit(100)
            self.util_log.add_log("계정 수집이 완료되었습니다.", "blue")
            self.task_finished.emit()

        except Exception as e:
            error_message = f"execute_task 오류 발생(재실행 필요): {str(e)}"
            self.util_log.add_log(error_message, "red")
            logging.error(f"execute_task 오류 발생: {traceback.format_exc()}")
            self.error_occurred.emit(error_message)