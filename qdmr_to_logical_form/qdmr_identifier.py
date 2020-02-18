from operator_identifier import *
from utils import *


class QDMRStep:
    def __init__(self, step_text, operator, arguments):
        self.step = step_text
        self.operator = operator
        self.arguments = arguments
        
    def __str__(self):
        return "%s%a" % (self.operator.upper(), self.arguments)
    
    
    
    
class StepIdentifier(object):
    def __init__(self):
        self.identifiers = {"select": IdentifyOperatorSelect(),
                            "filter": IdentifyOperatorFilter(),
                            "project": IdentifyOperatorProject(),
                            "aggregate": IdentifyOperatorAggregate(),
                            "group": IdentifyOperatorGroup(),
                            "superlative": IdentifyOperatorSuperlative(),
                            "comparative": IdentifyOperatorComparative(),
                            "union": IdentifyOperatorUnion(),
                            "intersection": IdentifyOperatorIntersect(),
                            "discard": IdentifyOperatorDiscard(),
                            "sort": IdentifyOperatorSort(),
                            "boolean": IdentifyOperatorBoolean(),
                            "arithmetic": IdentifyOperatorArithmetic(),
                            "comparison": IdentifyOperatorComparison()}
        self.operator = None
    
    def step_type(self, step_text):
        potential_operators = set()
        for op in self.identifiers:
            identifier = self.identifiers[op]
            if identifier.identify_op(step_text):
                potential_operators.add(op)
        # no matching operator found
        if len(potential_operators) == 0:
            return None
        operators = potential_operators.copy() 
        # duplicate candidates 
        if len(operators) > 1:
            # avoid project duplicity with aggregate
            if "project" in operators:
                operators.remove("project")
            # avoid filter duplcitiy with comparative, superlative, sort, discard
            if "filter" in operators:
                operators.remove("filter")
            # return boolean (instead of intersect)
            if "boolean" in operators:
                operators = {"boolean"}
            # return intersect (instead of filter)
            if "intersect" in operators:
                operators = {"intersect"}
            # return superlative (instead of comparative)
            if "superlative" in operators:
                operators = {"superlative"}
            # return group (instead of arithmetic)
            if "group" in operators:
                operators = {"group"}
            # return comparative (instead of discard)
            if "comparative" in operators:
                operators = {"comparative"}
            # return intersection (instead of comparison)
            if "intersection" in operators:
                operators = {"intersection"}
        assert(len(operators) == 1)
        operator = list(operators)[0]
        self.operator = operator
        return operator
    
    def step_args(self, step_text):
        self.operator = self.step_type(step_text)
        identifier = self.identifiers[self.operator]
        args = identifier.extract_args(step_text)
        return args
    
    def identify(self, step_text):
        self.operator = self.step_type(step_text)
        args = self.step_args(step_text)
        return QDMRStep(step_text, self.operator, args)
    

    
class QDMRProgramBuilder(object):
    def __init__(self, qdmr_text):
        self.qdmr_text = qdmr_text
        self.steps = None
        self.operators = None
        self.program = None
        
    def build(self):
        try:
            self.get_operators()
            self.build_steps()
        except:
            print("Unable to identify all steps: %s" % self.qdmr_text)
        return True
        
    def build_steps(self):
        self.steps = []
        steps = parse_decomposition(self.qdmr_text)
        step_identifier = StepIdentifier()
        for step_text in steps:
            try:
                step = step_identifier.identify(step_text)
            except:
                print("Unable to identify step: %s" % step_text)
                step = None
            self.steps += [step]
        return self.steps
    
    def get_operators(self):
        self.operators = []
        steps = parse_decomposition(self.qdmr_text)
        step_identifier = StepIdentifier()
        for step_text in steps:
            try:
                op = step_identifier.step_type(step_text)
            except:
                print("Unable to identify operator: %s" % step_text)
                op = None
            self.operators += [op]
        return self.operators
    
    def build_program(self):
        raise NotImplementedError
        return True
        