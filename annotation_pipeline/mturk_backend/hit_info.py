"""HIT information data structures"""

import json

class GenerationHITInfo:
    
    def __init__(self, annotation_id, question_id, question_text):
        self.annotation_id = int(annotation_id)
        self.question_id = question_id
        self.question_text = question_text
        self.type = 'gen'
        self.hit_id = None
        
    def set_hit_id(self, hit_id):
        self.hit_id = hit_id
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

        
class ValidationHITInfo:
    
    def __init__(self, annotation_id, question_id, question_text, decomposition, generator_id, \
                 generation_hit_id, bank_annotation_info):
        self.annotation_id = annotation_id
        self.question_id = question_id
        self.question_text = question_text
        self.decomposition = decomposition
        self.generator_id = generator_id
        self.generation_hit_id = generation_hit_id
        self.bank_annotation = bank_annotation_info
        self.type = 'val'
        self.hit_id = None
        
    def set_hit_id(self, hit_id):
        self.hit_id = hit_id
    
    def to_json(self):
        d = dict()
        for a, v in self.__dict__.items():
            if (hasattr(v, "to_json")):
                d[a] = v.to_json()
            else:
                d[a] = v
        return d

        
class BankAnnotationInfo:
    
    def __init__(self, bank_id, annotation_id, question_id, question_text, decomposition, decomposition_correct):
        self.bank_id = int(bank_id)
        self.annotation_id = int(annotation_id)
        self.question_id = question_id
        self.question_text = question_text
        self.decomposition = decomposition
        self.decomposition_correct = int(decomposition_correct)
        self.type = 'bank'
        
    def to_json(self):
        return self.__dict__
