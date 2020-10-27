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

### Lexicon file generation
The lexicon json files for our QDMR parsing models can be found in Break's [dataset](https://github.com/allenai/Break/tree/master/break_dataset).
To generate valid lexicon tokens for a *new* example, use the `valid_annotation_tokens` found [here](https://github.com/tomerwolgithub/Break/blob/master/annotation_pipeline/utils/app_store_generation.py). Note that you would still need to format the valid lexicon tokens according to the lexicon file format `{"source": "NL question", "allowed_tokens": [valid annotation tokens]}`, e.g.:

```
{"source": "what flights go from dallas to phoenix ", "allowed_tokens": "['higher than', 'same as', 'what ', 'and ', 'than ', 'at most', 'distinct', 'two', 'at least', 'or ', 'date', 'on ', '@@14@@', 'equal', 'hundred', 'those', 'sorted by', 'elevation', 'which ', '@@6@@', 'was ', 'dallas', 'did ', 'population', 'height', 'one', 'that ', 'on', 'did', 'who', 'true', '@@2@@', '100', 'false', 'and', 'was', 'who ', 'a ', 'the', 'number of ', '@@16@@', 'if ', 'where', '@@18@@', 'how', 'larger than', 'is ', 'from ', 'a', 'for each', 'less', 'are ', '@@19@@', '@@4@@', '@@11@@', 'distinct ', 'flight', 'to', 'not ', 'objects', 'with ', ', ', 'lowest', 'in', 'has ', 'zero', 'in ', 'there ', 'lower than', 'highest', 'go', '@@9@@', 'than', 'size', 'multiplication', 'with', 'besides ', ',', '@@1@@', 'what', 'have', 'those ', 'of', '@@3@@', 'that', 'there', '@@10@@', '@@5@@', 'both ', '@@15@@', 'number of', 'price', 'any', 'which', 'to ', 'how ', 'when ', 'of ', 'division', 'dallass', 'is', 'sum', 'or', 'if', 'more', '@@12@@', 'smaller than', 'flights', 'phoenix', '@@7@@', '@@17@@', 'for each ', 'from', '@@13@@', 'has', 'difference', 'when', 'are', 'any ', '@@8@@', 'both', 'the ', ',  ', 'besides', 'have ', 'where ', 'not']"}
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

### Cofiguration and petrained models

Training and running the neural models can be done with the [AllenNLP framework](https://allenai.github.io/allennlp-docs/) and the provided configurations.  
The pretrained neural models described in our [paper](https://arxiv.org/abs/2001.11770) are provided below, along with their hyperparameter configurations:

|model | dataset | hyperparameters | download |
|--------|:--------:|:--------:|:--------| 
| seq2seq | Break | `layers1_lr0.001_hd450_dop0.0` | [seq2seq_low](https://storage.googleapis.com/ai2i/break_models/seq2seq_layers1_lr0.001_hd450_dop0.0_final_low.zip) |
| copynet | Break | `layers2_lr0.001_hd450_dop0.2` | [copynet_low](https://storage.googleapis.com/ai2i/break_models/seq2seq-copynet_layers2_lr0.001_hd450_dop0.2_final_low.zip) |
| seq2seq-dynamic | Break | `layers1_lr0.001_hd450_dop0.2` | [dynamic_low](https://storage.googleapis.com/ai2i/break_models/seq2seq-dynamic_layers1_lr0.001_hd450_dop0.2_final_low_dynamic.zip) |
| seq2seq | Break high-level | `layers1_lr0.001_hd300_dop0.0` | [seq2seq_high](https://storage.googleapis.com/ai2i/break_models/seq2seq_layers1_lr0.001_hd300_dop0.0_final_high.zip) |
| copynet | Break high-level | `layers3_lr0.001_hd450_dop0.2` | [copynet_high](https://storage.googleapis.com/ai2i/break_models/seq2seq-copynet_layers3_lr0.001_hd450_dop0.2_final_high.zip) |
| seq2seq-dynamic | Break high-level | `layers1_lr0.001_hd300_dop0.3` | [dynamic_high](https://storage.googleapis.com/ai2i/break_models/seq2seq-dynamic_layers1_lr0.001_hd300_dop0.3_final_high_dynamic.zip) |
  

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

