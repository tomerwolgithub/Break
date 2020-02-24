# Break: A Question Understanding Benchmark

This repository contains code by [Mor Geva](https://mega002.github.io/), [Ankit Gupta](https://sites.google.com/view/ag1988/home) and [Tomer Wolfson](https://github.com/tomerwolgithub) for our paper, ["Break It Down: A Question Understanding Benchmark"](https://arxiv.org/abs/2001.11770v1) (TACL 2020). The repository features the codebase and models from our paper.   
For the Break dataset please refer to: [https://allenai.github.io/Break](https://allenai.github.io/Break)

Break is a human annotated dataset of natural language questions and their Question Decomposition Meaning Representations (QDMRs). Break consists of 83,978 examples sampled from 10 question answering datasets over text, images and databases.


### Changelog
- `2/24/2020` Open-domain QA experiments are now [available](https://github.com/tomerwolgithub/Break/tree/master/break_utility)!
- `2/20/2020` QDMR parsing models and evaluation are now [available](https://github.com/tomerwolgithub/Break/tree/master/qdmr_parsing)!
- `2/1/2020` The full dataset has been publicly released at [https://allenai.github.io/Break](https://allenai.github.io/Break/).

## Structure
The repository features:
* The [QDMR Parsing models](https://github.com/tomerwolgithub/Break/tree/master/qdmr_parsing), by [**Mor Geva**](https://mega002.github.io/)
* The [Open-domain QA models](https://github.com/tomerwolgithub/Break/tree/master/break_utility) utilizing QDMR, by [**Ankit Gupta**](https://sites.google.com/view/ag1988/home)
* The [annotation pipeline](https://github.com/tomerwolgithub/Break/tree/master/annotation_pipeline) of Break
* Code for converting [QDMR to logical-form](https://github.com/tomerwolgithub/Break/tree/master/qdmr_to_logical_form)


## Reference

```
@article{Wolfson2020Break,
  title={Break It Down: A Question Understanding Benchmark},
  author={Wolfson, Tomer and Geva, Mor and Gupta, Ankit and Gardner, Matt and Goldberg, Yoav and Deutch, Daniel and Berant, Jonathan},
  journal={Transactions of the Association for Computational Linguistics},
  year={2020},
}
```
