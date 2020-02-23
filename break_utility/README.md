# Utility of Break for open-domain QA
We describe the utility of Break decompositions for the HotpotQA "fullwiki" setting.

### Overview

Our experiments broadly use the following components besides Break -
1) HoptotQA: (`train`, `dev-distractor`, `dev-fullwiki`) data from [HotpotQA website](https://hotpotqa.github.io).</br>
2) Wikipedia (only first paras): from [HotpotQA wiki](https://hotpotqa.github.io/wiki-readme.html).</br>
3) IR: tf-idf ranker built on the above Wikipedia using [DrQA](https://github.com/facebookresearch/DrQA) (see `ranker/README.md`).</br>
4) Bert RC: BERT `base-uncased` span-extraction model finetuned on hotpot using an older version of [HuggingFace](https://github.com/huggingface/transformers)'s repo (see `bert_rc/README.md`).</br>
5) Single-hop RC: an ensemble trained on augmented SQuAD by [Min et al.](https://github.com/shmsw25/DecompRC/tree/master/DecompRC).</br>
6) Break RC: As described in our [paper](https://arxiv.org/abs/2001.11770v1).

### Usage
1) After navigating to the current directory, download [data.tar.gz](https://drive.google.com/file/d/1zOszBDjflJtUn8usXRz30m8KtNmk4S9P/view?usp=sharing). Then extract using `tar xvfz data.tar.gz` to have a `data` directory.</br>
2) Navigate to `ranker` directory and prepare the tf-idf ranker by following the instructions in `ranker/README.md`. E.g. one can do so as follows :
```
$ cd ranker
$ python build_tfidf.py --wiki ../data/wiki_firstpara_sents.jsonl
$ cd ..
```
You should end up with `data/wiki_first_paras-tfidf-ngram=2-hash=16777216-tokenizer=spacy.npz`.</br>

3) *Optional*: one can finetune BERT on Hotpot by following the instructions in `bert_rc/README.md`. We provide an already finetuned model in `data/bert_hotpot_67.3f1`.</br>
4) Preprocess the Break data provided in `data/qdmr_data` as follows:
```
$ cd process_break
$ python prepro_break.py --input_file ../data/qdmr_data/hotpotqa_dev_gold.csv --output_file processed_data_hotpotqa_gold.csv --is_gold

# qdmrs predicted using copy-net for the hotpot part of Break dev & test
$ python prepro_break.py --input_file ../data/qdmr_data/preds_copynet_hpqa_dev_test.tsv --ques_file ../data/qdmr_data/hotpotqa_dev_questions.csv --output_file processed_data_hotpotqa_copy_net.csv

# qdmrs predicted using rule-based model for the hotpot part of Break dev & test
$ python prepro_break.py --input_file ../data/qdmr_data/preds_rule_based_high_level_dev.tsv --ques_file ../data/qdmr_data/hotpotqa_dev_questions.csv --output_file processed_data_hotpotqa_rule_based.csv
$ cd ..
```
This will save `processed_data_hotpotqa_gold.csv`, `processed_data_hotpotqa_copy_net.csv`, `processed_data_hotpotqa_rule_based.csv` in `data/qdmr_data`. Further process these outputted files as:
```
# gold
$ python prepare_break.py --processed_break_csv data/qdmr_data/processed_data_hotpotqa_gold.csv --out_jsonl qdmrs_hotpotqa_gold.jsonl

# copy-net
$ python prepare_break.py --processed_break_csv data/qdmr_data/processed_data_hotpotqa_copy_net.csv --out_jsonl qdmrs_hotpotqa_copy_net.jsonl

# rule-based
$ python prepare_break.py --processed_break_csv data/qdmr_data/processed_data_hotpotqa_rule_based.csv --out_jsonl qdmrs_hotpotqa_rule_based.jsonl
```

5) Predict using Break RC and create Hotpot-style data for Bert RC : 
```
$ CUDA_VISIBLE_DEVICES=0 python run_break.py --qdmr_jsonl ./data/qdmr_data/qdmrs_hotpotqa_gold.jsonl --suffix gold --predict_batch_size 256
```
After taking some time, this would save:  
a) BreakRC results in `./data/predictions/break_rc_results_gold.json` (as `--suffix` was `gold`).</br>
b) Hotpot-style data for Bert RC using baseline IR using the whole question: in `./data/hotpot_data/hotpot_after_ques_ir_gold.json`.</br>
c) Hotpot-style data for Bert RC using Break IR : in `./data/hotpot_data/hotpot_after_break_ir_gold.json`.</br>

The above command and outputs are corresponding to the gold (human-annotated) QDMRs indicated by the `--suffix gold` arg. We note that `run_break.py` will load the ranker & Wikipedia in the RAM and one should make sure to have enough memory. One can similarly repeat this step for the predicted QDMRs (copy_net, rule_based, etc) by using appropriate file paths and `--suffix` to change the output file names :
```
# copy-net
$ CUDA_VISIBLE_DEVICES=0 python run_break.py --qdmr_jsonl ./data/qdmr_data/qdmrs_hotpotqa_copy_net.jsonl --suffix copy_net --predict_batch_size 256

# rule-based
$ CUDA_VISIBLE_DEVICES=0 python run_break.py --qdmr_jsonl ./data/qdmr_data/qdmrs_hotpotqa_rule_based.jsonl --suffix rule_based --predict_batch_size 256
```
Each of these two commands will output 3 files as described above.

6) Navigate to `bert_rc` and use Bert RC (instructions in `bert_rc/README.md`) to make predicions for each of the multiple Hotpot-style files outputted by BreakRC. Make sure to provide appropriate `--pred_dir` arg to store the predictions for different hotpot-style files in different directories. For example in the copy_net case, for the Break IR hotpot-style file outputted by the previous step one can make predictions as :
```
$ cd bert_rc

# convert to squad format
$ python hotpot_to_squad2.py --max_n_samples -1 --data_type dev --data_file ../data/hotpot_data/hotpot_after_break_ir_copy_net.json --out_file examples_data/bert_rc_break_ir_copy_net.json

# use bert rc
$ CUDA_VISIBLE_DEVICES=0 python run_squad.py  --bert_model bert-base-uncased  --do_predict --do_evaluate --do_lower_case --predict_file examples_data/bert_rc_break_ir_copy_net.json  --predict_batch_size 128  --max_seq_length 500  --doc_stride 128   --output_dir ../data/bert_hotpot_67.3f1  --n_best_size 5 --preds_dir preds_break_ir_copy_net

$ cd ..
```
This will save `predictions.json` in `preds_break_ir_copy_net` directory.

7) Evaluate the IR performance, EM, F1 of the Break RC outputs and various Bert RC outputs:
```
python evaluate_break.py --data_dir ./data --input_results_file ./data/predictions/break_rc_results_copy_net.json --bert_rc_pred_files path1,path2
```
where argument to `--bert_rc_pred_files` is a comma separated list of paths to any number of `predictions.json` files outputted by Bert RC. The best performance will be obtained by Break IR + Bert RC as reported in the paper. 


*Notes*: 
1) Code was tested on `requirements.txt`.</br>
2) We are not including the IR baselines based on content words & noun phrases as they do not improve over the trivial whole-question baseline. The interested reader can refer to our paper for exact details.</br>


Contact: [Ankit Gupta](https://github.com/ag1988).