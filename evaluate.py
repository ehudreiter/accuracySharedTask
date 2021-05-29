import csv
import json
import pprint
import sys
import yaml
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

''' Returns an int or None '''
def csv_int(x):
  return int(x) if x else None

def consistent_tokenization(tokenization_mode, current_line_mode):
  if tokenization_mode not in {None, current_line_mode}:
    raise Exception('You must consistently use either document-based, sentence-based or both for the tokenization method.')
  return current_line_mode

"""
  Creates and returns a dictionary representation of the mistake list (GSML or Submission)
  The dictiory is structured as:
  TEXT_ID
    SENTENCE_ID
      START_IDX
        MISTAKE_DATA
  The function returns a tuple where the first element is the dict, and the second is num_mistakes
"""
def create_mistake_dict(filename, categories, token_lookup):
  mistake_dict = {}
  matches = 0
  with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(reader, None)

    num_mistakes = 0

    tokenization_mode = None

    for i, row in enumerate(reader):
      # Columns from the CSV
      text_id         = row[0].replace('.txt','')
      sentence_id     = csv_int(row[1])
      annotation_id   = csv_int(row[2])
      tokens          = row[3]
      sent_start_idx  = csv_int(row[4])
      sent_end_idx    = csv_int(row[5])
      doc_start_idx   = csv_int(row[6])
      doc_end_idx     = csv_int(row[7])
      category        = row[8]

      # Check the sanity of the token submissions
      sent_given = (sent_start_idx != None and sent_end_idx != None and sentence_id != None)
      doc_given = (doc_start_idx != None and doc_end_idx != None)

      if sent_given and doc_given:
        tokenization_mode = consistent_tokenization(tokenization_mode, 'BOTH')
        # Check mapping from sent to doc tokenization matches our token_lookup
        assert doc_start_idx == token_lookup['sent_to_doc'][text_id][sentence_id][sent_start_idx]
        assert doc_end_idx == token_lookup['sent_to_doc'][text_id][sentence_id][sent_end_idx]
        # And doc to sent
        assert sentence_id == token_lookup['doc_to_sent'][text_id][doc_start_idx]['sentence_id']
        assert sent_start_idx == token_lookup['doc_to_sent'][text_id][doc_start_idx]['token_id']
        assert sent_end_idx == token_lookup['doc_to_sent'][text_id][doc_end_idx]['token_id']
      elif sent_given:
        tokenization_mode = consistent_tokenization(tokenization_mode, 'SENT')
        doc_start_idx = token_lookup['sent_to_doc'][text_id][sentence_id][sent_start_idx]
        doc_end_idx   = token_lookup['sent_to_doc'][text_id][sentence_id][sent_end_idx]
        # row[6] = doc_start_idx
        # row[7] = doc_end_idx
        # print('"' + '","'.join(str(r) for r in row) + '"')
      elif doc_given:
        tokenization_mode = consistent_tokenization(tokenization_mode, 'DOC')
        sentence_id = token_lookup['doc_to_sent'][text_id][doc_start_idx]['sentence_id']
        sent_start_idx = token_lookup['doc_to_sent'][text_id][doc_start_idx]['token_id']
        sent_end_idx = token_lookup['doc_to_sent'][text_id][doc_end_idx]['token_id']
      else:
        raise Exception(f'You must provide either document or sentence based token ids on {filename} row {i}')

      if category not in categories:
        continue

      if text_id not in mistake_dict: mistake_dict[text_id] = {}
      if sentence_id not in mistake_dict[text_id]: mistake_dict[text_id][sentence_id] = {}
      mistake_dict[text_id][sentence_id][sent_start_idx] = {
        'set':            set(range(sent_start_idx, sent_end_idx+1)),
        'category':       category,
        'sent_start_idx': sent_start_idx,
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
      # Within a sentence, record submitted_sent_start_idx that have been used for correct recall
      used_submissions = set([])
      for sent_start_idx, gsml_error_data in gsml_sentence_data.items():
        recall_match = False
        precision_matches = set([])
        if text_id in submitted and sentence_id in submitted[text_id]:
          for submitted_sent_start_idx, submitted_error_data in submitted[text_id][sentence_id].items():
            isect = submitted_error_data['set'].intersection(gsml_error_data['set'])
            if isect:
              # Award correct precision regardless
              precision_matches.add(submitted_sent_start_idx)
              overlaps.append(float(len(isect)) / float(len(gsml_error_data['set'])))

              # If the submission has been used already for correct recall, do not use it again
              if submitted_sent_start_idx not in used_submissions:
                # Do not consume multiple submitted mistakes, only the first
                if not recall_match:
                  gsml_tokens = gsml_error_data['tokens']
                  submitted_tokens = submitted_error_data['tokens']
                  recall_match = True
                  used_submissions.add(submitted_sent_start_idx)

        per_gsml_recall_matches[f'{text_id}_{sentence_id}_{sent_start_idx}'] = recall_match
        per_submitted_precision_matches[f'{text_id}_{sentence_id}_{sent_start_idx}'] = precision_matches
  return per_gsml_recall_matches, per_submitted_precision_matches, overlaps

"""
  Returns a dict containing sub-dicts of recall, precision and overlaps between a GSML and a submission
  Takes as input dicts created with match_mistake_dicts(), plus a list of categories
  Only the categories given will be checked.
"""
def calculate_recall_and_precision(gsml_filename, submitted_filename, token_lookup, categories=[]):
  gsml, gsml_num_lines = create_mistake_dict(gsml_filename, categories, token_lookup)
  submitted_gsml, submitted_num_lines = create_mistake_dict(submitted_filename, categories, token_lookup)
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

  sum_overlap = float(sum(overlaps))
  len_overlap = float(len(overlaps))
  # Overlaps
  if len(overlaps):
    mean_overlap = sum_overlap / len_overlap
  else:
    mean_overlap = None

  return {
    'recall': {
      'value': recall,
      'correct': correct_recall,
      'of_total': gsml_num_lines
    },
    'precision': {
      'value': precision,
      'correct': correct_precision,
      'of_total': submitted_num_lines
    },
    'overlap': {
      'value': precision,
      'sum_overlap': sum_overlap,
      'len_overlap': len_overlap
    }
  }


"""
  Load the token_lookup from YAML
"""

with open('token_lookup.yaml', 'r') as fh:
  token_lookup = yaml.full_load(fh)

"""
  Check all catogories combined, as well as each category individually
"""
categories_list = [all_categories()] + [[x] for x in all_categories()]

# Pass the GSML and the submission and CSL args
gsml_filename = sys.argv[1]
submitted_filename = sys.argv[2]

print('\n\n')
print('-' * 80)
print('GSML: EVALUATE')
print(f'comparing GSML => "{gsml_filename}" to submission => "{submitted_filename}"')

def format_result_value(value, dcp=3):
  if value:
    return round(value, dcp)
  return None

for categories in categories_list:
  category_display_str = ', '.join(categories)
  print(f'\n\t-- GSML for categories: [{category_display_str}]')

  result = calculate_recall_and_precision(gsml_filename, submitted_filename, token_lookup, categories)
  recall = format_result_value(result['recall']['value'])
  precision = format_result_value(result['precision']['value'])
  mean_overlap = format_result_value(result['overlap']['value'])
  print(f'\t\trecall => {recall}, precision => {precision}, overlap => {mean_overlap}')
  for k, v in result.items():
    print(f'\t\t\t{k}')
    for sub_k, sub_v in result.items():
      print(f'\t\t\t\t{sub_k} => {sub_v}')