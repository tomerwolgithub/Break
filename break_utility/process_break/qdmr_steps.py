"""
# @Time    : 2020/2/23
# @Author  : Wolfson
"""

### Code for QDMR step identifier:

import re

class QDMROperation:
    FIND, SELECT, FILTER, PROJECT, AGGREGATE, GROUP, SUPERLATIVE, COMPARATIVE, UNION, \
    INTERSECTION, DISCARD, SORT, BOOLEAN, ARITHMETIC, COMPARISON, NONE = range(16)
    
def op_name(qdmr_op):
    return {
        QDMROperation.FIND : 'FIND',
        QDMROperation.SELECT : 'SELECT',
        QDMROperation.FILTER : 'FILTER',
        QDMROperation.PROJECT : 'PROJECT',
        QDMROperation.AGGREGATE : 'AGGREGATE',
        QDMROperation.GROUP : 'GROUP',
        QDMROperation.SUPERLATIVE : 'SUPERLATIVE',
        QDMROperation.COMPARATIVE : 'COMPARATIVE',
        QDMROperation.UNION : 'UNION',
        QDMROperation.INTERSECTION : 'INTERSECTION',
        QDMROperation.DISCARD : 'DISCARD',
        QDMROperation.SORT : 'SORT',
        QDMROperation.BOOLEAN : 'BOOLEAN',
        QDMROperation.ARITHMETIC : 'ARITHMETIC',
        QDMROperation.COMPARISON : 'COMPARISON',
        QDMROperation.NONE : 'NONE'
    }.get(qdmr_op, QDMROperation.NONE)

   
def step_type(step, is_high_level):
    """
    Maps a single QDMR step into relevant its operator type
    
    Parameters
    ----------
    step : str
        String representation a single QDMR step
    is_high_level : bool
        Flag whether or not we include the high level FIND steps,
        associated with RC datasets
    
    Returns
    -------
    QDMROperation
        returns the type of QDMR operation of the step
    """
    step = step.lower()
    references = extract_references(step)
    if step.lower().startswith('if ') or step.lower().startswith('is ') or \
    step.lower().startswith('are '): 
        # BOOLEAN step - starts with either 'if', 'is' or 'are'
        return QDMROperation.BOOLEAN
    if len(references) == 0:
        # SELECT step - no references to previous steps
        return QDMROperation.SELECT
    # Discrete QDMR step types:
    if len(references) == 1:
        # AGGREGATION step - aggregation applied to one reference
        aggregators = ['number of', 'highest', 'largest', 'lowest', 'smallest', 'maximum', 'minimum', \
                       'max', 'min', 'sum', 'total', 'average', 'avg', 'mean ']
        for aggr in aggregators:
            aggr_ref = aggr + ' #'
            aggr_of_ref = aggr + ' of #'
            if (aggr_ref in step) or (aggr_of_ref in step):
                return QDMROperation.AGGREGATE
    if 'for each' in step:
        # GROUP step - contains term 'for each'
        return QDMROperation.GROUP
    if len(references) >= 2 and len(references) <= 3 and ('where' in step):
        # COMPARATIVE step - '#1 where #2 is at most three'
        comparatives = ['same as', 'higher than', 'larger than', 'smaller than', 'lower than',\
                        'more', 'less', 'at least', 'at most', 'equal', 'is', 'are', 'was', 'contain', \
                        'include', 'has', 'have', 'end with', 'start with', 'ends with', \
                        'starts with', 'begin']
        for comp in comparatives:
            if comp in step:
                return QDMROperation.COMPARATIVE
    if step.startswith('#') and ('where' in step) and len(references) == 2:
        # SUPERLATIVE step - '#1 where #2 is highest/lowest'
        superlatives = ['highest', 'largest', 'most', 'smallest', 'lowest', 'smallest', 'least', \
                       'longest', 'shortest', 'biggest']
        for s in superlatives:
            if s in step:
                return QDMROperation.SUPERLATIVE
    if len(references) > 1:
        # UNION step - '#1, #2, #3, #4' / '#1 or #2' / '#1 and #2'
        is_union = re.search("^[#\s]+[and0-9#or,\s]+$", step)
        if is_union:
            return QDMROperation.UNION
    if len(references) > 1 and ('both' in step) and ('and' in step):
        # INTERSECTION step - 'both #1 and #2'
        return QDMROperation.INTERSECTION
    if (len(references) >= 1) and (len(references) <= 2) and \
    (re.search("^[#]+[0-9]+[\s]+", step) or re.search("[#]+[0-9]+$", step)) and \
     ('besides' in step or 'not in' in step):
        # DISCARD step - '#2 besides X'
        return QDMROperation.DISCARD
    if ('sorted by' in step) or ('order by' in step) or ('ordered by' in step):
        # SORT step - '#1 ordered/sorted by #2'
        return QDMROperation.SORT
    if step.lower().startswith('which') and len(references) > 1:
        # COMPARISON step - 'which is better A or B or C'
        return QDMROperation.COMPARISON
    if len(references) >= 1 and ('and' in step or ',' in step):
        # ARITHMETIC step - starts with arithmetic operation
        arithmetics = ['sum', 'difference', 'multiplication', 'division']
        for a in arithmetics:
            if step.startswith(a) or step.startswith('the ' + a):
                return QDMROperation.ARITHMETIC
    # Non-discrete QDMR step types:
    if len(references) == 1 and re.search("[\s]+[#]+[0-9\s]+", step):
        # PROJECT step - 'property of #2'
        return QDMROperation.PROJECT
    if len(references) == 1 and step.startswith("#"):
        # FILTER step - '#2 [condition]'
        return QDMROperation.FILTER
    if len(references) > 1 and step.startswith("#"):
        # FILTER step - '#2 [relation] #3'
        return QDMROperation.FILTER
    if is_high_level:
        return QDMROperation.FIND
    return QDMROperation.NONE
    

def extract_references(step):
    """Extracts list of references to previous steps
    
    Parameters
    ----------
    step : str
        String representation of a QDMR step
    
    Returns
    -------
    list
        returns list of ints of referenced steps
    """
    # make sure decomposition does not contain a mere '# ' rather than reference.
    step = step.replace("# ", "hashtag ")
    # replace ',' with ' or'
    step = step.replace(", ", " or ")
    references = []
    l = step.split(REF)
    for chunk in l[1:]:
        if len(chunk) > 1:
            ref = chunk.split()[0]
            ref = int(ref)
            references += [ref]
        if len(chunk) == 1:
            ref = int(chunk)
            references += [ref]
    return references


DELIMITER = ';'
REF = '#'

def parse_decomposition(qdmr):
    """Parses the decomposition into an ordered list of steps
    
    Parameters
    ----------
    qdmr : str
        String representation of the QDMR
    
    Returns
    -------
    list
        returns ordered list of qdmr steps
    """
    crude_steps = qdmr.split(DELIMITER)
    steps = []
    for i in range(len(crude_steps)):
        step = crude_steps[i]
        tokens = step.split()
        step = ""
        # remove 'return' prefix
        for tok in tokens[1:]:
            step += tok.strip() + " "
        step = step.strip()
        steps += [step]
    return steps


def get_op_type(step):
    op = step_type(step, True)
    if op == QDMROperation.FIND or \
    op == QDMROperation.PROJECT:
        return "BRIDGE"
    if op == QDMROperation.BOOLEAN:
        refs = extract_references(step)
        if len(refs) == 2:
            if (' both ' in step) and (' and ' in step):
                return '%s_AND' % op_name(op)
            if (' either ' in step) and (' or ' in step):
                return '%s_OR' % op_name(op)
            if (' same as ' in step):
                return '%s_EQ' % op_name(op)
            if (' different ' in step):
                return '%s_NEQ' % op_name(op)     
        return op_name(op)
    else:
        return op_name(op)
    return False


def get_qdmr_ops(steps):
    op_list = []
    for step in steps:
        op_type = get_op_type(step)
        op_list += [op_type]
    return op_list


     
def is_operator_set(steps, op_set):
    """Returns whether the qdmr operators are identical to op set
    
    Parameters
    ----------
    steps : list
        List of QDMR steps.
    op_set: set
        Set of specific QDMR operators.
    
    Returns
    -------
    bool
        Returns True if the steps operators are 
        identical to those in op_set, otherwise False.
    """
    qdmr_ops = get_qdmr_ops(steps)
    return qdmr_ops == op_set


def contains_operator_set(steps, op_set):
    """Returns whether the op sets is contained in the decomposition
    
    Parameters
    ----------
    steps : list
        List of QDMR steps.
    op_set: set
        Set of specific QDMR operators.
    
    Returns
    -------
    bool
        Returns True if the operators in op_set all appear
        in the decomposition, otherwise False.
    """
    qdmr_ops = get_qdmr_ops(steps)
    return (op_set.issubset(qdmr_ops))