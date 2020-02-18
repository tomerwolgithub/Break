import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import inflect
import pandas as pd
import json
import logging


"""
Receives csv of NL questions, and generates the 'store.js' file for the AMT app.
The store contains info on the question id, text, and valid annotation tokens
"""

p = inflect.engine()
wordnet_lemmatizer = WordNetLemmatizer()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Question(object):
    """
    class representing dataset question
    """
    def __init__(self, index, text, valid_tokens):
        self.index = index
        self.text = text.replace('"', '').replace('\\', '')
        self.valid_tokens = valid_tokens
        
    def get_index(self):
        return self.index
    
    def get_text(self):
        return self.text
    
    def get_valid_tokens(self):
        return self.valid_tokens
    
    def set_text(self, new_text):
        self.text = new_text
    
    def set_valid_tokens(self, new_tokens):
        self.valid_tokens = new_tokens
            
    def store_json(self):
        tokens_string = generate_json_tokens(self.valid_tokens)
        string = "\t{\n\t\t\"id\": \"%s\", \n\t\t\"text\": \"%s\", \n\t\t\"valid_tokens\": %s\n\t}, \n" % (self.index, self.text, tokens_string)
        return string


# Just to make it a bit more readable
WN_NOUN = 'n'
WN_VERB = 'v'
WN_ADJECTIVE = 'a'
WN_ADJECTIVE_SATELLITE = 's'
WN_ADVERB = 'r'


def convert(word, from_pos, to_pos):    
    """ Transform words given from/to POS tags """

    synsets = wn.synsets(word, pos=from_pos)

    # Word not found
    if not synsets:
        return []

    # Get all lemmas of the word (consider 'a' and 's' equivalent)
    lemmas = []
    for s in synsets:
        for l in s.lemmas():
            if s.name().split('.')[1] == from_pos or from_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE) and s.name().split('.')[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE):
                lemmas += [l]

    # Get related forms
    derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in lemmas]

    # filter only the desired pos (consider 'a' and 's' equivalent)
    related_noun_lemmas = []

    for drf in derivationally_related_forms:
        for l in drf[1]:
            if l.synset().name().split('.')[1] == to_pos or to_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE) and l.synset().name().split('.')[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE):
                related_noun_lemmas += [l]

    # Extract the words from the lemmas
    words = [l.name() for l in related_noun_lemmas]
    len_words = len(words)

    # Build the result in the form of a list containing tuples (word, probability)
    result = [(w, float(words.count(w)) / len_words) for w in set(words)]
    result.sort(key=lambda w:-w[1])

    # return all the possibilities sorted by probability
    return result

    
def noun_inflections(sentence):
    """
    input: sentence string
    output: list of sentence nouns
    """
    nouns = []
    text = word_tokenize(sentence)
    parse = nltk.pos_tag(text)
    for token,pos in parse:
        # insert noun inflection
        if pos == 'NN':
            nouns += [inflect_plural(token)]
        elif pos == 'NNS':
            nouns += [inflect_singular(token)]
    return nouns

def inflect_plural(singular):
    """
    input: singular noun
    output: plural form of the noun
    """
    return p.plural_noun(singular)

def inflect_singular(plural):
    """
    input: plural noun
    output: singular forms of the noun
    """
    return p.singular_noun(plural)

def nounify_adjectives(sentence):
    """
    input: sentence
    output: list of its lemmatized comparatives/superlatives
    example: taller-->talleness, oldest-->oldness
    """
    adjectives = []
    nouns = []
    text = word_tokenize(sentence)
    parse = nltk.pos_tag(text)
    for token,pos in parse:
        # insert noun inflection
        if pos in ['RB', 'JJS', 'JJR']:
            adjectives += [token]
    for adj in adjectives:
        noun_list = convert(adj, WN_ADJECTIVE, WN_NOUN)
        if len(noun_list) > 0:
            noun = noun_list[0][0]
            nouns += [noun]
    return nouns

def lemmatize_adjectives(sentence):
    """
    input: sentence
    output: list of its lemmatized comparatives/superlatives
    example: taller-->tall, oldest-->old
    """
    adjectives = []
    lemmas = []
    text = word_tokenize(sentence)
    parse = nltk.pos_tag(text)
    for token,pos in parse:
        # insert noun inflection
        if pos in ['RB', 'JJS', 'JJR']:
            adjectives += [token]
    for adj in adjectives:
        lemma = wordnet_lemmatizer.lemmatize(adj, pos="a")
        lemmas += [lemma]
    return lemmas

def lemmatize_verbs(sentence):
    """
    input: sentence
    output: list of its lemmatized verbs
    example: uses-->use, died-->die, working --> work
    """
    verbs = []
    lemmas = []
    text = word_tokenize(sentence)
    parse = nltk.pos_tag(text)
    for token,pos in parse:
        # insert noun inflection
        if pos in ['VBZ', 'VBD', 'VBG']:
            verbs += [token]
    for verb in verbs:
        lemma = wordnet_lemmatizer.lemmatize(verb, pos="v")
        lemmas += [lemma]
    return lemmas


def additional_tokens():
    """
    input: none
    output: returns closed set of additional annotation tokens
    """
    words = ['a', 'if', 'how', 'where', 'when', 'which', 'who', 'what', 'with', 'was', 'did', 'to', 'from', 'both', 'and', 'or', 'the', 'of', 'is', 'are', 'besides', 'that', 'have', 'has', 'for each', 'number of', 'not', 'than', 'those', 'on', 'in', 'any', 'there', 'distinct', ',', ', ']
    # duplicate stop word prevalence for react 'auto-select' component
    words_duplicate = list(map(lambda x: x+' ', words))
    comparison = ['same as', 'higher than', 'larger than', 'smaller than', 'lower than', 'more', 'less', 'at least', 'at most', 'equal', 'highest', 'lowest']
    order = ['sorted by']
    airthmetic = ['sum', 'difference', 'multiplication', 'division', '100', 'hundred', 'one', 'two', 'zero']
    previous_steps = ['#'+str(x) for x in range(1, 20)]
    extra_relations = ['height', 'population', 'size', 'elevation', 'flights', 'objects', 'price', 'date', 'true', 'false']
    tokens = words + words_duplicate + comparison + order + airthmetic + previous_steps + extra_relations
    return tokens

def replace_duplicate_words(word_list):
    """
    input: list of words
    output: new list where words that appear more than once in the input are replaced by 'word '
            used due to react-autoselect UI of the app
    """
    new_list = []
    for word in word_list:
        occurences = word_list.count(word)
        if occurences > 1:
            for i in range(occurences):
                suffix = " "*i
                new_list += [word+suffix]
        else:
            new_list += [word]
    return new_list

def valid_annotation_tokens(question_text):
    """
    input: NL question
    output: the list of valid tokens to use in the decomposition
    """
    valid_tokens = word_tokenize(question_text)
    valid_tokens = replace_duplicate_words(valid_tokens)
    valid_tokens += noun_inflections(question_text)
    valid_tokens += nounify_adjectives(question_text)
    valid_tokens += lemmatize_adjectives(question_text)
    valid_tokens += lemmatize_verbs(question_text)
    valid_tokens += additional_tokens()
    valid_tokens = [t for t in valid_tokens if t not in ['.','?',':',';','\"', '\'', '``', '\'\'']]
    remove_duplicates = set(valid_tokens)
    valid_tokens = list(remove_duplicates)
    return valid_tokens

def generate_question(dataset_row):
    """
    input: 
        row dataframe object of the dataset <, id, question_text, logical_form>
    output: 
        question object
    """
    question_text = dataset_row['question_text']
    question_text = question_text.replace('\\', '')
    tokens = valid_annotation_tokens(question_text)
    question_text_abridged = question_text.replace("'", "\\'")
    question = Question(dataset_row['id'], question_text_abridged, tokens)
    return question

def generate_json_tokens(valid_tokens):
    """
    input: list of valid question tokens
    output: string rep. of the json store
    """
    arr_str = "["
    for tok in valid_tokens:
        arr_str += " \"%s\", " % tok
    arr_str = arr_str[:-2]
    arr_str += "]"
    return arr_str


def generate_json_store(dataset_path, store_path, batch_size):
    """
    input: 
        path to dataset csv <, id, question_text, logical_form>
        path to store.json file to write
        batch size of questions to be written each time
    output: 
        writes dataset JSON to store file
    """
    df = pd.read_csv(dataset_path)
    # filter out dataset questions to keep the store lightweight for app
    ### Keep only the NLVR2 dataset
    ###df = df[df['id'].str.contains("NLVR2_")]
    questions_to_process = len(df.index)
    # process questions into new dataframe
    json_headers = ["id", "text", "valid_tokens"]
    df_out = pd.DataFrame(columns=json_headers)
    with open(store_path, 'a', encoding="utf8") as file:
        count = 0 # index does not represent num of questions processed due to df fiter
        for index, row in df.iterrows():
            count += 1
            q = generate_question(row)
            q_list = [[q.get_index(), q.get_text(), q.get_valid_tokens()]]
            df_row = pd.DataFrame(q_list, columns=json_headers)
            df_out = df_out.append(df_row, ignore_index=True)
            if (count % batch_size == 0) and (count > batch_size):
                logger.info(f'Processed {count} / {questions_to_process} questions.')
        # write json string
        df_out = df_out.set_index('id')
        df_out.to_json(store_path, orient='index')
    return True
  

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('dataset', help='csv file containing NL questions id and text')
    # args = parser.parse_args()
    logger.info("* Generating store.json file:")
    file_path = "store_full.json"
    generate_json_store("decomposition_dataset_full.csv", file_path, 5000)
    logger.info("Done writing to %s" % (file_path))

if __name__ == '__main__':
    main()
