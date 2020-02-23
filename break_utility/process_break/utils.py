"""
# @Time    : 2020/2/23
# @Author  : Wolfson
"""

import spacy


def extract_noun_phrases(sentence):
    """Extracts the NPs in the sentence, by order of appearance
    
    Parameters
    ----------
    sentence : str
        English sentence
    
    Returns
    -------
    list
        returns list of sentence noun phrases,
        by order of appearance
    """
    noun_phrases = []
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(sentence)
    for np in doc.noun_chunks:
        noun_phrases += [np.text]
    if(len(noun_phrases) == 0):
        tokens = sentence.split()
        if len(tokens) > 1:
            sentence = ' '.join(tokens[1:])
            doc = nlp(sentence)
            for np in doc.noun_chunks:
                noun_phrases += [np.text]
            if(len(noun_phrases) == 0):
                return [tokens[1]]
        else:
            return [tokens[0]]
    return noun_phrases