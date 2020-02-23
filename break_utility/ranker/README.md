#### Building a tf-idf ranker over a set of documents.

The code is mostly modified from [DrQA](https://github.com/facebookresearch/DrQA).

The corpus should be a list of dicts each having a title and sentences like in `sample.jsonl`. For our experiments, we converted the Wikipedia (only introductory paras) as provided at [HotpotQA wiki](https://hotpotqa.github.io/wiki-readme.html).

After navigating to the `ranker` directory, a td-idf matrix (uncased) can be built using :
```
python build_tfidf.py --wiki ../data/wiki_firstpara_sents.jsonl
```
The output `wiki_first_paras-tfidf-ngram=2-hash=16777216-tokenizer=spacy.npz` will be saved in the same dir as `--wiki`. The corpus will be loaded in the RAM so make sure to have sufficient memory.

Contact: [Ankit Gupta](https://github.com/ag1988).

