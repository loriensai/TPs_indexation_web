from rank_bm25 import BM25Okapi

corpus = [
    "Hello there good man!"
]

tokenized_corpus = [doc.split(" ") for doc in corpus]
print(tokenized_corpus)

bm25 = BM25Okapi(tokenized_corpus)
# <rank_bm25.BM25Okapi at 0x1047881d0>

query = "windy London"
tokenized_query = query.split(" ")

doc_scores = bm25.get_scores(tokenized_query)
print(doc_scores)