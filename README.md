# Shared Task in Evaluating Accuracy
Our shared task focuses on techniques for evaluating the factual accuracy of texts produced by data-to-text systems.   We welcome submissions of both automatic metrics and human evaluation protocols for this task.

As training and development data, we provide a set of generated texts which have been manually annotated to identify factual inaccuracies.  We will evaluate submissions to the shared task based on a separate test set of manually annotated texts, and will report recall and precision compared to the test set annotations of inaccuracies.   This will be reported both overall, and for different types of factual inaccuracies, including incorrect numbers, incorrect names, incorrect words, and contextual errors. 

The texts we use are descriptions of basketball games produced three different neural NLG systems, from box-score data.  The descriptions are 300 words long on average.

For detailed information on the shared task, see https://www.aclweb.org/anthology/2020.inlg-1.28/

## News
* 4 June - Submission: we will release the test set on 15 June, and ask you to email us your results by 29 June; we will compute precision/recall against gold-standard error annotations (these wpnt be released on 15 June).   Please also email us your code (for metrics) or protocol (for human evals) on or before 15 June.  We dont intend to run this ourselves, but want a record in case concerns arise about participants changing metric/protocol after seeing the test set.
* 1 June - evaluate.py updated to work at document level and report additional info about recall/precision at token level
* 17 May - added section about Tokenization
* 16 May - added information about accompanying papers to Shared task schedule

## Shared task schedule
* 15 December 2020: Shared task officially launched at INLG 2020
* 1 March 2021: Deadline for notifying us that you intend to participate in the shared task (please email   e.reiter@abdn.ac.uk )
* 31 March 2021: Evaluation script to be realeased.
* 15 June 2021: Submission of techniques (metrics and protocols).  We will release the test set (without annotations), and ask participants to try their techniques on the test set and give us results within 2 weeks.   We will compare the results against our gold-standard human annotations of inaccuracies, and compute recall and precision statistics.
* 12 July 2021: (Optional) Submission of short papers about shared task entries.  These should follow the format of INLG short papers, but do not need to be anonymised.  We will review and provide comments by 26 July
* 1 August 2021: Results announced
* 12 August 2021: Camera-ready versions of (optional) short papers due
* 20-24 Sept 2021: Presentation of shared task at INLG 2021 (https://inlg2021.github.io/)

For more information or to register interest, please email Ehud Reiter at   e.reiter@abdn.ac.uk


## What is in this repo
This repository contains a set of 60 accuracy-annotated texts for the shared task, some of which were extracted from https://github.com/nlgcat/evaluating_accuracy. 
* texts: the source [texts](https://github.com/ehudreiter/accuracySharedTask/blob/main/texts) produced by neural NLG systems, which describe basketball box score data
* word_docs: word documents used in human experiments.  Page 6 includes the texts (same as in texts directory) and links which human subjects can use to get data about the games
* gold-standard markup list ([gsml.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/gsml.csv)), which lists mistakes in these texts.  This is a comma separated file, with cells encased in double quotes.
* appropriate subset of Rotowire JSON: For convenience, we have included the file [shared_task.jsonl](https://github.com/ehudreiter/accuracySharedTask/blob/main/shared_task.jsonl) which includes the lines from the Rotowire test set, for each of our annotated documents.
* game information ([games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/games.csv)): Information on the games we annotated to create the GSML.
* example annotation exercise ([example_exercise](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_exercise)):  An example annotation exercise to familiarize yourself with the task.
* evaluation script ([evaluate.py](https://github.com/ehudreiter/accuracySharedTask/blob/main/evaluate.py)) and [example_submissions](https://github.com/ehudreiter/accuracySharedTask/tree/main/example_submissions): To demonstrate how recall and precision are calculated.

Data for all games is available at [Rotowire](https://github.com/harvardnlp/boxscore-data) (original Rotowire JSON data).  it is also available at [SportSett](https://github.com/nlgcat/sport_sett_basketball) (extended relational database).  Please note that SportSett currently does not included playoff games, but does provide much more information on regular season games.

Please note that prior to the commits on Monday 22nd February, the line for S042 in [games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/games.csv) was incorrect (it referred to an incorrect game which is not part of the shared task).  There was also an issue with the GSML for S029.  Both of these have been fixed, but please make sure you are on the most recent version of this repository.

### [games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/games.csv) columns
1. DOC_ID: The ID for the summary within our shared task.  These match the filenames in [texts](https://github.com/ehudreiter/accuracySharedTask/blob/main/texts).
2. HOME_NAME: The name of the home team.
3. VIS_NAME: The name of the visiting team.
4. LINE_ID_FROM_TEST_SET: The line from the original [Rotowire](https://github.com/harvardnlp/boxscore-data) test set that this game came from.  Note that line numbers start at zero (position within the JSON file)
5. GENERATED_TEXT: The text that was generated by a neural data-to-text system using the data for this game.  This text has been cleaned by us to allow for error annotation to be performed in [WebAnno](https://webanno.github.io/webanno).  The most common example of this is names like "C.J." are replaced with "CJ" (for sentence boundary detection).  These generated texts are tokenized then joined by a single space.  This is what we annotated in WebAnno, and was used to generate the GSML.
6. DETOKENIZED_GENERATED_TEXT: The same as generated texts, but detokenized such that whitespace is as it should be in English.  This is what we gave to the Mechanical Turkers.
7. DATE: The date from the [Rotowire](https://github.com/harvardnlp/boxscore-data) JSON format.  MM_DD_YY.
8. BREF_BOX: A link to the box score and other statistics for the game, in [basketball-reference.com](https://www.basketball-reference.com)
9. BREF_HOME: A link to the season schedule for the home team, in  [basketball-reference.com](https://www.basketball-reference.com)
10. BREF_VIS: A link to the season schedule for the visiting team, in  [basketball-reference.com](https://www.basketball-reference.com)
11. CALENDAR: A link to a calander for the month the game was played in (we provided this to Turkers for convenience).

### [gsml.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/gsml.csv) columns
1. TEXT_ID: The ID for the summary within our shared task.  These match the filenames in [texts](https://github.com/ehudreiter/accuracySharedTask/blob/main/texts).
2. SENTENCE_ID: The sentence number with each summary (starting at 1, comes from WebAnno).
3. ANNOTATION_ID: A global ID for the annotation (error).
4. TOKENS: The tokens which were highlighted as a mistake, joined by a single space.
5. SENT_TOKEN_START: The start token position within the sentence (starting at 1, comes from WebAnno).
6. SENT_TOKEN_END: The end token position within the sentence (starting at 1, comes from WebAnno).
7. DOC_TOKEN_START: Like SENT_TOKEN_START except relative to the document start.
8. DOC_TOKEN_END: Like SENT_TOKEN_END except relative to the document start.
9. TYPE: The category that was agreed upon by our annotators for the error.
10. CORRECTION: The correction given (if it could be substituted directly and be almost grammatically correct).
11. COMMENT: If a direct CORRECTION cannot be made without a major rewrite of the sentence, or if the CORRECTION needs clarification.

A note on CORRECTION and COMMENT: NAME and NUMBER errors are mostly corrections (they are easier to directly substitute), WORD and CONTEXT are mostly COMMENT.

### [shared_task.jsonl](https://github.com/ehudreiter/accuracySharedTask/blob/main/shared_task.jsonl) details
This file is in the the same format as [Rotowire](https://github.com/harvardnlp/boxscore-data), except that each line contains a dictionary representing one game record.  This makes it easier to read than one massively long line.  Three keys were added:

1. shared_task_text_id: maps to our TEXT_ID above.
2. cleaned_text: the human authored (gold) text from the test set, cleaned as above.
2. cleaned_detokenized_text: the human authored (gold) text from the test set, cleaned and detokenized as above.

### [example_exercise](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_exercise)
In order to familiarize yourself with the problem, as well as the process by which our GSML was created, we suggest that participants annotate one text manually for errors themselves.  For this purpose, we have included an updated version of the qualifying task which we used to screen our crowd-source workers.  The [Example Annotation Exercise](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_exercise/Example_Annotation_Exercise.docx) file contains the instructions we gave to workers, an example annotated text, then a text for you to annotate yourself.  This is not a requirement, although we do think it is a very useful exercise to do, and should only take about 20-30 minutes.  We have provided our solution in the [Example Annotation Solution](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_exercise/Example_Annotation_Solution.docx) document.  This example exercise only differs slightly from that which our MTurk workers when they first started doing annotations for us.  Since then, we have made some minor clarifications to our instructions, it is these updated instructions which have been included here.

### [evaluate.py](https://github.com/ehudreiter/accuracySharedTask/blob/main/evaluate.py)
Python script to calculate recall and precision of submitted annotations against the GSML.  Example submissions are provided ([example_submissions](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions)).  The token_lookup.yml file contains a mapping from sentence to document based tokenization and vice versa.

Example use:
`python evaluate.py --gsml=gsml.csv --submitted=example_submissions/submission.csv --token_lookup=token_lookup.yaml`

This script outputs:
1. Mistake Recall - We consider correct recall as when a submitted mistake overlaps a GSML mistake.  Once a submitted mistake recalls a GSML mistake, the submitted mistake is consumed (it cannot be used to for recall of future GSML mistakes).  Mistakes are iterated left-to-right based on the DOC_TOKEN_START value.  None of the GSML mistakes span multiple sentences.  Please remember that overlapping mistake spans are not permitted.
2. Mistake Precision - Mistakes are consumed in the same way.
3. Token Recall - The recall at the token level (where mistakes are not consumed, as tokens are our atomic units).
4. Token Precision - The precision at the token level

It is possible for two submitted mistakes to overlap the same GSML mistake.  For example, "Miami Heat" [NAME] could be the gold error, but a submission could have separate submissions of "Miami" [NAME] and "Heat" [NAME].  In this case we would award one instance of both correct recall and precision at the mistake level.  At the token level this is not an issue.

Overlapping token spans within one mistake list are not allowed.  For example, a submission cannot include "The Miami" and "Miami Heat" as mistakes on the sequential tokens "The Miami Heat".

We also calculate per-category recall and precision, the console output first shows the results overall, followed by the results for each category individually.  Some example submissions for testing this script can be found in [example_submissions](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions) with an additional [README](https://github.com/ehudreiter/accuracySharedTask/blob/main/example_submissions/README.md) detailing their content.

PLEASE NOTE:  Results are calculated using document level token IDs, although if you only include sentence level token IDs (and sentence numbers), and this matches our tokenization scheme, then document level IDs will be calculated automatically.

### Tokenization
Our texts (GENERATED_TEXT) are already tokenized then joined with spaces.  The only sentence delimiting character is the period.  The [evaluate.py](https://github.com/ehudreiter/accuracySharedTask/blob/main/evaluate.py) script will be updated such that it uses document level token ids rather than sentence level ones.  This will make no difference to the way submisions are evaluated, but will mean participants who do not wish to consider sentence breaks do not have to.  It is, however, important that any submissions use the same tokenization as our original texts.

Additional info / background:  The original Rotowire corpus, and texts generated from it, used the nltk tokenizer.  The corpus includes tokenized text as a list with no original format texts.  However, the nltk tokenizer performs poorly on this dataset, tripping over names like C.J. Miles and sometimes not splitting tokens correctly (the vocabulary inludes things like "game.The" as one token).  The spaCy parser also struggles with such names, as does whichever parser WebAnno uses, they end sentences after "C.J.".  WebAnno also tried to split tokens differently, with words like "didn't" becoming three tokens where nltk and spaCy created two.  Therefore, since different parsers not only split sentences differently, but also tokens, we need to use a simple, standard scheme.  The training texts are already formatted by this scheme (albeit joined by whitespace so they are still human readble), and the test texts will be processed in the same way.  If you want to use tools like spaCy to perform, for example, some kind of dependency analysis, then you can, but make sure your submitted token ids align with those from the simple tokenization scheme above.

Note on tokens containing the characters "000":  Because WebAnno was attempting to apply additional tokenization over our already tokenized text, we had to replace apostrophe characters with "000" (a sequence of characters not otherwise in the corpus).  We then replaced this special sequence with apostrophes after the WebAnno export.  However, three of the files in the [texts](https://github.com/ehudreiter/accuracySharedTask/blob/main/texts) directory appear to not have had this replacement applied.  These tokens were never part of any marked errors in the GSML, which is why the test script missed them (it has been updated to check for this, and to check our tokenization scheme wrt the WebAnno export).  The most recent commit has rectified this.  Such tokens are till present in the WebAnno [curations](https://github.com/ehudreiter/accuracySharedTask/blob/main/curations) which are now also included in the repo in their raw export form.

### Reading the Box Score (fields in shared_task.jsonl)
Below are definitions of field labels which might not be familiar if you do not follow basketball.  They come from the [Box Score](https://en.wikipedia.org/wiki/Box_score), and whilst some of the headers can differ slightly depending on the source, the ones in the [Rotowire](https://github.com/harvardnlp/boxscore-data), which is the format our data is in are:

#### Basic statistics
* PTS: [Points](https://en.wikipedia.org/wiki/Point_(basketball)) scored ((2&ast;FGM) + FTM + FG3M)
* REB: total [Rebounds](https://en.wikipedia.org/wiki/Rebound_(basketball))
* AST: total [Assists](https://en.wikipedia.org/wiki/Assist_(basketball))
* BLK: total [Blocks](https://en.wikipedia.org/wiki/Block_(basketball))
* STL: total [Steals](https://en.wikipedia.org/wiki/Steal_(basketball))
* TO:  total [Turnovers](https://en.wikipedia.org/wiki/Turnover_(basketball))
* PF: total [Personal foul](https://en.wikipedia.org/wiki/Personal_foul_(basketball))

NB: OREB (offensive) and DREB (defensive) are sub-categories of rebound, (OREB + DREB) = REB

#### Shooting statistics
There are also shooting statistics, which show how many types of each shot a person attempted (A) and how many they made (M)

* FGM:  [Field goals](https://en.wikipedia.org/wiki/Field_goal_(basketball)) made
* FGA:  [Field goals](https://en.wikipedia.org/wiki/Field_goal_(basketball)) attempted
* FG3M: [Three-point field goals](https://en.wikipedia.org/wiki/Three-point_field_goal) made
* FG3A: [Three-point field goals](https://en.wikipedia.org/wiki/Three-point_field_goal) attempted
* FTM:  [Free-throws](https://en.wikipedia.org/wiki/Free_throw) made
* FTA:  [Free-throws](https://en.wikipedia.org/wiki/Free_throw) attempted

The three-point shooting statistics should be read as: "Of the total field goals, how many of them were worth three points"

#### Shooting percentages
There are also shooting percentages.  All such fields end in "&lowbar;PCT", such as "FG&lowbar;PCT", FG3&lowbar;PCT", and "FT&lowbar;PCT".  In all cases, they are simply derived from MADE/ATTEMPTED.

#### Names
The data also includes player, team, and place names, those should be self-explanatory.

### SQL Query for SportSett to get game_ids from rotowire line numbers
Note that playoff games are not currently available in SportSett.  It will, however, give complete access to every regular season game, including the league structure and schedule.  All games in the shared task are regular season games.  

Pleas also note that some additional denormalized tables have been added to [SportSett](https://github.com/nlgcat/sport_sett_basketball) to try and make it easier to use.  You do not have to use this resource for the shared task, but it is available if you want to use it.  The generated texts used the original Rotowire corpus as their training input.  Links to statistics websites are also included in [games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/games.csv)

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
    563,419,614,384,719,306,408,496,285,153,
    366,365,230,207,637,307,667,564,185,107,
    671,561,653,212,219,104,511,137,324,427,
    680,259,309,152,391,378,434,75,426,377,
    332,600,336,346,457,22,705,479,151,623,
    368,146,435,208,364,414,573,33,726,8
);
```
