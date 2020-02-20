# QDMR Parsing

This directory contains the implementation of our baseline models and evaluation metrics.

## Environment set-up
Our experiments were conducted in a **python 3.6.8** environment.
To set up the environment, please run the following commands, which download and install the required packages:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Data pre-processing
Before training or evaluating the models, the data files should be processed with the script `utils/preprocess_examples.py`.
```bash
$ python utils/preprocess_examples.py -h

usage: preprocess_examples.py [-h] [--lexicon_file LEXICON_FILE]
                              [--output_file_base OUTPUT_FILE_BASE]
                              [--sample SAMPLE]
                              input_file output_dir

example command: python utils/preprocess_examples.py data/QDMR/train.csv data/
--lexicon_file data/QDMR/train_lexicon_tokens.json --output_file_base
train_dynamic

positional arguments:
  input_file            path to input file
  output_dir            path to output file, without file extension

optional arguments:
  -h, --help            show this help message and exit
  --lexicon_file LEXICON_FILE
                        path to lexicon json file with allowed tokens per
                        example
  --output_file_base OUTPUT_FILE_BASE
                        output file base name (without file extension)
  --sample SAMPLE       json-formatted string with dataset down-sampling
                        configuration, for example: {"ATIS": 0.5, "CLEVR":
                        0.2}
```

## Model training and inference

There are 5 baseline models implemented in the paper, three seq2seq neural models and two rule-based (not-neural) models:

|model | type | implementation |
|--------|:--------:|:--------|
| copy | rule-based | `model/rule_based/copy_model.py` |
| rule-based | rule-based | `model/rule_based/rule_based_model.py` |
| seq2seq | neural | AllenNLP official model, configuration: `model/seq2seq/train-seq2seq.json` |
| copynet | neural | AllenNLP official model, configuration: `model/seq2seq/train-seq2seq-copynet.json` | 
| seq2seq-dynamic | neural | AllenNLP-based model, configuration: `model/seq2seq/train-seq2seq-dynamic.json` | 

To run our rule-based models, use the script `model/run_model.py` either on an input file or by providing a question as an argument (see examples in the evaluation section).

Training and running the neural models can be done with the [AllenNLP framework](https://allenai.github.io/allennlp-docs/) and the provided configurations (details on the hyperparameters used in our work can be found in the paper).
  

## Evaluation
Evaluation of any model with the metrics described in the paper (i.e. EM, SARI, GED, GED+) can be done with the script `model/run_model.py`, by specifying the model for evaluation and passing the flag `--evaluate`. For further usage options please check the help menu of the script, sample commands are provided below.

Code for computing the SARI score was taken from the [tensor2tensor](https://github.com/tensorflow/tensor2tensor/blob/master/tensor2tensor/utils/sari_hook.py) library by Google.

#### Note on evaluation speed
GED and GED+ are algorithms which approximate distance between graphs. Their execution, and particularly the execution of GED+, can take long time and for large graphs might not even be feasible. To handle this, we apply 3 mechanisms:
1) In case the execution of either GED or GED+ takes longer than 10 minutes, it is interrupted and the example will be skipped (it's also possible to interrupt evaluation on specific example with `Ctrl+C`).
2) Decomposition graphs with more than 5 nodes are skipped during GED+ computation.
3) Computation of GED+ can be done using multiple processes (see example in the section below). 


#### Example commands

1. Evaluating the a trained seq2seq-dynamic model on 10 random examples from the development set. 
    ```bash
   python model/run_model.py \
   --input_file data/dev_dynamic.tsv \
   --random_n 10 \
   --model dynamic \
   --model_dir trained_models/seq2seq_dynamic/ \
   --evaluate
   ```

2. Evaluating the copy baseline on the development set, with 10 processes for computing GED+. 
   ```bash
   python model/run_model.py \
   --input_file data/dev.tsv \
   --model copy \
   --evaluate \
   --num_processes 10
   ```

3. Evaluating the rule-based baseline on a question provided as an argument.
   ```bash
   python model/run_model.py \
   --model rule_based \
   --evaluate \
   --question "Return the keywords which have been contained by more than 100 ACL papers" \
   --gold "papers @@SEP@@ @@1@@ in ACL @@SEP@@ keywords of @@2@@ @@SEP@@ number of @@2@@ for each @@3@@ @@SEP@@ @@3@@ where @@4@@ is more than 100"
   ```

