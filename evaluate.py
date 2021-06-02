import csv
import json
import pprint
import sys
import yaml
from copy import deepcopy
import argparse

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Create the pretty printer
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

''' Helper that checks that either DOC or SENT based tokenization is used throughout'''
def consistent_tokenization(tokenization_mode, current_line_mode):
  if tokenization_mode not in {None, current_line_mode}:
    raise Exception('You must consistently use either document-based, sentence-based or both for the tokenization method.')
  return current_line_mode

"""
  Creates and returns a dictionary representation of the mistake list (GSML or Submission)
  The dictiory is structured as:
  - TEXT_ID, TEXT_DATA
    - START_IDX, MISTAKE_DATA
  The function returns a tuple where the first element is the dict, and the second is num_mistakes
"""
def create_mistake_dict(filename, categories, token_lookup):
  mistake_dict = {}
  tokens_used = {}
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
      elif doc_given:
        tokenization_mode = consistent_tokenization(tokenization_mode, 'DOC')
        sentence_id = token_lookup['doc_to_sent'][text_id][doc_start_idx]['sentence_id']
        sent_start_idx = token_lookup['doc_to_sent'][text_id][doc_start_idx]['token_id']
        sent_end_idx = token_lookup['doc_to_sent'][text_id][doc_end_idx]['token_id']
      else:
        raise Exception(f'You must provide either document or sentence based token ids on {filename} row {i}')

      if category not in categories:
        continue

      # For detecting overlapping spans
      if text_id not in tokens_used:
        tokens_used[text_id] = set([])

      for x in range(doc_start_idx, doc_end_idx+1):
        if x in tokens_used[text_id]:
          raise Exception(f'Token {x} already used, duplicate on {text_id}:{i}')
        tokens_used[text_id].add(x)

      # The mistake data structure
      if text_id not in mistake_dict:
        mistake_dict[text_id] = {}

      mistake_dict[text_id][doc_start_idx] = {
        'set':            set(range(doc_start_idx, doc_end_idx+1)),
        'category':       category,
        'sent_start_idx': sent_start_idx,
        'sent_end_idx':   sent_start_idx,
        'doc_start_idx':  doc_start_idx,
        'doc_end_idx':    doc_end_idx,
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
  per_category_matches = {k:{} for k in all_categories()}

  # Copy this because the algorithm consumes elements
  # - this can break the token level calcs if done in wrong order
  # - so copy for least surprise
  copy_submitted = deepcopy(submitted)

  for text_id, gsml_text_data in gsml.items():
    # mistake level - match each submission to at most one gold mistake
    used_submissions = set([])
    for doc_start_idx, gsml_error_data in gsml_text_data.items():
      doc_end_idx = gsml_error_data['doc_end_idx']
      category = gsml_error_data['category']
      assert category in per_category_matches

      pop_key = None
      if text_id in copy_submitted:
        for submitted_doc_start_idx, submitted_error_data in copy_submitted[text_id].items():
          # TODO - this is pretty brute force, it loops needlessly, but it works so ...

          # Check if the submitted error intersects the GSML error 
          if submitted_error_data['set'].intersection(gsml_error_data['set']):
            # Only use a submission once, it cannot recall multiple gold mistakes
            pop_key = submitted_doc_start_idx
            break

      match = pop_key != None
      if match:
        # Remove the submission so it will not be used again
        copy_submitted[text_id].pop(pop_key, None)

      per_category_matches[category][f'{text_id}_{doc_start_idx}'] = match
  return per_category_matches



'''Returns the correct and incorrect recall totals'''
def get_recall(matches):
  correct = {k:0 for k in all_categories()}
  incorrect = {k:0 for k in all_categories()}
  for category, h in matches.items():
    for mistake_id_str, v in h.items():
      if v:
        correct[category] += 1
      else:
        incorrect[category] += 1
  return correct, incorrect

def get_document_tokens(token_lookup):
  document_tokens = {}
  for text_id, token_data in token_lookup['doc_to_sent'].items():
    document_tokens[text_id] = {}
    for doc_token_id in token_data.keys():
      document_tokens[text_id][doc_token_id] = {
        'gsml': False,
        'submitted': False
      }
  return document_tokens

def match_tokens(data, document_tokens, mode):
  for text_id, text_data in data.items():
    for start_idx, error_data in text_data.items():
      for x in range(error_data['doc_start_idx'], error_data['doc_end_idx']+1):
        document_tokens[text_id][x][mode] = True

def get_token_level_result(gsml, submitted, token_lookup):
  document_tokens = get_document_tokens(token_lookup)
  match_tokens(gsml, document_tokens, 'gsml')
  match_tokens(submitted, document_tokens, 'submitted')

  recall = 0
  recall_denominator = 0
  precision_denominator = 0

  for text_id, data in document_tokens.items():
    for token_id, v in data.items():
      if v['gsml'] and v['submitted']:
        recall += 1
      if v['gsml']:
        recall_denominator += 1
      if v['submitted']:
        precision_denominator += 1

  return {
    'recall': recall,
    'recall_denominator': recall_denominator,
    'precision_denominator': precision_denominator,
  }

def safe_divide(x, y):
  if y > 0:
    return x / y
  return None

"""
  Returns a dict containing sub-dicts of recall, precision and overlaps between a GSML and a submission
  Takes as input dicts created with match_mistake_dicts(), plus a list of categories
  Only the categories given will be checked.
"""
def calculate_recall_and_precision(gsml_filename, submitted_filename, token_lookup, categories=[]):
  gsml, gsml_num_lines = create_mistake_dict(gsml_filename, categories, token_lookup)
  submitted, submitted_num_lines = create_mistake_dict(submitted_filename, categories, token_lookup)

  # Mistake level
  per_category_matches = match_mistake_dicts(gsml, submitted)

  correct_recall_h, incorrect_recall_h = get_recall(per_category_matches)
  correct_recall = sum(correct_recall_h.values())
  incorrect_recall = sum(incorrect_recall_h.values())

  assert (correct_recall + incorrect_recall) == gsml_num_lines

  recall = safe_divide(correct_recall, gsml_num_lines)
  precision = safe_divide(correct_recall, submitted_num_lines)

  # Token level
  token_result = get_token_level_result(gsml, submitted, token_lookup)
  token_recall = safe_divide(token_result['recall'], token_result['recall_denominator'])
  token_precision = safe_divide(token_result['recall'], token_result['precision_denominator'])

  # Values to display
  return {
    'recall': {
      'value': recall,
      'correct': correct_recall,
      'of_total': gsml_num_lines
    },
    'precision': {
      'value': precision,
      'correct': correct_recall,
      'of_total': submitted_num_lines
    },
    'token_recall': {
      'value': token_recall,
      'correct': token_result['recall'],
      'of_total': token_result['recall_denominator']
    },
    'token_precision': {
      'value': token_precision,
      'correct': token_result['recall'],
      'of_total': token_result['precision_denominator']
    },
    'correct_recall_debug': correct_recall_h,
    'incorrect_recall_debug': incorrect_recall_h
  }

def format_result_value(value, dcp=3):
  if value:
    return round(value, dcp)
  return None








# CLI args
parser.add_argument('--gsml', type=str,
                    help='The GSML file path (CSV)')

parser.add_argument('--submitted', type=str, nargs='?',
                    help='The submitted file path (CSV)')

parser.add_argument('--token_lookup', type=str,
                    help='The tokenization file (YAML)')

args = parser.parse_args()
gsml_filename = args.gsml
submitted_filename = args.submitted
token_lookup_filename = args.token_lookup

with open(token_lookup_filename, 'r') as fh:
  token_lookup = yaml.full_load(fh)

print('\n\n')
print('-' * 80)
print('GSML: EVALUATE')
print(f'comparing GSML => "{gsml_filename}" to submission => "{submitted_filename}"')

# Check all catogories combined, as well as each category individually
categories_list = [all_categories()] + [[x] for x in all_categories()]

for categories in categories_list:
  category_display_str = ', '.join(categories)
  print(f'\n\t-- GSML for categories: [{category_display_str}]')

  result = calculate_recall_and_precision(gsml_filename, submitted_filename, token_lookup, categories)
  recall = format_result_value(result['recall']['value'])
  precision = format_result_value(result['precision']['value'])
  token_recall = format_result_value(result['token_recall']['value'])
  token_precision = format_result_value(result['token_precision']['value'])
  print(f'\tsummary: recall => {recall}, precision => {precision}, token_recall => {token_recall}, token_precision => {token_precision}')
  print('\tbreakdown:')
  for k, v in result.items():
    print(f'\t\t{k}')
    for sub_k, sub_v in v.items():
      print(f'\t\t\t{sub_k} => {sub_v}')