# Example Submissions
This directory contains several example submissions for testing the [evaluate.py](https://github.com/ehudreiter/accuracySharedTask/blob/main/evaluate.py) script.  The script takes arguments in the format:

`python evaluate.py $GOLD $SUBMISSION`

In bash, you can run this on all example submissions (from the root directory of the repo) with:

`for F in example_submissions/submission*.csv; do python evaluate.py --gsml=gsml.csv --submitted=$F --token_lookup=token_lookup.yaml ;done`



The script performs all evaluation at the sentence level.  But, if you submit only document level ids they will be automatically converted based on on our [token_lookup](https://github.com/ehudreiter/accuracySharedTask/blob/main/token_lookup.yaml).

The files are:
- [submission.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/submission.csv), an example submission which used simple Name/Number grounding.  This file has both document and sentence level token ids.  The script will check that they are consistent based on our [token_lookup](https://github.com/ehudreiter/accuracySharedTask/blob/main/token_lookup.yaml).  It will fail if document and sentence level ids do not match the known tokenization/sentencization for the documents.

- [submission_doc_based.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/submission_doc_based.csv), based on submission.csv, but with only document level tokens.  It will lookup the sentence level tokens then evaluate.

- [submission_sent_based.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/submission_sent_based.csv), based on submission.csv, but with only sentence level tokens.  It will lookup the document level tokens (although the sentence level ones are used for evaluation).

- [submission_malformed.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/submission_malformed.csv), based on submission.csv, but with some lines with sentence level tokenization, and others with document level.  The script will raise an Exception on this file.  You should submit either document level tokens, sentence level tokens, or both (on all lines).

- [submission_blank.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/submission_blank.csv), based on submission.csv, but with no token ids of any kind.  An Exception will be raised for this file.

- [gsml_doc_based.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/gsml_doc_based.csv), based on gsml.csv, but with only document level token ids.  This will trivially obtain 100% (we are comparing the GSML with itself).  This is for sanity checking the evaluate script.

- [gsml_sent_based.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/gsml_sent_based.csv), based on gsml.csv, but with only sentence level token ids.  This will trivially obtain 100% (we are comparing the GSML with itself).  This is for sanity checking the evaluate script.

