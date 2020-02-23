import numpy as np
from ranker.tfidf_doc_ranker import TfidfDocRanker

class IR:
    def __init__(self, tfidf_path='data/wiki_first_paras-tfidf-ngram=2-hash=16777216-tokenizer=spacy.npz', 
                 cased=False):
        self.ranker = TfidfDocRanker(tfidf_path=tfidf_path, cased=cased)
        self.all_titles = self.ranker.doc_dict[0]

    def closest_docs(self, s, k=10):
        '''Input: s: query text, k: num of titles to return in decreasing order or similarity.
           Output: (titles, scores)
        '''
        try:
            return self.ranker.closest_docs(s, k=k)
        except RuntimeError:
            # invalid query: pad and retry
            return self.ranker.closest_docs(s + ' pad', k=k)
    
    def rank_titles(self, query, titles):
        '''Input: query: text, titles: iterable containing titles to rank
           Output: dict of title:score
        '''
        ranker = self.ranker
        scores = {title: 0 for title in titles}
        try:
            res = ranker.text2spvec(query) * ranker.doc_mat
        except RuntimeError:
            return scores
        relevant_inds = set(res.indices)
        for title in titles:
            idx = ranker.get_doc_index(title)
            if idx in relevant_inds:
                scores[title] = res.data[np.where(res.indices == idx)][0]
        return scores