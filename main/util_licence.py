import requests
import json

# Notion API 토큰 및 데이터베이스 ID 설정
NOTION_API_KEY = "secret_sH22wZDr5FpD3EAoZtAa1M0GEGZ0MOwQGgd9xHpMyo3"
DATABASE_ID = "1342f94a-e738-472f-96be-2c2683e053ae"

class UtilLicence:
    def __init__(self) -> None:
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        pass


    # 데이터베이스에서 데이터 읽기
    def read_database(self, cursor=None):
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        payload = {}
        if cursor:
            payload['start_cursor'] = cursor
        
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None

    # 특정 속성 값을 가진 항목이 존재하는지 확인하는 함수
    def value_exists(self, target_value):
        cursor = None
        while True:
            data = self.read_database(cursor)
            if data:
                for page in data['results']:
                    properties = page['properties']
                    value_property = properties.get('VALUE')
                    ip_property = properties.get("IP")
                    if value_property:
                        value = self.parse_property(value_property)
                        if value == target_value:
                            return True, ip_property
                cursor = data.get('next_cursor')
                if not data['has_more']:
                    break
            else:
                break
        return False, ""

    # 각 속성의 값을 적절히 파싱하는 함수
    def parse_property(self, prop):
        prop_type = prop['type']
        if prop_type == 'title':
            return ' '.join([item['text']['content'] for item in prop['title']])
        elif prop_type == 'rich_text':
            return ' '.join([item['text']['content'] for item in prop['rich_text']])
        elif prop_type == 'number':
            return prop['number']
        elif prop_type == 'select':
            return prop['select']['name'] if prop['select'] else None
        elif prop_type == 'multi_select':
            return ', '.join([item['name'] for item in prop['multi_select']])
        elif prop_type == 'date':
            return prop['date']['start'] if prop['date'] else None
        elif prop_type == 'checkbox':
            return prop['checkbox']
        elif prop_type == 'url':
            return prop['url']
        elif prop_type == 'email':
            return prop['email']
        elif prop_type == 'phone_number':
            return prop['phone_number']
        elif prop_type == 'formula':
            return prop['formula']['string']
        elif prop_type == 'rollup':
            return prop['rollup']['array']
        elif prop_type == 'people':
            return ', '.join([person['name'] for person in prop['people']])
        elif prop_type == 'files':
            return ', '.join([file['name'] for file in prop['files']])
        else:
            return "Unsupported Property"

    def get_licence_key(self):
        try:
            with open('licence.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('licence')
        except Exception as e:
            print("fail")
            return None