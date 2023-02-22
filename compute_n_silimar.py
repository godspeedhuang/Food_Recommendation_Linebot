import json
import random
from sentence_transformers import SentenceTransformer, util

# 資料庫檔案
with open("database_1_max.json", mode='r', encoding='utf-8') as file:
    data = json.load(file)


def cmp_t(w, simi_model):
    """跟資料庫名詞做名詞相似度計算"""
    max = 0
    for i in data:
        i = i.keys()
        for word in i:
            sim = compute_t((word, w), simi_model)
            if sim > max:
                max = sim
                ww = word
    return ww, max


def compute_t(wordpair, simi_model):
    """跟資料庫名詞做名詞相似度計算"""
    embeddings = simi_model.encode(wordpair)
    distance = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return distance


def get_best_store(name):
    """獲得該食物品項正評最多的店家"""
    for i in data:
        i_val = i.values()
        i_key = i.keys()
        for key, val in zip(i_key, i_val):
            if key == name:
                id = val['id']
    return id


def get_random_store():
    """隨機回傳店家"""
    random_id = []
    for i in data:
        i_val = i.values()
        i_key = i.keys()
        for key, val in zip(i_key, i_val):
            random_id.append(val['id'])
    id = random.sample(random_id, 1)
    return id[0]


if __name__ == '__main__':
    # another test model 'paraphrase-xlm-r-multilingual-v1'
    simi_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
    print("開始")
    print(cmp_t("排骨飯"))
    data = get_best_store("豆花")
    print(data)
