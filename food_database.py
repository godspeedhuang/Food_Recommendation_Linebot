import pandas as pd
import json

word_list = pd.read_csv(r'dataset\n_sumary.csv')
n_segment = pd.read_csv(
    r'dataset\combine_2_subject_food_emotion_positive_n_data.csv')

n_name = list(n_segment['name'])
n_n = list(n_segment['n'])
n_place_id = list(n_segment['place_id'])


data = []


# for i in word_list['單詞']:


def word_data(w):
    n[w] = []
    for j in range(len(n_name)):
        if w in n_n[j]:
            store = {}
            d = 0
            if len(n[w]) != 0:
                for i in n[w]:
                    # print(i)
                    if n_name[j] == i['name']:
                        i['count'] += 1
                        d += 1
                    else:
                        store['name'] = n_name[j]
                        store['id'] = n_place_id[j]
                        store['count'] = 1
            if len(n[w]) == 0:
                store['name'] = n_name[j]
                store['id'] = n_place_id[j]
                store['count'] = 1
            # if store
            if d == 0:
                n[w].append(store)


def data_max(n, w):
    max = 0
    for i in n[w]:
        if(i['count'] > max):
            max = i['count']
            data = i
    return data


w_list = list(word_list['單詞'])
# print(w_list)


for i in w_list:
    n = {}
    word_data(i)
    max_d = data_max(n, i)
    n[i] = max_d
    data.append(n)

# print(n)
# data.append(n)


with open("database_1_max.json", mode='w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False)
# # print(data)


# print(n)


# data = pd.read_csv("dataset\combine_2_subject_food_emotion_positive_n.csv")

# word_list = []

# for i in data['pos_n']:
#     w_list = str(i).split(",\u3000")
#     # i = list(i)
#     for t in w_list:
#         word_list.append(t)

# df = pd.DataFrame(word_list)
# print(df)

# df.to_csv("word_list.csv")

# with open("store_dataset.json", mode='r', encoding='utf-8') as file:
#     data = json.load(file)

# data_n = pd.read_csv("dataset\combine_2_subject_food_emotion_positive_n.csv")


# name_list = []
# place_id_list = []
# for i in data_n['label']:
#     for j in data:
#         url = j['result']['url']
#         if i == url:
#             name = j['result']['name']
#             place_id = j['result']['place_id']
#     name_list.append(name)
#     place_id_list.append(place_id)

# data_n['name'] = name_list
# data_n['place_id'] = place_id_list
# print(data_n['name'])
# print(data_n['place_id'])
# data_n.to_json("combine_2_food_n_data.json")
