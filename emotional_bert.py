import torch
from transformers import BertTokenizer, BertForSequenceClassification
from IPython.display import clear_output
import pandas as pd

from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.nn.utils.rnn import pad_sequence

PRETRAINED_MODEL_NAME = "bert-base-chinese"  # 指定繁簡中文 BERT-BASE 預訓練模型

# 取得此預訓練模型所使用的 tokenizer
tokenizer = BertTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)

# clear_output()
# print("PyTorch 版本：", torch.__version__)


class Review_Emotional(Dataset):
    # 讀取前處理後的 tsv 檔並初始化一些參數
    def __init__(self, mode, tokenizer):
        # assert mode in ["train", "test"]  # 一般訓練你會需要 dev set
        self.mode = mode
        # 大數據你會需要用 iterator=True
        self.df = pd.read_csv(mode + ".tsv", sep="\t").fillna("")
        self.len = len(self.df)
        self.label_map = {'負面': 0, '中立': 1, '正面': 2}
        self.tokenizer = tokenizer  # 我們將使用 BERT tokenizer

    # 定義回傳一筆訓練 / 測試數據的函式
    def __getitem__(self, idx):
        if self.mode == "response_emotion":
            text, label = self.df.iloc[idx, :].values
            label_tensor = None
        else:
            text, label = self.df.iloc[idx, :].values
            # 將 label 文字也轉換成索引方便轉換成 tensor
            label_id = self.label_map[label]
            label_tensor = torch.tensor(label_id)

        # 建立第一個句子的 BERT tokens 並加入分隔符號 [SEP]
        word_pieces = ["[CLS]"]
        tokens_a = self.tokenizer.tokenize(text)
        word_pieces += tokens_a + ["[SEP]"]
        len_a = len(word_pieces)

        # 將整個 token 序列轉換成索引序列
        ids = self.tokenizer.convert_tokens_to_ids(word_pieces)
        tokens_tensor = torch.tensor(ids)

        # 將第一句包含 [SEP] 的 token 位置設為 0，其他為 1 表示第二句
        segments_tensor = torch.tensor([0] * len_a, dtype=torch.long)

        return (tokens_tensor, segments_tensor, label_tensor)

    def __len__(self):
        return self.len


def e_create_mini_batch(samples):
    tokens_tensors = [s[0] for s in samples]
    segments_tensors = [s[1] for s in samples]

    # 測試集有 labels
    if samples[0][2] is not None:
        label_ids = torch.stack([s[2] for s in samples])
    else:
        label_ids = None

    # zero pad 到同一序列長度
    tokens_tensors = pad_sequence(tokens_tensors,
                                  batch_first=True)
    segments_tensors = pad_sequence(segments_tensors,
                                    batch_first=True)

    # attention masks，將 tokens_tensors 裡頭不為 zero padding
    # 的位置設為 1 讓 BERT 只關注這些位置的 tokens
    masks_tensors = torch.zeros(tokens_tensors.shape,
                                dtype=torch.long)
    masks_tensors = masks_tensors.masked_fill(
        tokens_tensors != 0, 1)

    return tokens_tensors, segments_tensors, masks_tensors, label_ids


def e_get_predictions(model, dataloader, compute_acc=False):
    predictions = None
    correct = 0
    total = 0

    with torch.no_grad():
        # 遍巡整個資料集
        for data in dataloader:
            # 將所有 tensors 移到 GPU 上
            if next(model.parameters()).is_cuda:
                data = [t.to("cuda:0") for t in data if t is not None]

            # 別忘記前 3 個 tensors 分別為 tokens, segments 以及 masks
            # 且強烈建議在將這些 tensors 丟入 `model` 時指定對應的參數名稱
            tokens_tensors, segments_tensors, masks_tensors = data[:3]
            outputs = model(input_ids=tokens_tensors,
                            token_type_ids=segments_tensors,
                            attention_mask=masks_tensors)

            logits = outputs[0]
            _, pred = torch.max(logits.data, 1)

            # 用來計算訓練集的分類準確率
            if compute_acc:
                labels = data[3]
                total += labels.size(0)
                correct += (pred == labels).sum().item()

            # 將當前 batch 記錄下來
            if predictions is None:
                predictions = pred
            else:
                predictions = torch.cat((predictions, pred))

    if compute_acc:
        acc = correct / total
        return predictions, acc
    return predictions


def e_convert2tsv(txt):
    df = pd.DataFrame(columns=['text', 'label'])
    df['text'] = [txt]
    df['label'] = ["test"]
    df.to_csv("response_emotion.tsv", sep="\t", index=False)


if __name__ == "__main__":
    model = BertForSequenceClassification.from_pretrained("_model")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    # # df_test = pd.read_csv("test_1.csv")
    # # df_test = df_test.loc[:, ["caption", 'subject']]
    # # df_test.columns = ["text", 'label']
    # # df_test.to_csv("test.tsv", sep="\t", index=False)
    # # print("預測樣本數：", len(df_test))

    txt = "賽車場有好多人"
    e_convert2tsv(txt)

    testset = Review_Emotional("response_emotion", tokenizer=tokenizer)
    testloader = DataLoader(testset, batch_size=16,
                            collate_fn=e_create_mini_batch)

    # 用分類模型預測測試集
    predictions = e_get_predictions(model, testloader)
    index_map = {v: k for k, v in testset.label_map.items()}
    predictions.tolist()
    df = pd.DataFrame({"label": predictions.tolist()})
    df['label_pre'] = df.label.apply(lambda x: index_map[x])
    df_pred = pd.concat([testset.df.loc[:, ["text"]],
                         df.loc[:, 'label_pre']], axis=1)
    # print(type(df_pred[0, 'label_pre']))
    # print(df_pred[0, 'label_pre'])
    for i in df_pred['label_pre']:
        print(str(i))
