# Shared Task Test set

This zip folder contains the shared task test set.  It includes the same types of files that were included in the repository for the training data, but for a different 30 texts/games.

We include here:
- games.csv => The list of games, with the links to external resources.
- gsml.csv => This contains the errors our human annotors found in the 30 test texts.
- shared_task.jsonl => The training data that was used to generate the text.  In JSONL format (one dictionary per line, in order based on the text IDs)
- texts => A directory containing the unannotated texts for the test set.
- token_lookup.yaml => A lookup of sentence based token ids to document based ones and vice versa.

# Instructions for participants


## What we need from you
We need a CSV file in the same format as the GSML.  An example can be found in [example_submissions/submission.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/submission.csv) of the Git repo.  Your submission must include the following columns, in this order:

- TEXT_ID => REQUIRED
- SENTENCE_ID
- ANNOTATION_ID
- TOKENS => REQUIRED
- SENT_TOKEN_START
- SENT_TOKEN_END
- DOC_TOKEN_START => REQUIRED
- DOC_TOKEN_END => REQUIRED
- TYPE => REQUIRED
- CORRECTION
- COMMENT

Only the columns marked "REQUIRED" are required.  You can leave the others blank if you wish.

You can include the CORRECTION/COMMENT if your method can detect them, although these are not part of the evaluation.

The evaluation script uses the document level token ids (DOC_TOKEN_START, DOC_TOKEN_END) although it will convert from the sentence level token ids (SENTENCE_ID, SENT_TOKEN_START, SENT_TOKEN_END) if you provide those.  You can include either only sentence level ids (in which case those three columns become "REQUIRED"), or document level ids, or both (provided they match).  

## Checking that tokenization is OK in your submission

You can check your submission against itself (as if it were the list of gold errors).  Obviously this should result in 1.0 precision and recall, but it will trigger the checks in our script that ensure the text you have included in the TOKENS field matches the text that is found in the texts/ directory at the given token ids.  This will check the internal consistency of your submission.

`python evaluate.py --gsml=submission.csv --submitted=submission.csv --token_lookup=test_set_unannotated/token_lookup.yaml`

If you have any problems with tokenization, or do not understand the format, please let us know and we can answer any questions.  Different tokenizers (NLTK, spaCy, and WebAnno which as a Java app might be using Stanford) have been tokenizing differently in some cases.  This is why we had to give you an explicit tokenization scheme (split the text on whitespace to obtain tokens, then sentence boundaries are on periods).  If the tokens ids in your submission are skewed, then it will likely affect your results negatively (if the evaluate.py script is able to process it at all).

### Query for SportSett
If you have been using this database, here is how to get the game IDs from the Rotowire test set line IDS.  These are the line numbers from the games.csv file (note the SQL query returns the games in a different order, you need to match the line_number to those in games.csv)

```
SELECT games.id AS game_id,
       rotowire_entries.rw_line AS line_number,
       rotowire_entries.summary AS gold_text
FROM rotowire_entries
LEFT JOIN dataset_splits
ON        dataset_splits.id = rotowire_entries.dataset_split_id
LEFT JOIN games_rotowire_entries
ON        games_rotowire_entries.rotowire_entry_id = rotowire_entries.id
LEFT JOIN games
ON        games.id = games_rotowire_entries.game_id
WHERE dataset_splits.name='test'
AND rotowire_entries.rw_line IN (
    369,290,55,709,454,382,586,247,647,591,
  100,602,83,508,162,439,399,562,158,59,
  142,582,231,373,514,358,68,438,488,417
);
```
