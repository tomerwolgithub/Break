"""HIT results data structure"""

import json

class HITResults:
    
    def __init__(self, hit_id, assignment_id, worker_id, submit_time):
        self.hit_id = hit_id
        self.assignment_id = assignment_id
        self.worker_id = worker_id
        # submit_time is a datetime object which we convert to a string
        self.submit_time = submit_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.accepted = None
        self.type = None
    
    def accept(self):
        self.accepted = True
        
    def reject(self):
        self.accepted = False
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

        
class GenerationResults(HITResults):
    
    def __init__(self, hit_id, assignment_id, worker_id, submit_time, decomposition):
        super().__init__(hit_id, assignment_id, worker_id, submit_time)
        self.decomposition = decomposition  
        self.type = 'gen'
        self.manually_validated = None
        self.valid_annotation = None
    
    def validate(self, manual_validation_result):
        self.manually_validated = True
        self.valid_annotation = manual_validation_result
        
        
class ValidationResults(HITResults):
    
    def __init__(self, hit_id, assignment_id, worker_id, submit_time, annotation_validation, bank_validation):
        super().__init__(hit_id, assignment_id, worker_id, submit_time)
        self.annotation_validation = annotation_validation 
        self.bank_validation = bank_validation 
        self.type = 'val'