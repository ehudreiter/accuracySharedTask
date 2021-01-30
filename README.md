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
* gold-standard markup list (GSML), which lists mistakes in these texts.  This is a comma separated file, with cells encased in double quotes.

Data for the games is available at [SportSett](https://github.com/nlgcat/sport_sett_basketball) (extended relational database) or [Rotowire](https://github.com/harvardnlp/boxscore-data) (original Rotowire JSON data).  GSML [gsml.xlsx](https://github.com/ehudreiter/accuracySharedTask/blob/main/gsml.csv) has ID's for SportSett, and line numbers for Rotowire.

