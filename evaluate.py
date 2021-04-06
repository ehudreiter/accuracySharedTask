import csv
import json
import pprint
from copy import deepcopy
pp = pprint.PrettyPrinter(indent=4)

"""
  It is possible for a metric to present multiple annotations which map to one annotation in the GSML.
     or vice verse.
  For example, "Miami Heat" could be a 2-token error "Miami Heat".
     or two 1-token errors "Miami" (wring city) "Heat" (wrong name).
  We award correct recall when at least one submitted mistake matches a GSML mistake.
  We award correct precision when a submitted mistake matches at least one GSML mistake.
  Mistakes are said to match when their ranges of token ids overlap.
  Once a submitted mistake has recalled a GSML mistake, the submitted mistake is consumed
    - It cannot recall a subsequent GSML mistake
"""

''' Returns the category labels described in the paper '''
def all_categories():
  return ['NAME', 'NUMBER', 'WORD', 'CONTEXT', 'NOT_CHECKABLE', 'OTHER']

"""
  Creates and returns a dictionary representation of the mistake list (GSML or Submission)
  The dictiory is structured as:
  TEXT_ID
    SENTENCE_ID
      START_IDX
        MISTAKE_DATA
  The function returns a tuple where the first element is the dict, and the second is num_mistakes
"""
def create_mistake_dict(filename, categories):
  mistake_dict = {}
  matches = 0
  with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(reader, None)

    num_mistakes = 0

    for i, row in enumerate(reader):
      # Columns from gthe CSV
      text_id = row[0].replace('.txt','')
      sentence_id = int(row[1])
      annotation_id = int(row[2])
      tokens = row[3]
      start_idx = int(row[4])
      end_idx = int(row[5])
      category = row[8]

      if category not in categories:
        continue

      if text_id not in mistake_dict: mistake_dict[text_id] = {}
      if sentence_id not in mistake_dict[text_id]: mistake_dict[text_id][sentence_id] = {}
      mistake_dict[text_id][sentence_id][start_idx] = {
        'set':            set(range(start_idx, end_idx+1)),
        'category':       category,
        'start_idx':      start_idx,
        'sentence_id':    sentence_id,
        'annotation_id':  annotation_id,
        'tokens':         tokens,
      }
      num_mistakes += 1
  return mistake_dict, num_mistakes

"""
  Recall is when at least one submitted mistake overlaps the GSML mistake
  - once a submitted mistake has been used for correct recall, it cannot be used again (it is consumed).
  Precision is when a submitted mistake overlaps any GSML mistake.
"""
def match_mistake_dicts(gsml, submitted):
  per_gsml_recall_matches = {}
  per_submitted_precision_matches = {}
  overlaps = []

  for text_id, gsml_text_data in gsml.items():
    for sentence_id, gsml_sentence_data in gsml_text_data.items():
      # Within a sentence, record submitted_start_idx that have been used for correct recall
      used_submissions = set([])
      for start_idx, gsml_error_data in gsml_sentence_data.items():
        recall_match = False
        precision_matches = set([])
        if text_id in submitted and sentence_id in submitted[text_id]:
          for submitted_start_idx, submitted_error_data in submitted[text_id][sentence_id].items():
            isect = submitted_error_data['set'].intersection(gsml_error_data['set'])
            if isect:
              # Award correct precision regardless
              precision_matches.add(submitted_start_idx)
              overlaps.append(float(len(isect)) / float(len(gsml_error_data['set'])))

              # If the submission has been used already for correct recall, do not use it again
              if submitted_start_idx not in used_submissions:
                # Do not consume multiple submitted mistakes, only the first
                if not recall_match:
                  gsml_tokens = gsml_error_data['tokens']
                  submitted_tokens = submitted_error_data['tokens']
                  recall_match = True
                  used_submissions.add(submitted_start_idx)

        per_gsml_recall_matches[f'{text_id}_{sentence_id}_{start_idx}'] = recall_match
        per_submitted_precision_matches[f'{text_id}_{sentence_id}_{start_idx}'] = precision_matches
  return per_gsml_recall_matches, per_submitted_precision_matches, overlaps

"""
  Returns the recall, precision and overlaps between a GSML and a submission
  Takes as input dicts created with match_mistake_dicts(), plus a list of categories
  Only the categories given will be checked.
"""
def calculate_recall_and_precision(gsml_filename, submitted_filename, categories=[]):
  gsml, gsml_num_lines = create_mistake_dict(gsml_filename, categories)
  submitted_gsml, submitted_num_lines = create_mistake_dict(submitted_filename, categories)
  recall_matches, precision_matches, overlaps = match_mistake_dicts(gsml, submitted_gsml)

  # Recall
  correct_recall = len([k for k, v in recall_matches.items() if v])
  incorrect_recall = len([k for k, v in recall_matches.items() if not v])
  assert (correct_recall + incorrect_recall) == gsml_num_lines
  if gsml_num_lines > 0:
    recall = correct_recall / gsml_num_lines
  else:
    recall = None

  # Precision
  correct_precision = sum([len(v) for k, v in precision_matches.items()])
  if submitted_num_lines > 0:
    precision = correct_precision / submitted_num_lines
  else:
    precision = None

  # Overlaps
  if len(overlaps):
    mean_overlap = float(sum(overlaps)) / float(len(overlaps))
  else:
    mean_overlap = None

  return recall, precision, mean_overlap

"""
  Check all catogories combined, as well as each category individually
"""
categories_list = [all_categories()] + [[x] for x in all_categories()]

for categories in categories_list:
  category_display_str = ', '.join(categories)
  print(f'\n-- GSML for categories: {category_display_str}')

  recall, precision, mean_overlap = calculate_recall_and_precision('gsml.csv', 'submitted_gsml.csv', categories)
  print(f'GSML vs example: recall => {recall}, precision => {precision}, overlap => {mean_overlap}')

  recall, precision, mean_overlap = calculate_recall_and_precision('gsml.csv', 'gsml.csv', categories)
  print(f'GSML vs example: recall => {recall}, precision => {precision}, overlap => {mean_overlap}')