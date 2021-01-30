# Shared Task in Evaluating Accuracy
Our shared task focuses on techniques for evaluating the factual accuracy of texts produced by data-to-text systems.   We welcome submissions of both automatic metrics and human evaluation protocols for this task.

As training and development data, we provide a set of generated texts which have been manually annotated to identify factual inaccuracies.  We will evaluate submissions to the shared task based on a separate test set of manually annotated texts, and will report recall and precision compared to the test set annotations of inaccuracies.   This will be reported both overall, and for different types of factual inaccuracies, including incorrect numbers, incorrect names, incorrect words, and contextual errors. 

The texts we use are descriptions of basketball games produced three different neural NLG systems, from box-score data.  The descriptions are 300 words long on average.

For detailed information on the shared task, see https://www.aclweb.org/anthology/2020.inlg-1.28/

## Shared task schedule
* 15 December 2020: Shared task officially launched at INLG 2020
* 15 February 2021: Deadline for notifying us that you intend to participate in the shared task (please email   e.reiter@abdn.ac.uk )
* 15 June 2021: Submission of techniques (metrics and protocols).  We will release the test set (without annotations), and ask participants to try their techniques on the test set and give us results within 2 weeks.   We will compare the results against our gold-standard human annotations of inaccuracies, and compute recall and precision statistics.
* 1 August 2021: Results announced
* Sept 2021: Presentation of shared task at INLG 2021

For more information or to register interest, please email Ehud Reiter at   e.reiter@abdn.ac.uk

## What is in this repo
This repository contains an initial set of 21 accuracy-annotated texts for the shared task, extracted from https://github.com/nlgcat/evaluating_accuracy, plus 6 new texts annotated by the same method.  It is our intention to have a total of 60 texts available by the February 15th 2021 deadline, but we wanted to make what we have already available for participants to view.  Note that the numbering of the texts in the initial set is from 5-18 and 22-28, the final set will have sequential numbering from 1 to 60.
* texts: the source texts produced by neural NLG systems, which describe basketball box score data
* word_docs: word documents used in human experiments.  Page 6 includes the texts (same as in texts directory) and links which human subjects can use to get data about the games
* gold-standard markup list ([gsml.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/gsml.csv)), which lists mistakes in these texts.  This is a comma separated file, with cells encased in double quotes.

Data for the games is available at [SportSett](https://github.com/nlgcat/sport_sett_basketball) (extended relational database) or [Rotowire](https://github.com/harvardnlp/boxscore-data) (original Rotowire JSON data).  Please note that SportSett currently does not included playoff games, whilst the original Rotowire partitions (and our annotated texts) do.

For convenience, we have included the file [shared_task.jsonl](https://github.com/ehudreiter/accuracySharedTask/blob/main/shared_task.jsonl) which includes the lines from the Rotowire test set, for each of our annotated documents.  This is in the format of one JSON entry per line (rather than one very long line like the original Rotowire dataset).  They are in the same order as [games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/games.csv) and a key (shared_task_document_id) has also been added for reference.  Please note that the tokenization scheme in the gold texts within the JSON is slightly different from that which we annotated (we had to clean it up).  We have included clean gold texts in [games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/games.csv) (CT: Still to add these).

The [games.csv](https://github.com/ehudreiter/accuracySharedTask/blob/main/games.csv) file has line numbers for Rotowire (the test set), as well as the human authored text for the game if.  It also includes some additional information that was used in the creation of the MS Word documents (such as links to statistics websites).

**SQL Query for SportSett to get game_ids from rotowire line numbers**
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
    AND rotowire_entries.id IN (720,307,409,497,286,154,367,366,231,208,638,308,668,565,562,654,213,220,105,512,138,681,260,392,379,415,727);
```