from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
# import button api
from linebot.models import ButtonsTemplate, MessageTemplateAction, TemplateSendMessage, PostbackTemplateAction
# import quick reply
from linebot.models import QuickReply, QuickReplyButton, LocationAction

import random
import configparser
import logging

from requests.models import Response

# import linebot回應模板
import view

# import subject/emotional辨識模型
from transformers import BertForSequenceClassification
import torch
from subject_bert import *
from emotional_bert import *

# import ckip_transformers模型
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger
from recognize_food_n import *

# import database similarity計算模型
from sentence_transformers import SentenceTransformer, util
from compute_n_silimar import *

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

line_bot_api = LineBotApi(config.get('line-bot', 'channel-access-token'))
handler = WebhookHandler(config.get('line-bot', 'channel-secret'))

# subject bert model
logging.debug("載入主題模型中...")
subject_model = BertForSequenceClassification.from_pretrained("subject_model")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
subject_model.to(device)
subject_model.eval()

# emotional bert model
logging.debug("載入情緒模型中...")
emotional_model = BertForSequenceClassification.from_pretrained(
    "emotional_model")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
emotional_model.to(device)
emotional_model.eval()

# ckip_pos Initialize drivers
logging.debug("載入分詞模型中...")
ws_driver = CkipWordSegmenter(level=3)
pos_driver = CkipPosTagger(level=3)

# n similarity model
logging.debug("載入相似度計算模型中...")
simi_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')


def cmp(w):
    """計算名詞相似度"""
    max = 0
    for i in data:
        i = i.keys()
        for word in i:
            sim = compute((word, w))
            if sim > max:
                max = sim
                ww = word
    return ww, max


def compute(wordpair):
    """計算名詞相似度"""
    embeddings = simi_model.encode(wordpair)
    distance = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return distance


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# global
ans = " "
lng = lat = 1.0
r = 0


@handler.add(MessageEvent)
# TextMessage
def handle_message(event):
    reply_all = []
    global ans, lng, lat, r

    # 處理地理座標type的訊息
    if event.message.type == 'location':
        logging.debug("接收到座標位置了")
        lat = event.message.latitude
        lng = event.message.longitude
        line_bot_api.reply_message(
            event.reply_token, view.transport())

    # 處理文字type的訊息
    elif event.message.type == 'text':
        text = event.message.text

        # 交通工具選擇
        if text == '步行' or text == '單車' or text == '機車' or text == '汽車':
            if(text == '步行'):
                r = 1000
            elif(text == '單車'):
                r = 3000
            elif(text == '機車'):
                r = 5000
            elif(text == '汽車'):
                r = 10000
            line_bot_api.reply_message(
                event.reply_token, view.open_q())

        # 聊天機器人開頭詞
        elif text == "哈囉" or text == "你好" or text == "嗨":
            line_bot_api.reply_message(
                event.reply_token, view.location())

        # 重新選擇交通工具
        elif text == "交通方式":
            line_bot_api.reply_message(
                event.reply_token, view.transport())

        # 資料庫無結果，透過GOOGLE NEARBY API進行搜尋
        elif text == '好的':
            logging.debug(f"{ans}, {lat}, {lng}, {r}")
            google_response = view.google_api(lat, lng, r, ans)

            # GOOGLE 查無結果
            if google_response == -1:
                reply_all.append(TextSendMessage(
                    text="不好意思，google map上也沒有你的搜尋結果，建議你可以嘗試輸入其他想吃的食物品項，讓我們再次為你服務"))

            # 回傳 GOOGLE 搜尋結果
            else:
                POI_name, POI_rating, POI_address, POI_open, POI_money, POI_url = google_response
                logging.debug(
                    f"{POI_name}, {POI_rating}, {POI_address},{POI_open}, {POI_money}, {POI_url}")
                reply_all.append(view.recommendation_pattern(
                    POI_name, POI_rating, POI_address, POI_open, POI_money, POI_url))

            line_bot_api.reply_message(event.reply_token, reply_all)

        # 資料庫比對無結果，且不需要透過GOOGLE幫忙搜尋
        elif text == '不需要':
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="請你再次輸入你想吃的食物內容"))

        # 處理開放式問答
        else:
            # 階段一：進行主題分類
            convert2tsv(text)
            testset = Review_Subject("response", tokenizer=tokenizer)
            testloader = DataLoader(testset, batch_size=1,
                                    collate_fn=create_mini_batch)

            predictions = get_predictions(subject_model, testloader)
            index_map = {v: k for k, v in testset.label_map.items()}
            predictions.tolist()
            df = pd.DataFrame({"label": predictions.tolist()})
            df['label_pre'] = df.label.apply(lambda x: index_map[x])
            df_pred = pd.concat([testset.df.loc[:, ["text"]],
                                 df.loc[:, 'label_pre']], axis=1)

            # 回傳主題分類結果
            for txt in df_pred['label_pre']:
                response = f"回答的主題是：{str(txt)}"
                subject = txt
            reply_all.append(TextSendMessage(text=response))

            if(subject == '食物'):
                # 階段二：若主題為食物，則進行情緒分類
                e_convert2tsv(text)
                testset = Review_Emotional(
                    "response_emotion", tokenizer=tokenizer)
                testloader = DataLoader(testset, batch_size=1,
                                        collate_fn=e_create_mini_batch)

                predictions = e_get_predictions(emotional_model, testloader)
                index_map = {v: k for k, v in testset.label_map.items()}
                predictions.tolist()
                e_df = pd.DataFrame({"label": predictions.tolist()})
                e_df['label_pre'] = e_df.label.apply(lambda x: index_map[x])
                e_df_pred = pd.concat([testset.df.loc[:, ["text"]],
                                       e_df.loc[:, 'label_pre']], axis=1)

                # 回傳情緒分類結果
                for txt in e_df_pred['label_pre']:
                    logging.debug(f"情緒是：{str(txt)}")
                    response = f"情緒是：{str(txt)}"
                    emotion = txt
                reply_all.append(TextSendMessage(text=response))

                # 階段三：進行詞性標記與篩選名詞
                text = [text]
                ws = ws_driver(text)
                pos = pos_driver(ws)
                for sentence_ws, sentence_pos in zip(ws, pos):
                    ans = pack_ws_pos_sentece(sentence_ws, sentence_pos)

                # 回傳名詞標記與篩選結果
                logging.debug(f"食物品項{ans}")
                reply_all.append(TextSendMessage(text=f"食物品項是：{ans}"))

                # 階段四：標記名詞與資料庫名詞進行相似度比對
                simi_food, simi_num = cmp(ans)
                logging.debug(f"資料庫比對結果為{simi_food},相似度{simi_num[0][0]:.3f}")

                # 回傳資料庫搜尋/隨機結果
                if emotion == "正面" or emotion == "中立":
                    if simi_num >= 0.8:
                        reply_all.append(TextSendMessage(
                            text=f"資料庫比對結果為:\n{simi_food}/相似度{simi_num[0][0]:.3f}"))
                        id = get_best_store(simi_food)
                        logging.debug(f"{id}")
                        result = view.get_poi_detail(id)
                        message = view.recommendation_pattern(
                            result[0], result[1], result[2], result[3], result[4], result[5])
                        reply_all.append(message)
                    else:
                        reply_all.append(TextSendMessage(
                            text=f"資料庫比對結果為:\n{simi_food}/相似度{simi_num[0][0]:.3f} \n⚠️相似度過低"))
                        reply_all.append(view.google_needed())

                elif emotion == "負面":
                    reply_all.append(TextSendMessage(
                        text=f"資料庫比對結果為:\n{simi_food}/相似度{simi_num[0][0]:.3f}\n⚠️我們將排除 {simi_food} 並隨機為您推薦資料庫中的店家"))
                    id = get_random_store()
                    logging.debug(f"{id}")
                    result = view.get_poi_detail(id)
                    message = view.recommendation_pattern(
                        result[0], result[1], result[2], result[3], result[4], result[5])
                    reply_all.append(message)

            # 回應主題"其他"
            elif(subject == '其他'):
                reply_all.append(TextSendMessage(
                    text="請您輸入想吃的食物品項喔！"))
            # 回應主題"價格、環境、地點、服務"
            else:
                reply_all.append(TextSendMessage(
                    text="不好意思，我們還不支援食物以外的主題喔~建議你可以重新搜尋，輸入想吃的食物品項，有助於我們更好的推薦你喔!"))

            line_bot_api.reply_message(event.reply_token, reply_all)


if __name__ == "__main__":
    # 主動推播第一則訊息
    line_bot_api.push_message(
        "Uf4811a6102c17022a991fcc3d85955b9", view.location())
    app.run(debug=True, port=8082)
