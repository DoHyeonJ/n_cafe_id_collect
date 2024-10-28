import sys
import traceback
import logging
from task_thread import TaskThread
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QDateTimeEdit, QSpinBox, QRadioButton, QGroupBox, QCheckBox, QButtonGroup, QFileDialog, QTableWidget, QMessageBox, QProgressBar
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import Qt
from util_log import UtilLog
from util_licence import UtilLicence
from api import Api

class MyApp(QWidget):
    def __init__(self):
        self.util_licence = UtilLicence()
        self.group_width = 630
        self.util_log = None
        self.is_login = False
        self.is_start = False
        self.cafe_list = None
        self.cafe_id = None
        self.cafe_url = None
        self.api = Api()
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set font
        font = QFont("Arial", 10)
        self.setFont(font)
        
        # Set stylesheet for a modern look similar to the provided image
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #bfbfbf;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QTextEdit, QDateTimeEdit, QSpinBox {
                background-color: #3c3f41;
                border: 1px solid #4a4a4a;
                padding: 8px;
                border-radius: 4px;
                color: #dcdcdc;
            }
            QPushButton, QRadioButton, QCheckBox {
                background-color: #3c3f41;
                color: white;
                border: 1px solid #5c5c5c;
                padding: 10px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover, QRadioButton:hover, QCheckBox:hover {
                background-color: #4a4a4a;
            }
            QPushButton#execute {
                background-color: #4CAF50;
            }
            QPushButton#execute:hover {
                background-color: #45a049;
            }
            QPushButton#stop {
                background-color: #f44336;
            }
            QPushButton#stop:hover {
                background-color: #e53935;
            }
            QLabel {
                color: #dcdcdc;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                margin-top: 5px;
                margin-bottom: 5px;
                padding: 10px;
            }
            QComboBox {
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px;
                color: #dcdcdc;
                width: 200px;
            }
            QPushButton#login_btn {
                background-color: #4CAF50;
            }
            QPushButton#login_btn:hover {
                background-color: #45a049;
            }
            QProgressBar {
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                background-color: #3c3f41;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 1px;
            }
        """)

        # Create widgets
        self.id_label = QLabel('ID')
        self.id_input = QLineEdit()
        self.id_input.setFixedHeight(40)
        
        self.pw_label = QLabel('PW')
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setFixedHeight(40)

        self.toggle_button = QPushButton('비밀번호 보기')
        self.toggle_button.setCheckable(True)
        self.toggle_button.toggled.connect(self.toggle_password_visibility)
        
        self.login_button = QPushButton('로그인')
        self.login_button.clicked.connect(self.check_login)
        self.login_button.setObjectName("login_btn")

        self.cafe_list_label = QLabel('카페 목록')
        self.cafe_list_combo = QComboBox()
        self.cafe_list_combo.setFixedHeight(35)
        self.cafe_list_combo.setMinimumWidth(280)
        self.cafe_url_chech_btn = QPushButton('게시판 추출')
        self.cafe_url_chech_btn.clicked.connect(self.collect_category_list)

        self.category_label = QLabel('게시판 종류')
        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(35)
        self.category_combo.setMinimumWidth(280)

        self.category_count_label = QLabel('수집 게시글 수')
        self.category_count_spinbox = QSpinBox()
        self.category_count_spinbox.setRange(1, 1000)  # 최소값과 최대값 설정
        self.category_count_spinbox.setSingleStep(1)  # 증가/감소 스텝 설정
        self.category_count_spinbox.setFixedHeight(35)
        self.category_count_spinbox.setMaximumWidth(100)
        self.is_collect_comment = QCheckBox("댓글 작성자 포함 수집")

        self.collect_kind_label = QLabel("수집 항목")
        self.collect_type_id = QCheckBox("아이디")
        self.collect_type_email = QCheckBox("이메일")
        self.collect_type_nickname = QCheckBox("닉네임")
        self.collect_type_title = QCheckBox("제목")
        self.collect_type_content = QCheckBox("내용")
        self.collect_type_comment = QCheckBox("댓글내용")
        
        self.collect_type_id.setChecked(True)

        self.log_monitor_label = QLabel('작업로그 모니터')
        self.log_monitor = QTableWidget(0, 2)  # 0 rows, 2 columns
        self.log_monitor.setHorizontalHeaderLabels(["Timestamp", "Log Message"])
        self.log_monitor.horizontalHeader().setStretchLastSection(True)
        self.log_monitor.setColumnWidth(0, 160)

        # Add border to header
        self.log_monitor.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; border: 1px solid #4a4a4a; padding: 4px; }")
        self.log_monitor.verticalHeader().setStyleSheet("QHeaderView::section { color: black; border: 1px solid #4a4a4a; padding: 4px; }")
        # Hide vertical header (row numbers)
        self.log_monitor.verticalHeader().setVisible(False)

        self.execute_button = QPushButton('계정 수집 실행')
        self.execute_button.setFixedHeight(40)
        self.execute_button.setObjectName('execute')

        self.setting_init_button = QPushButton('초기화')
        self.setting_init_button.setFixedHeight(40)
        self.setting_init_button.setObjectName('setting_init')

        self.execute_button.clicked.connect(self.execute_task)
        self.setting_init_button.clicked.connect(self.init_settings)

        # Grouping widgets
        id_pw_group = QGroupBox()
        id_pw_group.setMaximumWidth(self.group_width)
        id_pw_layout = QVBoxLayout()
        id_pw_input_layout = QHBoxLayout()
        id_pw_input_layout.addWidget(self.id_label)
        id_pw_input_layout.addWidget(self.id_input)
        id_pw_input_layout.addWidget(self.pw_label)
        id_pw_input_layout.addWidget(self.pw_input)
        id_pw_input_layout.addWidget(self.toggle_button)
        id_pw_input_layout.addWidget(self.login_button)
        id_pw_layout.addLayout(id_pw_input_layout)
        
        cafe_list_layout = QHBoxLayout()
        cafe_list_layout.addWidget(self.cafe_list_label, stretch=1)
        cafe_list_layout.addWidget(self.cafe_list_combo, stretch=6)
        cafe_list_layout.addWidget(self.cafe_url_chech_btn, stretch=1)
        id_pw_layout.addLayout(cafe_list_layout)

        category_layout = QHBoxLayout()
        category_layout.addWidget(self.category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(self.category_count_label)
        category_layout.addWidget(self.category_count_spinbox)
        id_pw_layout.addLayout(category_layout)
        
        collect_kind_label_layout = QHBoxLayout()
        collect_kind_label_layout.addWidget(self.collect_kind_label)
        id_pw_layout.addLayout(collect_kind_label_layout)

        collect_kind_comment = QHBoxLayout()
        collect_kind_comment.addWidget(self.is_collect_comment)
        collect_kind_comment.addWidget(self.collect_type_comment)
        id_pw_layout.addLayout(collect_kind_comment)

        collect_kind_layout = QHBoxLayout()
        collect_kind_layout.addWidget(self.collect_type_id)
        collect_kind_layout.addWidget(self.collect_type_email)
        collect_kind_layout.addWidget(self.collect_type_nickname)
        collect_kind_layout.addWidget(self.collect_type_title)
        # collect_kind_layout.addWidget(self.collect_type_content)
        id_pw_layout.addLayout(collect_kind_layout)

        id_pw_group.setLayout(id_pw_layout)

        control_group = QGroupBox()
        control_group.setMaximumWidth(self.group_width)
        setting_control_box_layout = QVBoxLayout()

        setting_control_layout = QHBoxLayout()
        setting_control_layout.addWidget(self.setting_init_button)
        setting_control_box_layout.addLayout(setting_control_layout)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.execute_button)
        setting_control_box_layout.addLayout(control_layout)        

        qna_label = QLabel('개발문의 :')
        kakao_button = QPushButton("카카오 오픈채팅")
        discord_button = QPushButton("디스코드")
        # 버튼 클릭 시 링크 연결
        kakao_button.clicked.connect(self.open_kakao_chat)
        discord_button.clicked.connect(self.open_discord_chat)
        qna_layout = QHBoxLayout()
        qna_layout.addWidget(qna_label, stretch=1)
        qna_layout.addWidget(kakao_button, stretch=4)
        qna_layout.addWidget(discord_button, stretch=4)
        setting_control_box_layout.addLayout(qna_layout)

        control_group.setLayout(setting_control_box_layout)

        monitor_group = QGroupBox()
        monitor_group.setMaximumWidth(1000)
        monitor_layout = QVBoxLayout()

        # log_monitor의 비율을 2로 설정
        monitor_layout.addWidget(self.log_monitor_label)
        monitor_layout.addWidget(self.log_monitor, stretch=2)

        monitor_group.setLayout(monitor_layout)

        # 프로그레스바 생성 및 초기 숨김 처리
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(1000)
        self.progress_bar.hide()

        # Arrange groups in the grid layout
        grid = QGridLayout()
        grid.addWidget(id_pw_group, 0, 0)
        grid.addWidget(control_group, 1, 0)
        grid.addWidget(monitor_group, 0, 1, 2, 1)
        grid.addWidget(self.progress_bar, 2, 0, 2, 2, alignment=Qt.AlignCenter)

        self.setLayout(grid)
        
        self.setWindowTitle('Naver Cafe ID Collect')
        self.setGeometry(100, 100, 1300, 500)
        self.show()

        self.util_log = UtilLog(log_monitor=self.log_monitor)
        self.api.util_log = self.util_log
        self.util_log.add_log("프로그램이 실행되었습니다.")

        licence_key = self.util_licence.get_licence_key()
        if licence_key != "naverautocommentmasterkey20240722":
            if not licence_key:
                self.util_log.add_log("라이선스 키가 없습니다. licence.json 파일을 확인해주세요.", "red")
                self.util_log.add_log("5초 후 프로그램이 종료됩니다.", "red")
                QTimer.singleShot(5000, self.close_application)
            else:
                exists, ip = self.util_licence.value_exists(licence_key)
                if not exists:
                    self.util_log.add_log("잘못된 라이선스 키 입니다. licence.json 파일을 확인해주세요.", "red")
                    self.util_log.add_log("5초 후 프로그램이 종료됩니다.", "red")
                    QTimer.singleShot(5000, self.close_application)

    # 버튼 클릭 시 링크로 연결되는 함수 정의
    def open_kakao_chat(self):
        QDesktopServices.openUrl(QUrl("https://open.kakao.com/o/sEAjJBEg"))

    def open_discord_chat(self):
        QDesktopServices.openUrl(QUrl("https://discord.gg/FupABeCw"))

    def close_application(self):
        self.close()
        QApplication.instance().quit()

    def toggle_password_visibility(self, checked):
        if checked:
            self.pw_input.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setText('비밀번호 숨김')
        else:
            self.pw_input.setEchoMode(QLineEdit.Password)
            self.toggle_button.setText('비밀번호 보기')

    def check_login(self):
        if self.id_input.text() == "" or self.pw_input.text() == "":
            QMessageBox.information(self, '알림', 'ID, PW를 입력해주세요')
            return
        
        self.util_log.add_log("로그인을 시작합니다. (완료될 때 까지 잠시만 기다려 주세요.)")
        QApplication.processEvents()

        user_id = self.id_input.text().strip()
        user_pw = self.pw_input.text().strip()

        is_login = self.api.auto_login(user_id, user_pw)
        if is_login:
            self.util_log.add_log("로그인에 성공했습니다.")
            self.is_login = True
            QMessageBox.information(self, '알림', '로그인에 성공 했습니다.')
            cafe_list = self.api.get_cafe_list()
        
            self.cafe_list = cafe_list

            cafe_names = [cafe[2] for cafe in cafe_list]  # cafe[2]는 cafeName

            self.cafe_list_combo.addItems(cafe_names)
        else:
            self.util_log.add_log("로그인에 실패했습니다. (로그인 정보 재입력 후 재시도 해주세요.)", "red")
            QMessageBox.information(self, '경고', '로그인에 실패 했습니다. (로그인 정보 재입력 후 재시도 해주세요.)')
            return

    # 게시판 종류 추출
    def collect_category_list(self):
        if self.is_login:
            cafe_idx = self.cafe_list_combo.currentIndex()
            cafe_id = self.cafe_list[cafe_idx][0]

            board_list = self.api.call_board_no(cafe_id)
            self.category_combo.clear()

            self.category_combo.addItems([f"{item['menu_id']}] {item['menu_name']}" for item in board_list])
            self.util_log.add_log("게시판 종류 추출이 완료되었습니다.")
            QMessageBox.information(self, '알림', '게시판 추출 완료')
        else:
            QMessageBox.warning(self, '경고', '로그인을 먼저 진행해 주세요')

    # 설정값 초기화
    def init_settings(self):
        reply = QMessageBox.question(self, '확인', '정말로 초기화 하시겠습니까? \n 초기화 후에는 로그인 및 Cafe ID추출을 재시도 해주세요',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.id_input.clear()
                self.pw_input.clear()
                self.category_combo.setCurrentIndex(0)
                self.category_combo.clear()
                self.cafe_list_combo.clear()
                self.log_monitor.setRowCount(0)

                self.util_log.add_log("설정값을 초기화 합니다.")
                QMessageBox.information(self, '알림', '설정값을 초기화 했습니다. (로그인 및 Cafe ID추출을 재시도 해주세요)')
            except:
                self.util_log.add_log("설정값 초기화 실패", "red")
                logging.error(f"설정값 초기화 실패 :: {traceback.format_exc()}")

    def execute_task(self):
        try:
            if not self.is_login:
                QMessageBox.warning(self, '경고', '로그인을 먼저 진행해 주세요')
                return

            if self.cafe_list_combo.currentIndex() < 0:
                QMessageBox.warning(self, '경고', '카페목록을 확인해주세요 (로그인 해주세요)')
                return

            if self.category_combo.currentIndex() < 0:
                QMessageBox.warning(self, '경고', '게시판 종류를 확인해주세요 (게시판 추출을 해주세요)')
                return

            if (not self.collect_type_id.isChecked() and not self.collect_type_email.isChecked() 
                and not self.collect_type_nickname.isChecked() and not self.collect_type_title.isChecked() 
                and not self.collect_type_content.isChecked()):
                QMessageBox.warning(self, '경고', '최소 한 가지 이상의 수집 항목을 선택해 주세요')
                return

            # 수집 파라미터 설정
            collect_params = {
                "cafe_id": self.cafe_list[self.cafe_list_combo.currentIndex()][0],
                "board_id": self.category_combo.currentText().split("]")[0],
                "board_collect_count": self.category_count_spinbox.text(),
                "options": {
                    "is_collect_comment": self.is_collect_comment.isChecked(),
                    "is_collect_type_id": self.collect_type_id.isChecked(),
                    "is_collect_type_email": self.collect_type_email.isChecked(),
                    "is_collect_type_nickname": self.collect_type_nickname.isChecked(),
                    "is_collect_type_title": self.collect_type_title.isChecked(),
                    "is_collect_type_comment": self.collect_type_comment.isChecked()
                }
            }

            # 프로그레스바 표시 및 초기화
            self.progress_bar.setValue(0)
            self.progress_bar.show()

            # 버튼 비활성화
            self.execute_button.setEnabled(False)
            self.setting_init_button.setEnabled(False)
            self.login_button.setEnabled(False)
            self.cafe_url_chech_btn.setEnabled(False)

            # 스레드 설정 및 실행
            self.thread = TaskThread(self.api, self.util_log, collect_params)
            self.thread.progress_update.connect(self.update_progress)
            self.thread.task_finished.connect(self.task_finished)
            self.thread.error_occurred.connect(self.handle_error)
            self.thread.start()

        except Exception as e:
            error_message = f"execute_task 오류 발생(재실행 필요): {str(e)}"
            self.util_log.add_log(error_message, "red")
            logging.error(f"execute_task 오류 발생: {traceback.format_exc()}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)  # 프로그레스바 값 업데이트

    def task_finished(self):
        QMessageBox.information(self, "완료", "계정 수집이 완료되었습니다.")
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        # 버튼 활성화
        self.execute_button.setEnabled(True)
        self.setting_init_button.setEnabled(True)
        self.login_button.setEnabled(True)
        self.cafe_url_chech_btn.setEnabled(True)

    def handle_error(self, error_message):
        QMessageBox.critical(self, "에러", error_message)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        # 버튼 활성화
        self.execute_button.setEnabled(True)
        self.setting_init_button.setEnabled(True)
        self.login_button.setEnabled(True)
        self.cafe_url_chech_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
