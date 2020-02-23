#!/usr/bin/env python3
# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
"""A script to build the tf-idf document matrices for retrieval."""

import numpy as np
import scipy.sparse as sp
import argparse
import os, regex
import math
import logging
from sklearn.utils import murmurhash3_32
from tqdm import tqdm

from multiprocessing import Pool as ProcessPool
from multiprocessing.util import Finalize
from functools import partial
from collections import Counter

import ujson as json
import unicodedata
import spacy, jsonlines
import en_core_web_sm


# python build_tfidf.py --wiki ../data/wiki_firstpara_sents.jsonl
# concat title at beginning and then the usual filtering of ngrams

normalize = lambda text: unicodedata.normalize('NFD', text)
nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner'])

# will be set in main()
global wiki

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

DOC2IDX = None

def fetch_text(doc_id):
    return ' '.join(wiki[doc_id]['sents']).strip()

def tokenize(text):
    return [x.text for x in nlp.tokenizer(text)]

def hash(token, num_buckets):
    """Unsigned 32 bit murmurhash for feature hashing."""
    return murmurhash3_32(token, positive=True) % num_buckets


# ------------------------------------------------------------------------------
# Sparse matrix saving/loading helpers.
# ------------------------------------------------------------------------------

def save_sparse_csr(filename, matrix, metadata=None):
    data = {
        'data': matrix.data,
        'indices': matrix.indices,
        'indptr': matrix.indptr,
        'shape': matrix.shape,
        'metadata': metadata,
    }
    np.savez(filename, **data)

    
# ------------------------------------------------------------------------------
# Build article --> word count sparse matrix.
# ------------------------------------------------------------------------------

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've',
    'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven',
    'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren',
    'won', 'wouldn', "'ll", "'re", "'ve", "n't", "'s", "'d", "'m", "''", "``"
}

def filter_word(text):
    """Take out english stopwords, punctuation, and compound endings."""
    text = normalize(text)
    if regex.match(r'^\p{P}+$', text):
        return True
    if text.lower() in STOPWORDS:
        return True
    return False

def filter_fn(gram, mode='any'):
    """Decide whether to keep or discard an n-gram.
    Args:
        gram: list of tokens (length N)
        mode: Option to throw out ngram if
          'any': any single token passes filter_word
          'all': all tokens pass filter_word
          'ends': book-ended by filterable tokens
    """
    filtered = [filter_word(w) for w in gram]
    if mode == 'any':
        return any(filtered)
    elif mode == 'all':
        return all(filtered)
    elif mode == 'ends':
        return filtered[0] or filtered[-1]
    else:
        raise ValueError('Invalid mode: %s' % mode)


def count(n, hash_size, doc_id, cased):
    """Fetch the text of a document and compute hashed ngrams counts."""
    # doc_id is the page title
    global DOC2IDX
    row, col, data = [], [], []
    # Tokenize after prefixing the title to the text
    text = normalize(doc_id + '. ' + fetch_text(doc_id))
    tokens = tokenize(text) if cased else tokenize(text.lower())
    
    ngrams = [(s, e + 1) for s in range(len(tokens)) 
                         for e in range(s, min(s + n, len(tokens)))
                         if not filter_fn(tokens[s:e + 1])]
    # Concatenate into strings
    ngrams = ['{}'.format(' '.join(tokens[s:e])) for (s, e) in ngrams]

    # Hash ngrams and count occurences
    counts = Counter([hash(gram, hash_size) for gram in ngrams])

    # Return in sparse matrix data format.
    row.extend(counts.keys())
    col.extend([DOC2IDX[doc_id]] * len(counts))
    data.extend(counts.values())
    return row, col, data


def get_count_matrix(args):
    """Form a sparse word to document count matrix (inverted index).

    M[i, j] = # times word i appears in document j.
    """
    # Map doc_ids to indexes
    global DOC2IDX
    doc_ids = list(wiki.keys())  # all titles
    DOC2IDX = {doc_id: i for i, doc_id in enumerate(doc_ids)}

    # Compute the count matrix in steps (to keep in memory)
    logger.info('Mapping...')
    row, col, data = [], [], []
    for i, doc_id in enumerate(tqdm(doc_ids)):
        b_row, b_col, b_data = count(args.ngram, args.hash_size, doc_id, args.cased)
        row.extend(b_row)
        col.extend(b_col)
        data.extend(b_data)
    
    logger.info('Creating sparse matrix...')
    count_matrix = sp.csr_matrix(
        (data, (row, col)), shape=(args.hash_size, len(doc_ids))
    )
    count_matrix.sum_duplicates()
    return count_matrix, (DOC2IDX, doc_ids)


# ------------------------------------------------------------------------------
# Transform count matrix to different forms.
# ------------------------------------------------------------------------------


def get_tfidf_matrix(cnts):
    """Convert the word count matrix into tfidf one.

    tfidf = log(tf + 1) * log((N - Nt + 0.5) / (Nt + 0.5))
    * tf = term frequency in document
    * N = number of documents
    * Nt = number of occurences of term in all documents
    """
    Ns = get_doc_freqs(cnts)
    idfs = np.log((cnts.shape[1] - Ns + 0.5) / (Ns + 0.5))
    idfs[idfs < 0] = 0
    idfs = sp.diags(idfs, 0)
    tfs = cnts.log1p()
    tfidfs = idfs.dot(tfs)
    return tfidfs


def get_doc_freqs(cnts):
    """Return word --> # of docs it appears in."""
    binary = (cnts > 0).astype(int)
    freqs = np.array(binary.sum(1)).squeeze()
    return freqs


# ------------------------------------------------------------------------------
# Main.
# ------------------------------------------------------------------------------


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ngram', type=int, default=2,
                        help=('Use up to N-size n-grams '
                              '(e.g. 2 = unigrams + bigrams)'))
    parser.add_argument('--hash-size', type=int, default=int(math.pow(2, 24)),
                        help='Number of buckets to use for hashing ngrams')
    parser.add_argument('--cased', type=bool, default=False)
    parser.add_argument('--wiki', type=str, default='../data/wiki_firstpara_sents.jsonl')
    args = parser.parse_args()

    logging.info('reading wiki data...')
    with jsonlines.open(args.wiki, 'r') as reader:
        wiki = {d['title']: d['para'] for d in tqdm(reader.iter())}
#         wiki = {}
#         for d in tqdm(reader.iter()):
#             wiki[d['title']] = d['para']
#             if len(wiki) > 1000:
#                 break
                
    logging.info('Counting words...')
    count_matrix, doc_dict = get_count_matrix(args)

    logger.info('Making tfidf vectors...')
    tfidf = get_tfidf_matrix(count_matrix)

    logger.info('Getting word-doc frequencies...')
    freqs = get_doc_freqs(count_matrix)

    basename = ('wiki_first_paras-tfidf-ngram=%d-hash=%d-tokenizer=%s%s' %
                 (args.ngram, args.hash_size, 'spacy', '-cased' if args.cased else ''))
    filename = f'{os.path.dirname(args.wiki)}/{basename}' if os.path.dirname(args.wiki) else basename
    
    logger.info('Saving to %s.npz' % filename)
    metadata = {
        'doc_freqs': freqs,
        'hash_size': args.hash_size,
        'ngram': args.ngram,
        'doc_dict': doc_dict
    }
    save_sparse_csr(filename, tfidf, metadata)

# file will be saved in the same dir as --wiki
'''python build_tfidf.py --wiki ../data/wiki_firstpara_sents.jsonl  
outputs wiki_first_paras-tfidf-ngram=2-hash=16777216-tokenizer=spacy.npz'''