from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from util_log import UtilLog
import os
import platform
import pyperclip
import logging
import requests
import datetime
import sys
import html
import traceback
import pandas as pd

# 로그 포맷 정의
log_format = '%(asctime)s - %(levelname)s - %(message)s'

# 현재 연도와 월에 해당하는 디렉토리 경로 생성
log_dir = "logs/{year}-{month}".format(
    year=datetime.datetime.now().strftime("%Y"),
    month=datetime.datetime.now().strftime("%m")
)

# 디렉토리가 없는 경우 생성
os.makedirs(log_dir, exist_ok=True)

# 로그 파일 이름 생성
log_file_name = os.path.join(log_dir, "sys_log_" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + ".log")

# 기본 설정을 UTF-8로 설정
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_file_name, encoding="utf-8"),  # 파일 핸들러에 UTF-8 인코딩 지정
        logging.StreamHandler(sys.stdout)  # 콘솔 출력 설정 (원하는 경우)
    ]
)


class Api():
    def __init__(self, util_log: UtilLog=None, cafe_id=None, board_id=None, board_collect_count=None):
        self.driver = None
        self.headers = None
        self.util_log = util_log
        self.cafe_id = cafe_id
        self.board_id = board_id
        self.board_collect_count = board_collect_count

    def _open_web_mode(self):
        driver_path = ChromeDriverManager().install()
        correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
        self.driver = webdriver.Chrome(service=Service(executable_path=correct_driver_path))
        self.driver.set_page_load_timeout(120)

    # 로그인, 회원정보 추출
    def auto_login(self, user_id, user_pw):
        self._open_web_mode()
        self.driver.get("https://nid.naver.com/nidlogin.login?mode=form")

        # 아이디 입력
        id_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id"))
        )
        id_input.click()
        pyperclip.copy(user_id)
        
        actions = ActionChains(self.driver)
        if platform.system() == 'Darwin':  # macOS
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
        else:  # Windows and others
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # 패스워드 입력
        pw_input = self.driver.find_element(By.ID, "pw")
        pw_input.click()
        pyperclip.copy(user_pw)
        
        if platform.system() == 'Darwin':  # macOS
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
        else:  # Windows and others
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.ID, "log.login")
        login_btn.click()

        try:
            err_common = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.ID, "err_common"))
            )

            error_msg = err_common.find_element(By.CSS_SELECTOR ,".error_message")

            # 로그인 실패 시
            if error_msg.text:
                logging.info("로그인 실패")
                self.driver.quit()
                return False
        except:
            logging.info("로그인 실패메세지 pass")

        # 로그인 후 '새로운 환경' 알림에서 '등록안함' 버튼 클릭
        try:
            element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.btn_cancel"))
            )
            element.click()
        except:
            logging.info("등록안함 pass")

        # 2차 인증 존재하는지 체크
        try:
            element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button#useotpBtn"))
            )
            
            self.util_log.add_log("2차 인증이 존재합니다. 인증을 완료해주세요.")
        except:
            logging.info("2차 인증 pass")

        # 메인페이지로 성공적으로 돌아왔을때 쿠키 Get
        try:
            element = WebDriverWait(self.driver, 240).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.search_area"))
            )
        except:
            logging.info("메인 페이지 접근 실패")

        cookies = self.driver.get_cookies()
        result_cookie_str = ""
        for cookie in cookies:
            key = cookie['name']
            value = cookie['value']
            result_cookie_str = f"{result_cookie_str} {key}={value};"
        
        if cookies:
            user_agent = self.driver.execute_script("return navigator.userAgent;")
            # Header 정보 세팅
            self.headers = {
                'Cookie': result_cookie_str.strip(),
                'Referer': 'https://cafe.naver.com/',
                'User-Agent': user_agent
            }

            logging.info("사용자 정보 확인 완료 ::: ")
            logging.info(self.headers)
            self.driver.quit()
            return True
        
        logging.info("사용자 정보 확인 실패")
        self.driver.quit()
        return False
    
    # 로그인한 계정의 카페 리스트 GET
    def get_cafe_list(self):
        api_url = "https://apis.naver.com/cafe-home-web/cafe-home/v1/cafes/join?page=1&perPage=1000&type=join&recentUpdates=true"

        response = requests.get(api_url, headers=self.headers)

        data = response.json()
        
        cafe_info = [(cafe['cafeId'], cafe['cafeUrl'], cafe['cafeName']) for cafe in data['message']['result']['cafes']]

        return cafe_info

    # 게시판 종류 GET
    def call_board_no(self, cafe_id):
        menu_list = []
        url = f"https://apis.naver.com/cafe-web/cafe2/SideMenuList?cafeId={cafe_id}"
        response = requests.get(url, headers=self.headers)
        # menuType
        # P: 즐겨찾는게시판, F: 대분류, L: 링크, B: 게시판, M: 멤버전용

        # 전체글 포함
        menu_list.append({'menu_id': "all",'menu_name': "전체 게시글", 'menu_type': "",'board_type': "",'sort': 0})

        # boardType
        # I: 이미지, L: 일반 게시판, T: 판매
        response_json = response.json()
        if response.status_code == 200:
            for menu in response_json['message']['result']['menus']:
                if menu['menuType'] != 'P' and menu['menuType'] != 'L' and menu['menuType'] != 'F':
                    menu_list.append(
                        {
                        'menu_id': menu['menuId'],
                        'menu_name': html.unescape(menu['menuName']), 
                        'menu_type': menu['menuType'],
                        'board_type': menu['boardType'],
                        'sort': menu['listOrder']
                        }
                    )

            menu_list.sort(key=lambda x: x['sort'])

            return menu_list
        
        return False
    
    def call_board_list(self):
        cafe_id = self.cafe_id
        menu_id = self.board_id
        per_page = 20  # 한 페이지당 최대 20개의 게시글을 가져옴
        total_collect_count = int(self.board_collect_count)
        result = []
        page = 1

        while len(result) < total_collect_count:
            url = f"https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json?search.clubid={cafe_id}&search.queryType=lastArticle&search.menuid={menu_id}&search.page={page}&search.perPage={per_page}&adUnit=MW_CAFE_ARTICLE_LIST_RS"
            
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    response_json = response.json()
                    article_list = response_json['message']['result']['articleList']
                    article_list = sorted(article_list, key=lambda x: x['articleId'])

                    # 결과 리스트에 추가하고 필요한 게시글 수 만큼만 저장
                    for article in article_list:
                        if len(result) >= total_collect_count:
                            break
                        article_id = article['articleId']
                        subject = article['subject']
                        writer = article['writerNickname']
                        result.append({"article_id": article_id, "subject": subject, "writer": writer})

                else:
                    logging.error(f"Failed to fetch page {page}: {response.status_code}")
                    break  # 요청 실패 시 루프 종료

                page += 1  # 다음 페이지로 이동

            except Exception as e:
                error_message = f"게시글 수집 실패: {str(e)}"
                logging.error(error_message)
                break  # 예외 발생 시 루프 종료

        return result  # 수집된 게시글 리스트 반환


    def get_article_user_id(self, article_id):
        api_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/{self.cafe_id}/articles/{article_id}?query=&useCafeId=true&requestFrom=A"

        try:
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()

            writer_id = response_json['result']['article']['writer']['id']
            nick = response_json['result']['article']['writer']['nick']
            subject = response_json['result']['article']['subject']

            user_info = {
                "writer_id": writer_id,
                "nick": nick,
                "subject": subject
            }

            return user_info
        except Exception as e:
            error_message = f"게시글 사용자 정보 추출 실패 (Article ID: {article_id}): {str(e)}"
            logging.error(error_message)
            return {}

    def get_comment_user_id(self, article_id):
        user_info_list = []
        page_num = 1

        while True:
            # 100개라면 다음페이지 존재함
            api_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2/cafes/{self.cafe_id}/articles/{article_id}/comments/pages/{page_num}?requestFrom=A&orderBy=asc"

            try:
                response = requests.get(api_url, headers=self.headers)
                response.raise_for_status()
                response_json = response.json()

                comment_list = response_json['result']['comments']['items']
                for comment in comment_list:
                    user_info = {
                        'comment': comment['content'],
                        'id': comment['writer']['id'],
                        'nick': comment['writer']['nick']
                    }
                    user_info_list.append(user_info)

                if len(comment_list) < 100:
                    break
                else:
                    page_num += 1
            except Exception as e:
                error_message = f"댓글 수집 실패 (Article ID: {article_id}, Page: {page_num}): {str(e)}"
                logging.error(error_message)
                break

        return user_info_list

    def run(self, is_collect_comment=False, is_collect_type_id=False, is_collect_type_email=False,
        is_collect_type_nickname=False, is_collect_type_title=False, is_collect_type_comment=False):
        """
        게시글을 수집하고 지정된 옵션에 따라 데이터를 엑셀 파일로 저장합니다.

        :param is_collect_comment: 댓글 수집 여부
        :param is_collect_type_id: 작성자 ID 수집 여부
        :param is_collect_type_email: 작성자 이메일 수집 여부 (API에서 제공되지 않는 경우 비활성화)
        :param is_collect_type_nickname: 작성자 닉네임 수집 여부
        :param is_collect_type_title: 게시글 제목 수집 여부
        :param is_collect_type_comment: 게시글 댓글 수집 여부
        """
        try:
            seen_writer_ids = set()  # 중복 확인을 위한 set

            # 게시글 수집
            board_list = self.call_board_list()
            article_ids = [article['article_id'] for article in board_list]

            data_list = []

            for article_id in article_ids:
                user_info = self.get_article_user_id(article_id)
                if user_info == {}:
                    logging.error(f"수집 실패한 게시글 PASS :: article_id : {article_id}")
                    continue

                writer_id = user_info.get('writer_id', '')

                if writer_id in seen_writer_ids:  # 이미 처리된 writer_id라면 건너뜀
                    continue

                data = {}

                if is_collect_type_id:
                    data['writer_id'] = writer_id
                if is_collect_type_email:
                    # API 응답에 이메일 정보가 없는 경우 빈 값으로 설정
                    data['email'] = user_info.get('writer_id', '') + "@naver.com"
                if is_collect_type_nickname:
                    data['nick'] = user_info.get('nick', '')
                if is_collect_type_title:
                    data['subject'] = user_info.get('subject', '')

                if writer_id != '':
                    seen_writer_ids.add(writer_id)  # 처리된 writer_id를 set에 추가

                data_list.append(data)

                if is_collect_comment:
                    comment_info = self.get_comment_user_id(article_id)
                    if len(comment_info) == 0:
                        logging.error(f"수집 실패한 댓글 PASS :: article_id : {article_id}")
                        continue

                    for comment in comment_info:
                        data = {}

                        if comment['id'] in seen_writer_ids:  # 이미 처리된 writer_id라면 건너뜀
                            continue

                        if is_collect_type_comment:
                            data['comment'] = comment['comment']
                        if is_collect_type_id:
                            data['writer_id'] = comment['id']
                        if is_collect_type_nickname:
                            data['nick'] = comment['nick']
                        if is_collect_type_email:
                            data['email'] = comment['id'] + "@naver.com"

                        seen_writer_ids.add(comment['id'])

                        data_list.append(data)

            if not data_list:
                self.util_log.add_log("수집된 게시글이 없습니다.", "yellow")
                logging.warning("수집된 게시글이 없습니다.")
                return

            # 엑셀 파일로 저장
            self.save_to_excel(data_list)
        except Exception as e:
            error_message = f"계정 수집 중 오류 발생: {traceback.format_exc()}"
            self.util_log.add_log(error_message, "red")
            logging.error(error_message)


    def save_to_excel(self, data_list):
        # 데이터프레임 생성 및 컬럼명 변경
        df = pd.DataFrame(data_list)
        column_mapping = {
            'writer_id': '아이디',
            'email': '이메일',
            'nick': '닉네임',
            'subject': '제목',
            'comment': '댓글내용'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 현재 연도와 월에 해당하는 디렉토리 경로 생성
        excel_dir = "excel/{year}-{month}".format(
            year=datetime.datetime.now().strftime("%Y"),
            month=datetime.datetime.now().strftime("%m")
        )

        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(excel_dir, exist_ok=True)

        # 엑셀 파일 이름 생성
        base_file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        excel_file_name = os.path.join(excel_dir, base_file_name)

        # 파일이 이미 존재할 경우 넘버링 추가
        counter = 1
        while os.path.exists(excel_file_name):
            numbered_file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d')}({counter}).xlsx"
            excel_file_name = os.path.join(excel_dir, numbered_file_name)
            counter += 1

        try:
            # 엑셀 파일로 저장
            df.to_excel(excel_file_name, index=False)
            success_message = f"엑셀 파일 생성 성공: {excel_file_name}"
            self.util_log.add_log(success_message, "green")
            logging.info(success_message)
        except Exception as e:
            error_message = f"엑셀 파일 생성 실패: {str(e)}"
            self.util_log.add_log(error_message, "red")
            logging.error(error_message)



