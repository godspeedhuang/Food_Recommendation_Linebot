# 食在好用-台南美食推薦機器人

## 專案簡介

![頁面4](/images/Slide4.JPG)
![](/images/Slide5.JPG)
![](/images/Slide6.JPG)
![](/images/Slide7.JPG)
![](/images/Slide8.JPG)
![](/images/Slide9.JPG)
![](/images/Slide10.JPG)
## 檔案架構

```bash
Final Project
    ├── app.py                    # LineBot主程式
    ├── view.py                   # LineBot回應內容
    ├── emotional_bert.py         # 情緒分類模型(正面/中立/負面)
    ├── response_emotion.tsv      # 使用者傳入訊息紀錄
    ├── emotional_model/          # 預訓練情緒模型
    │    ├── pytorch_model.bin
    │    └── config.json
    ├── subject_bert.py           # 主題分類模型(食物/環境/價錢/服務/地點/其他)
    ├── response.tsv              # 使用者傳入訊息紀錄
    ├── subject_model/            # 預訓練主題模型
    │    ├── pytorch_model.bin
    │    └── config.json
    ├── recognize_food_n.py       # 擷取開放式回應中"名詞內容"
    ├── compute_n_silimar.py      # 計算該名詞與資料庫中"名詞相似度"
    ├── food_database.py          # 店家、美食品項資料庫建置
    ├── database_1.json           # 美食資料庫
    ├── database_1_max.json
    ├── google_api_dataset.json   # 店家資料庫
    ├── review_preprocess.py      # 評論資料前處理
    ├── dataset/                  # 處理後評論資料集
    │    └── ...
    ├── data/                     # 處理前評論資料集
    │    └── ...
    ├── config.ini
    ├── Dockerfile
    └── requirements.txt
```

## Docker 建置

<!-- - 步驟一：將 dockerfile 打包成 image

```bash
$ docker build -t final_project .
# docker build -t {image_name} {currect_folder}
```

- 步驟二：透過 image 產生 container

```bash
$ docker run -d -p 80:8082 --name final final_project
# -d 背景執行
# -p 將主機80port與container的 8082 port 綁定
# --name container名稱 -->
<!-- ``` -->

## Other Code From Colab

- 情緒模型訓練: https://colab.research.google.com/drive/1lSt67rvvuMsUizAnNsX81lLiy8WsgdPT?usp=sharing
- 主題模型訓練:
  https://colab.research.google.com/drive/1y8krqcxPTxV1-6jX5ZXRITWSx7FGuEuv?usp=sharing
- Calculate N similarity:
  - Using Bert-base-chinese/CKIP transformer: https://colab.research.google.com/drive/1IV1lUzXyGIm68ytvH3yH10CWLyuSaiK-?usp=sharing
  - Using Sentense Transformers' distiluse-base-multilingual-cased-v2:https://colab.research.google.com/drive/1SeuwuAvQzNu6swZnzgLDXW_59M0YkinY?usp=sharing
