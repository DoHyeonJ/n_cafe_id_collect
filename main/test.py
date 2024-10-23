import requests
import json

header = {'Cookie': 'BUC=_iy07Svi574lnh2iVp3ffhI9_ADnP4mGCxBO2u-0h58=; NM_srt_chzzk=1; PM_CK_loc=290e49fae29e5c027ce9fd02a78e28e5a08029d311a79232d5f52710aa5854de; NID_JKL=+qo1m7EuCgqB0grQZGQwVLByrHy6LSHhZjyYMkWZLi4=; nid_inf=506380252; NID_SES=AAABk7tb7sKwbEaopOGXZ6ciLXPpAZIYzC//otbteD5sXosWcheNz16Yf9qn4fVRpCPvNZ1B3iK6HkdpWUmthZdbS2p1IVNsVMePsPa4chugKW8CUQUp+EaHzAcD55g+LO23FFi8AE45DqNt0qb1NnPjEOyDEr9Opk6mmFOohJuL5xVg1uVwV+GBv6PGUIWV1OZxflHWuW8xZvlw9GgzT+fO9vCVXgskZdnqElno6EqF6P82BcUj034IQ9leUHPFavk9c0FNtXF9IDkutV3ADmOzho9wkG39h3MjXl+u7EZ3CQy7mbNAtVxFwpmVfMCoBqUXyTKU8wbgRbENWXSBi40Gq46Sc16DHumoEC+8Weh8APdzPfo/aAJZPBw0Cci0yoeZIc6lrY87MIWDIaazBrqThW4e9VFRb5zzOvAaU+eX72l0G4ma+ucF/fPweDqlwBB+hMi5weq2zpst0Ce8KlSelkDJVsY2KQUreFBGJW2cOOYPizzRGULGRChTaTqHqziW7pcq+f59OWc/cbi/ncgx5WEDY6aFtQW1U+QuLQggrNNo; NACT=1; NID_AUT=9zpLSw78Wu12sLf5EcMw6QAEh6ELC38NS3y1l5oEUx68LzgRQpgHUeEjw/aWtYd/; NNB=SOR432WYFIIWO; NAC=d2QeDoAs7FNPB;', 'Referer': 'https://cafe.naver.com/', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'}

# 1) 로그인 하고, 카페 게시판 추출하고 특정 게시판에 존재하는 게시글들 ID랑 댓글 ID추출하는

# 2) 특정 게시글 링크를 넣고 단발성으로 추출하는

# 3) 게시글 정보도 같이 추출 -> 엑셀파일로 만들어줌 \

def get_board_list():
    pass

# 게시글 유저ID 추출
def get_article_user_id(cafe_id, article_id):
    api_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/{cafe_id}/articles/{article_id}?query=&useCafeId=true&requestFrom=A"

    response = requests.get(api_url, headers=header)
    response_json = response.json()

    writer_id = response_json['result']['article']['writer']['id']
    subject = response_json['result']['article']['subject']

    return writer_id, subject

# 댓글 유저ID 추출
def get_comment_user_id(cafe_id, article_id, page_num=1):
    user_ids = []

    while True:
        # 100개라면 다음페이지 존재함
        api_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2/cafes/{cafe_id}/articles/{article_id}/comments/pages/{page_num}?requestFrom=A&orderBy=asc"

        response = requests.get(api_url, headers=header)
        response_json = response.json()

        comment_list = response_json['result']['comments']['items']
        for comment in comment_list:
            user_info = {
                'comment': comment['content'],
                'id': comment['writer']['id'],
                'nick': comment['writer']['nick']
            }
            user_ids.append(user_info)

        if len(comment_list) < 100:
            break
        else:
            page_num += 1

    return user_ids

# 쪽지 제한 수 GET
def get_limit_message():
    pass

# 쪽지 전송
def post_message():
    pass

if __name__ == "__main__":
    article_user_info = get_article_user_id("15723206", "2148422")
    comment_user_list = get_comment_user_id("15723206", "2148422")
    get_limit_message()
    post_message()

    print(article_user_info)
    
    user_str = ""
    added_ids = set()  # 이미 추가된 ID를 저장할 집합
    for comment in comment_user_list:
        if comment['id'] not in added_ids:
            user_str += comment['id'] + ","
            added_ids.add(comment['id'])

    user_str = user_str.rstrip(",")  # 마지막 쉼표 제거
    print(user_str)

