import re, string
from collections import Counter
from dateutil import parser

# ------ comparison utils ----------

def get_type(s):
    try:
        dt = parser.parse(s)
        return dt, 'date'
    except ValueError:
        # not date
        try:
            flt = float(s)
            return flt, 'float'
        except ValueError:
            # not float
            return s, 'str'

        
def first_arg_smaller(s0, s1):
    # earlier, first, old, low, less, close
    # not: more, new, great, high, large, long, tall
    s0, type0 = get_type(s0)
    s1, type1 = get_type(s1)
    if type0 == 'date' and type1 == 'date':
        return s0 <= s1
    if type0 == 'float' and type1 == 'float':
        return s0 <= s1
    return str(s0) <= str(s1)


def compare(last_part, s0, s1):
    order = [0, 1] if first_arg_smaller(s0, s1) else [1, 0]
    if any(k in last_part for k in ['earlier', 'first', 'old', 'low', 'less', 'close']):
        return order[0]
    return order[1]


# -------- data format conversion --------------

def to_squad(article):
    '''convert HotpotQA format to SQuAD format'''
    def _process_sent(sent):
        if type(sent) != str:
            return [_process_sent(s) for s in sent]
        return sent.replace('–', '-').replace('&', 'and').replace('&amp;', 'and')

    paragraphs = article['context']
    question = _process_sent(article['question'].strip()).lower()
    answer = article['answer'].strip()
    contexts_list, answers_list = [], []
    
    for para_idx, para in enumerate(paragraphs):
        title = _process_sent(para[0])
        content = para[1]
        answers = []
        contexts = ["{} {} {}".format("<title>", title.lower().strip(), "</title>")]
        offset = len(contexts[0]) + 1

        for sent_idx, sent in enumerate(content):
            contexts.append(sent.lower().strip())
            offset += len(contexts[-1]) + 1

        if len(contexts) > 1:
            context = " ".join(contexts)
            contexts_list.append(context)
            answers_list.append(answers)

    assert len(contexts_list) > 1
    assert len(contexts_list) == len(answers_list)

    paragraph = {
            'context': contexts_list,
            'qas': [{
                'final_answers': [answer],
                'question': question,
                'answers': answers_list,
                'id': article['_id'],
                'type': article['type']
            }]
        }
    return {'paragraphs': [paragraph]}