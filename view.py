from linebot.models import *
import requests
import json


def location():
    """第一句，請使用者傳送地點"""
    message = TextSendMessage(text="你好，我是美食機器人，請告訴我你的所在位置，我將會為您推薦好吃的食物!",
                              quick_reply=QuickReply(items=[
                                  QuickReplyButton(action=LocationAction(label="查詢目前所在位置"))])
                              )
    return message


def transport():
    """第二句，請使用者選擇他使用的交通工具"""
    message = TemplateSendMessage(
        alt_text='交通運具選擇方式',
        template=ButtonsTemplate(
            title='交通工具',
            text='請問您使用的交通運具種類為何呢？\n(如需重新選擇請輸入「交通方式」)',
            actions=[
                MessageTemplateAction(
                    label='步行',
                    text='步行',
                    # data=""
                ),
                MessageTemplateAction(
                    label='單車',
                    text='單車',
                    # data=''
                ),
                MessageTemplateAction(
                    label='機車',
                    text='機車',
                    # data=''
                ),
                MessageTemplateAction(
                    label='汽車',
                    text='汽車',
                    # data=''
                )
            ]
        )
    )
    return message


def open_q():
    """開放式問答"""
    message = TextSendMessage(text="好的，請問你想吃甚麼呢？")
    return message


def google_needed():
    """資料庫查無結果的時候使用"""
    message = TemplateSendMessage(
        alt_text='資料庫尚無匹配到相關店家，是否需要透過google map幫您搜尋?',
        template=ButtonsTemplate(
            title='資料庫無資料',
            text='資料庫尚無匹配到相關店家，是否需要透過google map幫您搜尋相關結果?',
            actions=[
                MessageTemplateAction(
                    label='是',
                    text='好的',
                    # data=""
                ),
                MessageTemplateAction(
                    label='否',
                    text='不需要',
                    # data=''
                )
            ]
        )
    )
    return message


def random_recommendation():
    """食物主題，負面情緒時使用"""
    message = TemplateSendMessage(
        alt_text='隨機為您推薦店家',
        template=ButtonsTemplate(
            title='隨機推薦',
            text='喜歡我們隨機推薦你的美食嗎?',
            actions=[
                MessageTemplateAction(
                    label='是',
                    text='喜歡',
                    # data=""
                ),
                MessageTemplateAction(
                    label='否',
                    text='不喜歡，再來一個',
                    # data=''
                )
            ]
        )
    )
    return message


def recommendation_pattern(POI_name, POI_rating, POI_address, POI_open, POI_money, POI_url):
    """推薦食品的預設格式"""
    message = TextSendMessage(
        text=f"""===== 以下為您推薦 =====\n \
📌 {POI_name}\n \
⭐ 評分 | {POI_rating}\n \
🏠 地址 | {POI_address}\n \
🈺 營業狀況 | {POI_open} \n \
💲 價錢區間 | {POI_money} \n \
📢 點我查看更多 \n{POI_url}""")
    return message


def google_api(lat, lng, r, keyword):
    """最後一句，如果在資料庫裏面找不到相對應的品項，就呼叫google places api做搜尋"""
    API = "AIzaSyBXioCZJv01QRXxBedIqkjSeC2ilJY3TVU"
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}%2C{lng}&radius={r}&type=restaurant&keyword={keyword}&key={API}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    max = 0
    place_id = ""
    try:
        for i in response['results']:
            if(float(i['rating']) > max):
                max = float(i['rating'])
                place_id = i['place_id']
                POI_name = i['name']
                POI_url, POI_address = __get_poi_url(place_id, API=API)
                try:
                    POI_rating = i['rating']
                except:
                    POI_rating = "無資料"
                try:
                    POI_open = i['opening_hours']['open_now']
                except:
                    POI_open = "無資料"
                try:
                    POI_money = i['price_level']
                except:
                    POI_money = "無資料"
    except:
        return -1
    else:
        # POI_open data convert
        if POI_open == True:
            POI_open = '營業中'
        elif POI_open == "無資料":
            POI_open = '無資料'
        else:
            POI_open = '休息中'

        # POI_money data convert
        if POI_money == 0:
            POI_money = "免費"
        elif POI_money == 1:
            POI_money = "低"
        elif POI_money == 2:
            POI_money = "中"
        elif POI_money == 3:
            POI_money = "高"
        elif POI_money == 4:
            POI_money = '超高'
        print(POI_name, POI_rating, POI_address, POI_open, POI_money, POI_url)
        return (POI_name, POI_rating, POI_address, POI_open, POI_money, POI_url)


# 取得前述餐廳中評分最高的google map url
def __get_poi_url(place_id, API):
    """透過google places api搜尋店家google map網址"""
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=url%2Cformatted_address&key={API}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    POI_url = response['result']['url']
    POI_address = response['result']['formatted_address']
    return POI_url, POI_address


def get_poi_detail(place_id):
    API = "AIzaSyBXioCZJv01QRXxBedIqkjSeC2ilJY3TVU"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    POI_name = response['result']['name']
    POI_address = response['result']['formatted_address']
    POI_url = response['result']['url']
    try:
        POI_rating = response['result']['rating']
    except:
        POI_rating = "無資料"
    try:
        POI_open = response['opening_hours']['open_now']
    except:
        POI_open = "無資料"
    try:
        POI_money = response['price_level']
    except:
        POI_money = "無資料"
    # POI_open data convert
    if POI_open == True:
        POI_open = '營業中'
    elif POI_open == "無資料":
        POI_open = '無資料'
    else:
        POI_open = '休息中'
    # POI_money data convert
    if POI_money == 0:
        POI_money = "免費"
    elif POI_money == 1:
        POI_money = "低"
    elif POI_money == 2:
        POI_money = "中"
    elif POI_money == 3:
        POI_money = "高"
    elif POI_money == 4:
        POI_money = '超高'
    return (POI_name, POI_rating, POI_address, POI_open, POI_money, POI_url)


if(__name__ == "__main__"):
    data = google_api(23.00071, 120.215205, 1500, '咖哩')
    print(data)
