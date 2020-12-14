# Shared Task in Evaluating Accuracy
For more information on the shared task, see https://www.aclweb.org/anthology/2020.inlg-1.28/

## Shared task schedule
* 15 December 2020: Shared task officially launched at INLG 2020
* 15 February 2021: deadline for registration
* 15 June 2021: submission of techniques (algorithms and protocols).  Test set released, participants must give results within 2 weeks
* 1 August 2021: results announced
* Sept 2021: presentation of shared task at INLG 2021

For more information or to refister interest, please email Ehud Reiter at   e.reiter@abdn.ac.uk

## What is in this repo
This repository contains an initial set of 21 accuracy-annotated texts for the shared task, extracted from https://github.com/nlgcat/evaluating_accuracy
We will expand the size of this set.  Note that the numbering of the texts in the initial set is from 5-18 and 22-28
* texts: the source texts produced by neural NLG systems, which describe basketball box score data
* word_docs: word documents used in human experiments.  Page 6 includes the texts (same as in texts directory) and links which human subjects can use to get data about the games
* gold-standard markup list (GSML), which lists mistakes in these texts

Data for the games is available at https://github.com/nlgcat/sport_sett_basketball (extended relational database) and https://github.com/harvardnlp/boxscore-data (original Rotowire JSON data).  The generated_text_info tab of https://github.com/ehudreiter/accuracySharedTask/blob/main/gsml.xlsx has ID's for SportSett, and line 
numbers for Rotowire.
