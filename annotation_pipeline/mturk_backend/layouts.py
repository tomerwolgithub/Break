"""Functions for creating MTurk HIT layouts"""

import jinja2
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import random


def create_gen_hit_layout(annotation_id, question_id, template_dir_path, template_name):
    """Creates an XML layout of an MTurk generation HIT for a specific dataset question
    
    Parameters
    ----------
    annotation_id : str
        The annotation id from the annotation log file
    question_id : str
        Question id to be annotated
    template_dir_path : str
        Path to the dir containing XML layout templates
    template_name : str
        Specific template XML to be used for the HIT layout
    
    Returns
    -------
    str
        Returns xml string representing the generation HIT layout
    """
    # pass the directory containing the templates to the FileSystemLoader
    file_loader = FileSystemLoader(template_dir_path)
    # load the environment
    env = Environment(loader=file_loader)
    template = env.get_template(template_name)
    hit_layout = template.render(annotation_id=annotation_id, question_id=question_id)
    return hit_layout

def create_val_hit_layout(annotation_id, question_id, question_text, decomposition,\
                          bank_id, bank_question_text, bank_decomposition, template_dir_path, template_name):
    """Creates an XML layout of an MTurk validation HIT for a given decomposition
        and for a bank decomposition that is used to assess validator quality
    
    Parameters
    ----------
    annotation_id : str
        The annotation id from the annotation log file
    question_id : str
        Question id of the decomposed question
    question_text : str
        Text of the original decomposed question
    decomoposition : str
        The decomposition annotated by a worker
    bank_id : str
        Id from the gold annotations bank of a decomposition whose accuracy is known
    bank_question_text : str
        Text of the bank decomposition original question
    bank_decomoposition : str
        The bank decomposition
    template_dir_path : str
        Path to the dir containing XML layout templates
    template_name : str
        Specific template XML to be used for HIT layout
    
    Returns
    -------
    str
        Returns xml string representing the validation HIT layout
    """
    # flag indicating whether bank decomposition is displayed before the actual decomposition
    bank_comes_first = (random.randint(0,1) == 0)
    # pass the directory containing the templates to the FileSystemLoader
    file_loader = FileSystemLoader(template_dir_path)
    # load the environment
    env = Environment(loader=file_loader)
    template = env.get_template(template_name)
    dec_formatted = html_formatted_decomposition(decomposition)
    bank_dec_formatted = html_formatted_decomposition(bank_decomposition)
    hit_layout = template.render(annotation_id=annotation_id, question_id=question_id,\
                                 question_text=question_text, decomoposition=dec_formatted,\
                                 bank_id=bank_id, bank_question_text=bank_question_text,\
                                 bank_decomoposition=bank_dec_formatted)
    return hit_layout


def html_formatted_decomposition(decomposition_string, delimiter=";"):
    """Returns a formatted html string representation of a query decomposition
        to be displayed on an html HIT layout.
    
    Parameters
    ----------
    decomposition_string : str
        decompositiong string with delimited steps 
    delimiter : str
        delimiter at the end of decomposition steps
    
    Returns
    -------
    str
        Returns formatted html string, numbered steps, each step in a new line
    """
    html_decomposition = ""
    # remove last delimiter
    if decomposition_string[-1] == delimiter:
        decomposition_string = decomposition_string[:-1]
    # break into steps
    steps = decomposition_string.split(delimiter)
    for i in range(len(steps)):
        html_decomposition += '<br>' + str(i+1) + '. ' + steps[i]
    return html_decomposition