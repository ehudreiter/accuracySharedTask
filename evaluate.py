import csv
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

# It is possible for a metric to present multiple annotations which map to one annotation in the GSML
#    or vice verse
# For example, "Miami Heat" could be a 2-token error "Miami Heat"
#    or two 1-token errors "Miami" (wring city) "Heat" (wrong name)
# We award correct recall when at least one submitted mistake matches a GSML mistake
# We aware correct precision when a submitted mistake matches at least one GSML mistake
# mistakes are said to match when their ranges of token ids overlap

def all_categories():
  return ['NAME', 'NUMBER', 'WORD', 'CONTEXT', 'NOT_CHECKABLE', 'OTHER']

def create_gsml_dict(filename, categories):
  gsml = {}
  matches = 0
  with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(reader, None)

    num_lines = 0

    for i, row in enumerate(reader):
      # Columns from gthe CSV
      text_id = row[0].replace('.txt','')
      sentence_id = int(row[1])
      annotation_id = int(row[2])
      start_idx = int(row[4])
      end_idx = int(row[5])
      category = row[8]

      if category not in categories:
        continue

      if text_id not in gsml: gsml[text_id] = {}
      if sentence_id not in gsml[text_id]: gsml[text_id][sentence_id] = {}
      gsml[text_id][sentence_id][start_idx] = {
        'set':            set(range(start_idx, end_idx+1)),
        'category':       category,
        'start_idx':      start_idx,
        'sentence_id':    sentence_id,
        'annotation_id':  annotation_id,
      }
      num_lines += 1
  return gsml, num_lines

def match_gsml(gsml, submitted_gsml):
  per_gsml_matches = {}
  for text_id, gsml_text_data in gsml.items():
    for sentence_id, gsml_sentence_data in gsml_text_data.items():
      for start_idx, gsml_error_data in gsml_sentence_data.items():
        matches = set([])
        if text_id in submitted_gsml and sentence_id in submitted_gsml[text_id]:
          for submitted_start_idx, submitted_sentence_data in submitted_gsml[text_id][sentence_id].items():
            if submitted_sentence_data['set'].intersection(gsml_error_data['set']):
              matches.add(submitted_start_idx)
        per_gsml_matches[f'{text_id}_{sentence_id}_{start_idx}'] = matches
  return per_gsml_matches

def calculate_recall_and_precision(gsml_filename, submitted_filename, categories):
  gsml, gsml_num_lines = create_gsml_dict(gsml_filename, categories)
  submitted_gsml, submitted_num_lines = create_gsml_dict(submitted_filename, categories)

  # Test on an example submission
  matches = match_gsml(gsml, submitted_gsml)

  # Recall
  correct_recall = len([k for k, v in matches.items() if len(v) > 0])
  incorrect_recall = len([k for k, v in matches.items() if len(v) == 0])
  assert (correct_recall + incorrect_recall) == gsml_num_lines
  if gsml_num_lines > 0:
    recall = correct_recall / gsml_num_lines
  else:
    recall = None

  # Precision
  correct_precision = sum([len(v) for k, v in matches.items()])
  if submitted_num_lines > 0:
    precision = correct_precision / submitted_num_lines
  else:
    precision = None

  return recall, precision

categories_list = [all_categories()] + [[x] for x in all_categories()]
for categories in categories_list:
  category_display_str = ', '.join(categories)
  print(f'\n-- GSML for categories: {category_display_str}')

  recall, precision = calculate_recall_and_precision('gsml.csv', 'submitted_gsml.csv', categories)
  print(f'GSML vs example: recall => {recall}, precision => {precision}')

  recall, precision = calculate_recall_and_precision('gsml.csv', 'gsml.csv', categories)  
  print(f'GSML vs self: recall => {recall}, precision => {precision}')