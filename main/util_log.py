import datetime
import time
import os
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
from PyQt5.QtGui import QColor

class UtilLog():
    def __init__(self, log_monitor: QTableWidget) -> None:
        self.log_monitor = log_monitor

    # 시스템 로그 추가 함수
    def add_log(self, message, color = None):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_position = self.log_monitor.rowCount()
        self.log_monitor.insertRow(row_position)
        log_time = QTableWidgetItem(current_time)
        log_msg = QTableWidgetItem(message)
        
        if color:
            log_time.setForeground(QColor(color))
            log_msg.setForeground(QColor(color))

        self.log_monitor.setItem(row_position, 0, log_time)
        self.log_monitor.setItem(row_position, 1, log_msg)
        self.log_monitor.scrollToBottom()
        time.sleep(0.01)

        # 현재 시간과 로그 메시지 예시
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 연도 및 월별 디렉토리 경로 생성
        log_dir = "logs/{year}-{month}".format(
            year=datetime.datetime.now().strftime("%Y"),
            month=datetime.datetime.now().strftime("%m")
        )

        # 디렉토리가 없는 경우 생성
        os.makedirs(log_dir, exist_ok=True)

        # 로그 파일 이름 생성 (sys_log_YYYY-MM-DD.log 형식)
        log_name = "sys_log_" + datetime.datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(log_dir, f"{log_name}.log")

        # 로그 메시지 파일에 추가
        with open(log_file_path, "a", encoding='utf-8') as log_file:
            log_file.write(f"{current_time} - {message}\n")