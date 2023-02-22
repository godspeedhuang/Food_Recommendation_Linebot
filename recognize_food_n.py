from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
import pandas as pd


def pack_ws_pos_sentece(sentence_ws, sentence_pos):
    assert len(sentence_ws) == len(sentence_pos)
    res = []
    for word_ws, word_pos in zip(sentence_ws, sentence_pos):
        if(word_pos == 'Na'):
            res.append(f"{word_ws} ")
    return "\u3000".join(res)


# Show results(contain NER)
# for sentence, sentence_ws, sentence_pos, sentence_ner in zip(text, ws, pos, ner):
#     print(sentence)
#     print(pack_ws_pos_sentece(sentence_ws, sentence_pos))
#     for entity in sentence_ner:
#         print(entity)
#     print()
if __name__ == "__main__":
    # data = pd.read_csv(r"dataset\food_positve.csv")
    # text_list = [i for i in data['caption']]
    # print(text_list)
    # Initialize drivers
    ws_driver = CkipWordSegmenter(level=3)
    pos_driver = CkipPosTagger(level=3)
    ner_driver = CkipNerChunker(level=1)

    text = ["擔仔麵的味道很純厚，讓人想一直吃下去！"]
    ws = ws_driver(text)
    pos = pos_driver(ws)
    ner = ner_driver(text)
    for sentence, sentence_ws, sentence_pos, sentence_ner in zip(text, ws, pos, ner):
        print(sentence)
        print(pack_ws_pos_sentece(sentence_ws, sentence_pos))
        for entity in sentence_ner:
            print(entity)
        print()
