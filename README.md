# 食在好用-台南美食推薦機器人
- [專案簡介](#專案簡介)
- [使用流程](#使用流程)
- [建置過程](#建置過程)
- [檔案架構](#檔案架構)
- [其他](#其他)

----
## 專案簡介
此專案為成功大學敏求智慧學院 `聊天機器人之互動設計` 課程期末專題報告。
以交通部精選之台南市觀光餐飲店約150家為基礎，爬取每家餐飲店的google評論內容與星級進行NLP語言模型訓練，針對各條評論的`主題與情緒`進行分類標記後進行模型訓練，最終部署於Line聊天機器人上，詳細專案內容及實際Demo影片可參考以下連結。

- [介紹及Demo影片](https://youtu.be/XwzXm0-V7Q8)
- [專案簡報](https://ncku365-my.sharepoint.com/:p:/g/personal/f24076182_ncku_edu_tw/EQv2qIagAthNobIF0u2i92gBUtteD9s-hAx_nXZW9sMnVw?e=xZEcmt)

## 使用流程
### 步驟一：使用者點選聊天畫面中的 `查詢目前所在位置`，提供地理座標系統給後端程式。
![頁面1](/images/Slide4.JPG)
### 步驟二：使用者點選目前所使用的交通運具，用意為限縮推薦餐廳之所在範圍，不同運具對應不同的環域範圍。
![頁面2](/images/Slide5.JPG)
### 步驟三：聊天機器人詢問請問你想吃什麼，使用者可 `隨意回答` 任何可能之回答，回傳後端後將交由NLP模型進行判斷。
![頁面3](/images/Slide6.JPG)
### 步驟四：NLP模型會針對上述語句做二個面向的判斷，一是 `主題` (價格/服務/食物/環境/地點/其他)，二是 `情緒` (正面/中立/負面)，之後針對句子做各項詞句標記，用意系為了找到`食物主題之名詞`，最終由上述這三個資訊和後端資料庫進行比對，找出相似度最高且評分最高的餐飲店進行推薦。
![頁面4](/images/Slide7.JPG)
### 例外情況一：若輸入之食物不在資料庫內，聊天機器人將自動將其透過 `Google Places API` 進行搜尋並回傳評分最高之餐廳，因此即便使用者想吃的食物不在資料庫內也能進行推薦，是避免機器人癱瘓之保護機制之一，
![頁面5](/images/Slide8.JPG)
### 下圖顯示各種回應對應之主題，本聊天機器人目前`僅支援美食主題`，其他尚未建置相關資料庫，且若使用者隨意回答與問題不相關之回應將會被引導回最初的問題。
![頁面6](/images/Slide9.JPG)
### 若使用者用排除法回答問題(例如:我不想吃...以外都可以)，聊天機器人也能針對其情緒進行相對應的排除，並進行隨機推薦，若使用者不喜歡該推薦，聊天機器人也可以持續進行其他推薦。
![頁面7](/images/Slide10.JPG)

## 建置過程
以下為資料庫建置與模型訓練過程簡介
### 一、透過交通部API鎖定位於台南的知名觀光餐飲餐廳，總數約150家以上。
![頁面1](/images/Slide11.JPG)
### 二、以下為Google評論爬蟲之過程與評論資料之整理格式。
![頁面2](/images/Slide12.JPG)
### 三、Google評論內容的前處理過程，針對主題、情緒與食物品項進行標記。
![頁面3](/images/Slide13.JPG)
### 四、標記1600+後進行模型訓練，透過訓練後之模型分類50000+評論，最終輸出模型並部署於Line聊天機器人的後端程式中。
![頁面4](/images/Slide14.JPG)

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

<!-- ## Docker 建置 -->

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
