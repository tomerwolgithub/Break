import os
import ujson as json
import argparse

import numpy as np
from tqdm import tqdm
import en_core_web_sm

from utils import read_file, write_file, dirname


nlp = en_core_web_sm.load()  # spacy 


def save(args, data):
    out_file = args.out_file
    os.makedirs(dirname(out_file), exist_ok=True)
    write_file({'data': data}, out_file, verbose=True)

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file', type=str, default='./data/hotpot_data/hotpot_train_v1.json')
    parser.add_argument('--max_n_samples', type=int, default=-1)
    parser.add_argument('--n_distractors', type=int, default=8)
    parser.add_argument('--sorted_titles_hotpot', type=str, default='')
    parser.add_argument('--data_type', type=str, default='dev')
    parser.add_argument('--out_file', type=str, default='./examples_data/train.json')
    args = parser.parse_args()

    data = load_hotpot(args)
    save(args, data)

    
def load_hotpot(args):
    data = read_file(args.data_file, verbose=True)
    l_sorted_titles = None
    if args.sorted_titles_hotpot.strip():
        l_sorted_titles = read_file(args.sorted_titles_hotpot.strip(), verbose=True)
    
    def _process_sent(sent):
        if type(sent) != str:
            return [_process_sent(s) for s in sent]
        return sent.replace('–', '-').replace('&', 'and').replace('&amp;', 'and')

    print('converting hotpot data to squad format...')
    data_list, n_with_ans = [], 0
    for article_id, article in enumerate(tqdm(data)):
        if args.max_n_samples > 0 and article_id >= args.max_n_samples:
            break
            
        paragraphs = article['context']
        if l_sorted_titles:
            # sort the paras acc to td-idf sim wrt question: closest first
            paragraphs.sort(key=lambda p: l_sorted_titles[article['_id']].index(p[0]))
        
        gold_titles = {x[0] for x in article['supporting_facts']}
        
        if args.data_type == 'train' and l_sorted_titles:          
            # for train set only keep top n_distractors
            distractors = [t for t in l_sorted_titles[article['_id']] if t not in gold_titles]
            keep = gold_titles.union(distractors[:args.n_distractors])
            paragraphs = [p for p in paragraphs if p[0] in keep]
            
        sfs = [(_process_sent(t), s) for t, s in article['supporting_facts']]
        question = article['question']
        answer = article['answer'].strip()

        contexts, answers, offset = [], [], 0
        for para_idx, para in enumerate(paragraphs):
            title, sents = _process_sent(para[0]), para[1]
            is_gold = title in gold_titles
            
            for sent_idx, sent in enumerate(sents):
                if sent_idx == 0:
                    contexts.append("<aug> yes no </aug> <title> %s </title> %s" % (
                                                    title.lower().strip(), sent.lower().strip()))
                else:
                    contexts.append(sent.lower().strip())
                is_sf = (title, sent_idx) in sfs
                if args.data_type != 'train' or is_sf or (is_gold and answer.lower().strip() in ['yes', 'no']):
                    # for train set we pick the answer as the one occuring in supporting facts
                    # for train set we pick the yes/no answers as the ones prefixed to gold paras
                    # for dev set all valid answer spans are allowed 
                    if answer.lower() in contexts[-1]:
                        curr_answers = find_span_from_text(contexts[-1], 
                                                           [w.text for w in nlp.tokenizer(contexts[-1])], 
                                                           answer.lower())
                        for i, curr_answer in enumerate(curr_answers):
                            curr_answers[i]['answer_start'] += offset
                        answers += curr_answers
                offset += len(contexts[-1]) + 1
        
        context = " ".join(contexts)    
        n_with_ans += int(len(answers) > 0)
        
        for a in answers:
            assert a['text'] == context[a['answer_start']:a['answer_start']+len(a['text'])]

        if args.data_type == 'train':  # only keep one answer for train set as required by train-squad script 
            answers = answers[:1]
            if not answers:
                continue
    
        paragraph = {
                'context': context,
                'qas': [{
                    'question': question,
                    'answers': answers,
                    'id': article['_id'],
                    'final_answer': answer,
                    'type': article['type']
                }]
            }
        data_list.append({'paragraphs': [paragraph]})
    
    print('ans found in %d samples out of %d' % (n_with_ans, len(data)))
    return data_list


def find_span_from_text(context, tokens, answer):
    
    if answer not in context:
        return []

    offset = 0
    spans = []
    scanning = None
    process = []

    for i, token in enumerate(tokens):
        while context[offset:offset+len(token)] != token:
            offset += 1
            if offset >= len(context):
                break
        if scanning is not None:
            end = offset + len(token)
            if answer.startswith(context[scanning[-1]:end]):
                if context[scanning[-1]:end] == answer:
                    spans.append(scanning[0])
                elif len(context[scanning[-1]:end]) >= len(answer):
                    scanning = None
            else:
                scanning = None
        if scanning is None and answer.startswith(token):
            if token == answer:
                spans.append(offset)
            if token != answer:
                scanning = [offset]
        offset += len(token)
        if offset >= len(context):
            break
        process.append((token, offset, scanning, spans))

    answers = []

    for span in spans:
        if context[span:span+len(answer)] != answer:
            print (context[span:span+len(answer)], answer)
            print (context)
            assert False
        answers.append({'text': answer, 'answer_start': span})
    return answers


if __name__ == '__main__':
    main()

'''
# for hotpot finetuning
# python hotpot_to_squad2.py --max_n_samples -1 --n_distractors 8 --data_type train --sorted_titles_hotpot ../data/hotpot_data/sorted_titles_train_distdev.json --data_file ../data/hotpot_data/hotpot_train_v1.json --out_file ./examples_data/train.json
# python hotpot_to_squad2.py --max_n_samples -1 --n_distractors 8 --data_type dev --sorted_titles_hotpot ../data/hotpot_data/sorted_titles_train_distdev.json --data_file ../data/hotpot_data/hotpot_dev_distractor_v1.json --out_file ./examples_data/dev.json

# for bert rc
# python hotpot_to_squad2.py --max_n_samples -1 --data_type dev --data_file ../data/hotpot_data/hotpot_for_ques_ir_gold.json --out_file ./examples_data/bert_rc_eval.json
'''