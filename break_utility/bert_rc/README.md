#### Finetuning BERT on HotpotQA.

The code is mostly modified from an older version of [HuggingFace](https://github.com/huggingface/transformers)'s SQuAD finetuning script. 

##### __Description__:
1) We arrange the context paras in decreasing order of tf-idf similarity to the question (we provide the similarity scores in `../data/hotpot_data/sorted_titles_train_distdev.json`).
2) To handle yes/no questions, we append the string `<aug> yes no </aug> <title> ...para_title.. </title>` before each each para. Then concatenate all the paras into a single context as in Squad.  
3) For train set, the finetuning script requires each sample to have exactly 1 answer span. So we use the one occurring in the supporting facts. For yes/no questions, we use the one in '<aug> yes no </aug>' appended to the first gold para.  
4) During evaluation, we use all occurring answer spans in all paras.  

##### __Usage__:
Navigate to the `bert_rc` directory and convert hotpot-format data into squad format using `hotpot_to_squad2.py` :
1) for hotpot training set: 
```
python hotpot_to_squad2.py --max_n_samples -1 --n_distractors 8 --data_type train --sorted_titles_hotpot ../data/hotpot_data/sorted_titles_train_distdev.json --data_file ../data/hotpot_data/hotpot_train_v1.json --out_file ./examples_data/train.json
```
2) for hotpot distractor set: 
```
python hotpot_to_squad2.py --max_n_samples -1 --n_distractors 8 --data_type dev --sorted_titles_hotpot ../data/hotpot_data/sorted_titles_train_distdev.json --data_file ../data/hotpot_data/hotpot_dev_distractor_v1.json --out_file ./examples_data/dev.json
```
3) in general, for evaluating any hotpot-style data:
```
python hotpot_to_squad2.py --max_n_samples -1 --data_type dev --data_file ../data/hotpot_data/hotpot_after_ques_ir_gold.json --out_file ./examples_data/bert_rc_eval.json
```
The outputs of the above commands will be stored in the directory `examples_data`. It is recommended that paras are already arranged according to tf-idf similarity w.r.t. the question as above.

Once we have the data in squad format, one can finetune/evaluate Bert as follows: 
1) Finetuning:
```
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6 python run_squad.py  --bert_model bert-base-uncased  --do_train  --do_predict --do_lower_case --train_file examples_data/train.json   --predict_file examples_data/dev.json   --train_batch_size 49   --predict_batch_size 630   --learning_rate 3e-5   --num_train_epochs 3.0   --max_seq_length 500   --doc_stride 128   --overwrite_output_dir   --output_dir ./out/  --preds_dir ./preds --n_best_size 5   --eval_period 2000 --load_from_cache 
```
The model checkpoints, etc will be stored in the output_dir directory `out` and the predictions in preds_dir `preds`. This should give ~ 67.3 F1 on hotpot distractor dev. One can view the exact training args that we used using `torch.load('../data/bert_hotpot_67.3f1/training_args.bin')`.

2) For making predictions using an already finetuned model (for e.g. stored in `../data/bert_hotpot_67.3f1`):
```
CUDA_VISIBLE_DEVICES=0,1,2,3 python run_squad.py  --bert_model bert-base-uncased  --do_predict --do_evaluate --do_lower_case --predict_file examples_data/dev.json  --predict_batch_size 630  --max_seq_length 500  --doc_stride 128   --output_dir ../data/bert_hotpot_67.3f1  --n_best_size 5 --preds_dir ./preds_hotpot_distdev
```
The predictions will be stored in the preds_dir `preds_hotpot_disdev`. One can adjust `--predict_batch_size` based on memory availability.

2) Evaluating the predictions using hotpot eval script:
```
python hotpot_evaluate_v1.py ./preds_hotpot_distdev/predictions.json  ../data/hotpot_data/hotpot_dev_distractor_v1.json
```


Contact: [Ankit Gupta](https://github.com/ag1988).

