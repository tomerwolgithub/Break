import ujson as json
import os, re, string, jsonlines
from collections import Counter
from dateutil import parser

# ----- eval utils -----

def normalize_answer(s):
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score(prediction, ground_truth):
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    ZERO_METRIC = 0

    if normalized_prediction in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC
    if normalized_ground_truth in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return ZERO_METRIC
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def exact_match_score(prediction, ground_truth):
    return float(normalize_answer(prediction) == normalize_answer(ground_truth))


# ----- I/O utils -----

def read_file(file, verbose=False):
    if verbose:
        print(f'reading from {file}')
        
    if file.endswith('jsonl'):
        with jsonlines.open(file, 'r') as reader:
            return [d for d in reader.iter()]
    
    if file.endswith('json'):
        with open(file, encoding='utf8') as f:
            return json.load(f)

    if any([file.endswith(ext) for ext in ['pkl', 'pickle', 'pck', 'pcl']]):
        with open(file, 'rb') as f:
            return pickle.load(f)


def write_file(data, file, verbose=False):
    if verbose:
        print(f'writing to {file}')
        
    if file.endswith('jsonl'):
        with jsonlines.open(file, mode='w') as writer:
            writer.write_all(data)

    if file.endswith('json'):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    
    if any([file.endswith(ext) for ext in ['pkl', 'pickle', 'pck', 'pcl']]):
        with open(file, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def dirname(path):
    '''direc containing the file at path.'''
    direc = os.path.dirname(path)
    return f'{direc}/' if direc else './'

# -------- wikipedia utils ----------

def get_ent(s, nlp, only_longest=True):
    '''Input: s: query text similar to Wikipedia, nlp: spacy object.  
       Output: returns the named entities or None. 
       If only_longest==True then return only the longest one.
    '''
    tokenize = lambda s: [x.text for x in nlp.tokenizer(s)]
    tokens = tokenize(' '.join(s.strip().split()))
    # chunks of words starting with a capital
    # chunk of words within " ", ' '

    # central question word
    aux = ['am', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
           'do', 'does', 'did', 'will', 'would', 'shall',
           'should', 'can', 'could'] # 'VBD', 'VBZ', 'VBP', 'VBN'
    dt = ['this', 'the', 'an']
    vb = ['name'] # 'VB'
    wh = ['who', 'when', 'what', 'why', 'which', 'waht', 'whiich',
          'whom', 'where', 'how', 'whose'] # 'WP', 'WRB', 'WDT'
    Qwords = aux + dt + vb + wh
    
    # identify main ent indices
    _potential_ent_idx, start = [], 0
    for i, w in enumerate(tokens):
        if w == '.':
            start = i + 1
        if i == start and (w.lower() in Qwords+['in']):
            continue
        if (w[0].isalnum() and (w[0] == w[0].upper())) or (w in ['\'', '\"']):
            _potential_ent_idx.append(i)
            
    # allow ents to have stop words in between 
    potential_ent_idx = _potential_ent_idx[:]
    for i_p, i in enumerate(_potential_ent_idx[:-1]):
        j = _potential_ent_idx[i_p + 1]
        if all([w in ['in', 'of', 'at', 'on', 'a', 'the', 'v.', 'for', 'and', '&', ',', 'le', '!', '-', '\'s'] 
                for w in tokens[i+1:j]]):
            potential_ent_idx.extend(list(range(i+1, j)))
    potential_ent_idx.sort()
    
    # chunking for ents and spans
    ents, ent, ent_spans, ent_span = [], '', [], []
    for i_p, i in enumerate(potential_ent_idx):
        if i_p == 0 or ent == '':
            # new ent
            ent, ent_span = tokens[i], [i, i]
        elif potential_ent_idx[i_p - 1] == i-1:
            # continue ent
            ent += ' ' + tokens[i]
            ent_span[1] = i
        else:
            # end of ent
            is_nat = any([e.label_ == 'NORP' for e in nlp(ent).ents])
            if not is_nat and ent not in ['', '\'', '\"', 'Of', 'Between']:
                ents.append(ent); ent_spans.append(ent_span)
            # start new ent
            ent, ent_span = tokens[i], [i, i]
    is_nat = any([e.label_ == 'NORP' for e in nlp(ent).ents])
    if not is_nat and ent not in ['', '\'', '\"']:
        ents.append(ent); ent_spans.append(ent_span)
    if len(ents) > 0:
        if only_longest:
            # select the longest
            return sorted([(len(e), e) for e in ents])[-1][1]
        return ents
            
