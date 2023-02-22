import glob
from typing import Text
import pandas as pd
import emoji
import re

# 1. 先把空字串、google翻譯字串清除
# 2. 合併成一個檔案
# 3. 建立斷句標準
# 4. 太長或太短的就刪除


def __delete_emoji(data):
    """刪除表情符號"""
    for i in range(len(data['caption'])):
        try:
            txt = emoji.demojize(data.iloc[i, 3])
            result = re.sub(r"(:\S+:)", " ", txt)
            data.iloc[i, 3] = result
            # print(data.iloc[i, 3])
        except:
            pass
    return data


def __clear_data(data):
    """刪除空字串、非中文評論"""
    # 刪除空字串
    # data = data.dropna(axis=0, how='any', subset=[3])
    # 刪除多餘欄位
    # data = data.drop(
    #     ["language_select", "n_review_user", "n_photo_user"], axis=1)
    # 刪除googel翻譯
    index_c = 0
    try:
        for i in data['caption']:
            if(type(i) == str):
                # text = emoji.demojize(i)
                # result = re.sub(r":\S+", "", text)
                # i = result
                if("由 Google 提供翻譯" in i):
                    data = data.drop(index=int(index_c))
            else:
                data = data.drop(index=int(index_c))
            index_c += 1
    except:
        print(data['place_name'])
    data.reset_index(inplace=True, drop=True)
    return data


def __segment_by_period(data, mark):
    """針對各種標記進行標記"""
    tmp = pd.DataFrame(columns=["place_name", "id_review", "caption", "language_select", "relative_date",
                                "retrieval_date", "rating", "username", "n_review_user", "n_photo_user", "url_user", "url_source"])
    drop_list = list()
    for i in range(len(data['caption'])):
        try:
            if(mark in data.iloc[i, 2]):
                seg_list = (data.iloc[i, 2].split(mark))
                for j in seg_list:
                    if(len(j) > 0):
                        if(mark != "但"):
                            j += mark
                        j = j.strip()
                        append_list = [(data.iloc[i, 0], data.iloc[i, 1],  j, data.iloc[i, 3],  data.iloc[i, 4], data.iloc[i, 5],
                                        data.iloc[i, 6], data.iloc[i, 7], data.iloc[i, 8], data.iloc[i, 9], data.iloc[i, 10], data.iloc[i, 11])]
                        df_append = pd.DataFrame(append_list, columns=["place_name", "id_review", "caption", "language_select", "relative_date",
                                                                       "retrieval_date", "rating", "username", "n_review_user", "n_photo_user", "url_user", "url_source"])
                        # print(df_append['caption'])
                        tmp = tmp.append(df_append, ignore_index=True)
                drop_list.append(i)
        except:
            pass
    data = data.append(tmp, ignore_index=True)
    data = data.drop(index=drop_list)
    return data


if __name__ == "__main__":
    data = pd.read_csv("dataset\combine_1_untag.csv")
    data = __delete_emoji(data)
    data.to_csv("dataset\combine_2_untag.csv")
    # df = pd.DataFrame(columns=["place_name", "id_review", "caption", "language_select", "relative_date",
    #                            "retrieval_date", "rating", "username", "n_review_user", "n_photo_user", "url_user", "url_source"])
    # for file in glob.glob(r"data\*.csv"):
    #     data = pd.read_csv(file)
    #     data = __clear_data(data)
    #     data = __segment_by_period(data, "。")
    #     data = __segment_by_period(data, "!")
    #     data = __segment_by_period(data, "！")
    #     data = __segment_by_period(data, "~")
    #     data = __segment_by_period(data, "～")
    #     data = __segment_by_period(data, "但")
    #     df = df.append(data, ignore_index=True)

    # df.to_csv(r"combine.csv")
