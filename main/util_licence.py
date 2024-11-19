import requests
import json
import sys
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import QTimer

class UtilLicence:
    def __init__(self) -> None:
        self.base_url = "http://jdh7693.gabia.io"
        self.headers = {
            "accept": "application/json"
        }

    def check_license(self, license_key):
        url = f"{self.base_url}/license"
        params = {"license_key": license_key, "license_type": "N_CAFE_COLLECT"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return False, "라이선스 확인 중 알수 없는 오류가 발생했습니다."

            response_data = response.json()

            if response_data.get('status_code') == 200:
                return True, response_data['data']['expires_at']
            else:
                return False, response_data['detail']
                
        except Exception as e:
            print(e)
            return False, "라이선스 확인 중 알수 없는 오류가 발생했습니다."

    def get_licence_key(self):
        try:
            with open('licence.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('licence')
        except Exception as e:
            print("fail")
            return None
