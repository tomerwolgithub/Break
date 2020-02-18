import json
import pandas as pd
import csv
import os
import collections
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Question:

    def __init__(self, original_dataset, dataset_id, question_text, logical_form):
        self.original_dataset = original_dataset
        self.dataset_id = dataset_id
        self.question_text = question_text
        self.logical_form = logical_form
        
    def question_id(self):
        """
        returns a unique question id in format:
            [dataset]_[id]
        """
        q_id = self.original_dataset + "_" + str(self.dataset_id)
        return q_id
    
    def has_logical_form(self):
        return (self.logical_form != None)
        

class DatasetReader:

    def __init__(self, dataset_name, split, file_path):
        self.dataset_name = dataset_name
        self.split = split # train/dev/test
        self.file_path = file_path
        self.dataset = [] # list of Question objects
        self.dataset_dict = {'id':[], 'question_text':[], 'logical_form': []}

    def get_full_name(self):
        return self.dataset_name + '_' + self.split
    
    def read(self):
        raise Exception('Error - called abstract read function of DatasetReader') 
        
    def get_dataset(self):
        return self.dataset
    
    def get_dataset_dict(self):
        return self.dataset_dict
    
    def add_question(self, question):
        self.dataset += [question]
        self.update_dict(question)
    
    def update_dict(self, question):
        self.dataset_dict['id'] += [question.question_id()]
        self.dataset_dict['question_text'] += [question.question_text]
        self.dataset_dict['logical_form'] += [question.logical_form]
        

class SpiderReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("SPIDER", split, file_path)
    
    # SPIDER dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
        for i in range(len(data)):
            question_text = data[i]["question"]
            logical_form = data[i]["query"]
            q = Question(self.get_full_name(), i, question_text, logical_form)
            self.add_question(q)
        return True

    
class ATISReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("ATIS", split, file_path)
        
    # ATIS dataset is in txt format with delimiter |||
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        delimiter = "|||"
        with open(self.file_path) as f:
            data = f.readlines()
        for i in range(len(data)):
            line = data[i]
            question_text, logical_form = line.split("|||")
            q = Question(self.get_full_name(), i, question_text, logical_form)
            self.add_question(q)
        return True

    
class AcademicReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("ACADEMIC", split, file_path)
        
    # Academic dataset is in txt format with delimiter |||
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        delimiter = "|||"
        with open(self.file_path) as f:
            data = f.readlines()
        for i in range(len(data)):
            line = data[i]
            question_text, logical_form = line.split("|||")
            q = Question(self.get_full_name(), i, question_text, logical_form)
            self.add_question(q)
        return True

    
class GeoReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("GEO", split, file_path)
        
    # Geo dataset is in txt format with delimiter |||
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        delimiter = "|||"
        with open(self.file_path) as f:
            data = f.readlines()
        for i in range(len(data)):
            line = data[i]
            question_text, logical_form = line.split("|||")
            q = Question(self.get_full_name(), i, question_text, logical_form)
            self.add_question(q)
        return True

    
class ClevrReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("CLEVR", split, file_path)
        
    # CLEVR-humans dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
            questions = data["questions"]
        for i in range(len(questions)):
            question_text = questions[i]["question"]
            logical_form = None
            q = Question(self.get_full_name(), i, question_text, logical_form)
            self.add_question(q)
        return True

    
class GQAReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("GQA", split, file_path)
        
    # GQA dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
        for i in data:
            question_id = i
            question_text = data[i]["question"]
            logical_form = None
            q = Question(self.get_full_name(), question_id, question_text, logical_form)
            self.add_question(q)
        return True  
    
    
class CWQReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("CWQ", split, file_path)
        
    # ComplexWebQuestions dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
        for i in range(len(data)):
            question_id = data[i]["ID"]
            question_text = data[i]["question"]
            logical_form = repr(data[i]["sparql"])
            q = Question(self.get_full_name(), question_id, question_text, logical_form)
            self.add_question(q)
        return True  
    
    
class HotpotReader(DatasetReader):

    def __init__(self, split, file_path, level=None):
        super().__init__("HOTPOT", split, file_path)
        self.level = level
        
    # Hotpot dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
        for i in range(len(data)):
            # skip questions of other difficulty
            if self.level != None:
                question_level = data[i]["level"]
                if self.level != question_level:
                    continue
            question_id = data[i]["_id"]
            question_text = data[i]["question"]
            logical_form = data[i]["type"]
            q = Question(self.get_full_name(), question_id, question_text, logical_form)
            self.add_question(q)
        return True  


class DropReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("DROP", split, file_path)
        
    # DROP dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
        for passage in data:
            questions = data[passage]["qa_pairs"]
            for ex in questions:
                question_id = passage + "_" + ex["query_id"]
                question_text = ex["question"]
                logical_form = None
                q = Question(self.get_full_name(), question_id, question_text, logical_form)
                self.add_question(q)
        return True  
    

class ComQAReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("COMQA", split, file_path)
        
    # ComQA dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path) as f:
            data = json.load(f)
        for cluster in data:
            # return only clusters with answers
            answers = cluster["answers"]
            if answers != [""]:
                # test split strcuture is different
                if self.split == 'test':
                    question_id = "id-" + str(cluster["id"])
                    question_text = cluster["question"]
                    logical_form = None
                    q = Question(self.get_full_name(), question_id, question_text, logical_form)
                    self.add_question(q)
                else:
                    question_paraphrases = cluster["questions"]
                    cluster_id = cluster["cluster_id"]
                    count = 1
                    for q in question_paraphrases:
                        # add each question paraphrase
                        question_id = cluster_id + "-" + str(count)
                        question_text = q
                        count += 1
                        logical_form = None
                        q = Question(self.get_full_name(), question_id, question_text, logical_form)
                        self.add_question(q)
        return True  

    
class TempQReader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("TEMPQ", split, file_path)
        
    # TempQuestions dataset is in json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path, encoding="utf8") as f:
            data = json.load(f)
        for example in data:
            question_id = "id-" + str(example["Id"])
            question_text = example["Question"]       
            logical_form = None
            q = Question(self.get_full_name(), question_id, question_text, logical_form)
            self.add_question(q)
        return True
    

class NLVR2Reader(DatasetReader):

    def __init__(self, split, file_path):
        super().__init__("NLVR2", split, file_path)
        
    # NLVR2 dataset is in single line json format
    def read(self):
        """Returns a list of Question objects representing the dataset"""
        with open(self.file_path, encoding="utf8") as f:
            for line in f:
                example = json.loads(line)
                question_id = example['identifier']
                sentence = example['sentence']
                # set sentence prefix to a yes/no question
                question_text = "If " + sentence.lower()
                logical_form = None
                q = Question(self.get_full_name(), question_id, question_text, logical_form)
                self.add_question(q)
        return True


    
def dataset_filters(dataset_df):
    """Filters the dataset question so that only complex question remain
    
    Parameters
    ----------
    dataset_df : dataframe
        A dataframe containing the joint datasets info


    Returns
    -------
    dataframe
        A filtered dataframe based on criteria
    """
    # E.g, remove questions with duplicate text (DROP nfl contains quite a few...)
    df = dataset_df
    # sorting by question_text
    df.sort_values("question_text", inplace = True) 
    # dropping ALL duplicate values 
    #df.drop_duplicates(subset="question_text", keep ='first', inplace=True)
    # dropping duplicate ids since DROP contains one (prob. their mistake)
    df.drop_duplicates(subset="id", keep='first', inplace=True)
    return df


def write_datasets(datasets, file_path):
        """Writes datasets into csv file

        Parameters
        ----------
        file_path : str
            The path of the csv to contain the dataset.
            If file_path does not exist, it is created by the function.
            csv contains three columns: id, question_text, logical_form
        datasets : list
            list of dataset readers to be written to csv
        """
        # append datasets into one large dictionary
        full_datasets_dict = {'id':[], 'question_text':[], 'logical_form': []}
        for reader in datasets:
            d = reader.get_dataset_dict()
            for key, value_list in d.items():
                full_datasets_dict[key] += value_list
        # write dataframe to csv
        df = pd.DataFrame(full_datasets_dict)
        logger.info("Size before filter: "+str(df.shape))##########
        # apply necessary filters on dataframe
        df = dataset_filters(df)
        logger.info("Size after filter: "+str(df.shape))##########
        with open(file_path, 'w+') as csv_file:
            df.to_csv(file_path, header=True)
        return True

def tree():
    return collections.defaultdict(tree)

def build_decomposition_questions(new_dataset_path):
    dataset_paths = tree()
    dataset_paths['academic']['train'] = "qa_datasets/academic/academic.txt"
    dataset_paths['atis']['train'] = "qa_datasets/atis/atis.uw.train.txt"
    dataset_paths['atis']['dev'] = "qa_datasets/atis/atis.uw.dev.txt"
    dataset_paths['atis']['test'] = "qa_datasets/atis/atis.uw.test.txt"
    dataset_paths['clevr']['train'] = "qa_datasets/clevr-humans/CLEVR-Humans-train.json"
    dataset_paths['clevr']['dev'] = "qa_datasets/clevr-humans/CLEVR-Humans-val.json"
    dataset_paths['clevr']['test'] = "qa_datasets/clevr-humans/CLEVR-Humans-test.json"
    dataset_paths['cwq']['train'] = "qa_datasets/cwq/ComplexWebQuestions_train.json"
    dataset_paths['cwq']['dev'] = "qa_datasets/cwq/ComplexWebQuestions_dev.json"
    dataset_paths['cwq']['test'] = "qa_datasets/cwq/ComplexWebQuestions_test.json"
    dataset_paths['drop']['train'] = "qa_datasets/drop/drop_dataset_train.json"
    dataset_paths['drop']['dev'] = "qa_datasets/drop/drop_dataset_dev.json"
    dataset_paths['geo']['train'] = "qa_datasets/geo/geography.uw.train.txt"
    dataset_paths['geo']['dev'] = "qa_datasets/geo/geography.uw.dev.txt"
    dataset_paths['geo']['test'] = "qa_datasets/geo/geography.uw.test.txt" 
    # Freeze GQA inclusion
    ### dataset_paths['gqa']['train'] = "qa_datasets/gqa/train_balanced_questions.json"
    ### dataset_paths['gqa']['dev'] = "qa_datasets/gqa/val_balanced_questions.json"
    ### dataset_paths['gqa']['test'] = "qa_datasets/gqa/test_balanced_questions.json"
    dataset_paths['hotpot']['train'] = "qa_datasets/hotpot/hotpot_train_v1.1.json"
    dataset_paths['hotpot']['dev'] = "qa_datasets/hotpot/hotpot_dev_distractor_v1.json"
    dataset_paths['spider']['train'] = "qa_datasets/spider/train_spider.json"
    dataset_paths['spider']['dev'] = "qa_datasets/spider/dev_spider.json"
    dataset_paths['comqa']['train'] = "qa_datasets/comqa/comqa_train.json"
    dataset_paths['comqa']['dev'] = "qa_datasets/comqa/comqa_dev.json"
    dataset_paths['comqa']['test'] = "qa_datasets/comqa/comqa_test.json" 
    dataset_paths['tempq']['train'] = "qa_datasets/tempquestions/TempQuestions.json"
    dataset_paths['nlvr2']['train'] = "qa_datasets/nlvr2/train.json"
    dataset_paths['nlvr2']['dev'] = "qa_datasets/nlvr2/dev.json"
    dataset_paths['nlvr2']['test'] = "qa_datasets/nlvr2/test1.json" 
    
    # build readers
    dataset_readers = []
    for name, splits_dict in dataset_paths.items():
        for split, path in splits_dict.items():
            if name == 'academic':
                dataset_readers += [AcademicReader(split, path)]
            elif name == 'atis':
                dataset_readers += [ATISReader(split, path)]
            elif name == 'clevr':
                dataset_readers += [ClevrReader(split, path)]
            elif name == 'cwq':
                dataset_readers += [CWQReader(split, path)]
            elif name == 'drop':
                dataset_readers += [DropReader(split, path)]
            elif name == 'geo':
                dataset_readers += [GeoReader(split, path)]
            ### elif name == 'gqa':
            ###     dataset_readers += [GQAReader(split, path)]
            elif name == 'hotpot':
                dataset_readers += [HotpotReader(split, path, level="hard")]
            elif name == 'spider':
                dataset_readers += [SpiderReader(split, path)]
            elif name == 'comqa':
                dataset_readers += [ComQAReader(split, path)]
            elif name == 'tempq':
                dataset_readers += [TempQReader(split, path)]
            elif name == 'nlvr2':
                dataset_readers += [NLVR2Reader(split, path)]
            else:
                raise ValueError('build_decomposition_questions - Unkown dataset name given! %s' % name)
    count = 0   
    for reader in dataset_readers:
        count += 1
        reader.read()
        logger.info("--- Read {} / {} datasets : {}".format(count, len(dataset_readers), reader.get_full_name()))
    write_datasets(dataset_readers, new_dataset_path)
    logger.info("--- Done")
    return True



build_decomposition_questions("full_dataset_TEST.csv")    


#x = DatasetReader("ATIS", "train", "atis.json")
#y = SpiderReader("dev","dev_spider.json")
#z = DropReader("dev","drop_dataset_dev.json")
#y.read()
#z.read()
#write_datasets([y,z], "test_dataset.csv")
#df = pd.read_csv("test_dataset.csv")
