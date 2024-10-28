import requests
import json

header = {'Cookie': 'BUC=Z3aR2lKzpwdhszQqRmCyDbgIIWLxPqc7ChG7jqC84UQ=; NM_srt_chzzk=1; PM_CK_loc=290e49fae29e5c027ce9fd02a78e28e5a08029d311a79232d5f52710aa5854de; NID_JKL=vpFvtmGde+DwZDSFGIWUH1gDnestgo4ccg0OUKxn1rY=; nid_inf=346058160; NID_SES=AAABoaWJwpy/mywj5EYPKXvGNy/nhLHHYh7MCK6G37RJ0NgjBORbpcFQn9hzfkvRSa3/AESSaPMstlYUcjGZ0brt9C61SF03ZRDhOUhEWCUuob04yrA5B2jnY2nXFn76fWj97J8qPrH8ZeNiw7QutJiPoWegTEy/4FowKfml75jqmYuzXSUAFCbuEk+zJYVxitCaqVGXVtb3kqtuId1Vuh5trcNLEs4o6VP8TaWlUca5VsnJTSk2ko7GTO5N1JE3ltuQ4gzr1XKeCaNddFmwfNk+u/Ztz+OGEUmtAKr7QJFv9JQ7rOfMQ62yhYkGYeaiNARf3XcewNWfbOIUzQ4E9I7nXIcbjU733NmAY9D2ipLi4eVaoozjl96NErkSyiaPnZUVk1zA6oCETVaDLenPzrgBpzP0LnXBsES/jcB8x29lzBGnz/qE8wntuT257OtzunhdZe5JnTmqxJHbYQdCFgqKjCOIj2oodtVJy37mImjidalJ9gsOezU6loCCucyyXTCN4MCG+I2Bk92Pg5zP4wEo20c/p7pe78QCE8Je+3Xbu823QKy/rnzO72K3LsHaOVQBwg==; NACT=1; NID_AUT=hwFlGA9uXLejH+CMwqnpM/dXDjZXgg9nLgVb1RisWn2TXxipQrEbcSwMF5FcVBzM; NNB=AXDFWGRQNEOGO; NAC=4cfBCwACQ997B;', 'Referer': 'https://cafe.naver.com/', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}


# 1) 로그인 하고, 카페 게시판 추출하고 특정 게시판에 존재하는 게시글들 ID랑 댓글 ID추출하는

# 2) 특정 게시글 링크를 넣고 단발성으로 추출하는

# 3) 게시글 정보도 같이 추출 -> 엑셀파일로 만들어줌 \
# 


# 게시글 유저ID 추출
def get_article_user_id(cafe_id, article_id):
    api_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/{cafe_id}/articles/{article_id}?query=&useCafeId=true&requestFrom=A"

    response = requests.get(api_url, headers=header)
    response_json = response.json()

    writer_id = response_json['result']['article']['writer']['id']
    nick = response_json['result']['article']['writer']['nick']
    subject = response_json['result']['article']['subject']
    
    print(writer_id, nick, subject)

    return writer_id, subject, nick

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

# 로그인한 계정의 카페 리스트 GET
def get_cafe_list():
    api_url = "https://apis.naver.com/cafe-home-web/cafe-home/v1/cafes/join?page=1&perPage=1000&type=join&recentUpdates=true"

    response = requests.get(api_url, headers=header)

    data = response.json()
    
    cafe_info = [(cafe['cafeId'], cafe['cafeUrl'], cafe['cafeName']) for cafe in data['message']['result']['cafes']]

    return cafe_info

# 쪽지 제한 수 GET
def get_limit_message():
    pass

# 쪽지 전송
def post_message():
    pass

# menu_id를 비우고 요청할 경우 전체 글 조회 #
def call_board_list():
    page = "1"
    result = []

    url = f"https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json?search.clubid={25228091}&search.queryType=lastArticle&search.menuid=all&search.page={page}&search.perPage={100}&adUnit=MW_CAFE_ARTICLE_LIST_RS"
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            response_json = response.json()
            article_list = response_json['message']['result']['articleList']
            article_list = sorted(article_list, key=lambda x:x['articleId'])
            for article in article_list:
                article_id = article['articleId']
                subject = article['subject']
                writer = article['writerNickname']
                result.append({"article_id": article_id, "subject": subject, "writer": writer})

        print(len(result))
        return result
    except:
        pass

if __name__ == "__main__":
    # article_user_info = get_article_user_id("15723206", "2148422")
    # comment_user_list = get_comment_user_id("15723206", "2148422")
    # get_limit_message()
    # post_message()

    # print(article_user_info)
    
    # user_str = ""
    # added_ids = set()  # 이미 추가된 ID를 저장할 집합
    # for comment in comment_user_list:
    #     if comment['id'] not in added_ids:
    #         user_str += comment['id'] + ","
    #         added_ids.add(comment['id'])

    # user_str = user_str.rstrip(",")  # 마지막 쉼표 제거
    # print(user_str)

    # get_cafe_list()

    response = call_board_list()
    # print(response)