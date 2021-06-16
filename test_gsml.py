import csv
import json
import glob

import pprint
pp = pprint.PrettyPrinter(indent=4)

# Check the details in games.csv match those in the JSON
with open('games.csv', newline='') as csvfile, open('shared_task.jsonl') as fh:
  json_lines = []

  for line in fh.readlines():
    json_lines.append(json.loads(line))

  reader = csv.reader(csvfile, delimiter=',', quotechar='"')
  next(reader, None)

  # Iterate the CSV rows
  for i, row in enumerate(reader):
    text_id = row[0]
    print(text_id)
    home_name = row[1]
    vis_name = row[2]
    generated_text = row[4].strip()
    the_date = row[6]
    
    # Check vs JSON data
    json_line = json_lines[i]

    if text_id != json_line['shared_task_text_id']:
      raise Exception('TEXT_IDs do not match')

    if home_name != json_line['home_name']:
      raise Exception('Home team names do not match')

    if vis_name != json_line['vis_name']:
      raise Exception('Visiting team names do not match')

    if the_date != json_line['day']:
      raise Exception('The dates do not match')

    # Check that the GENERATED_TEXT column matches the files in /texts
    with open(f'texts/{text_id}.txt', 'r') as fh_t:
      text_from_file = fh_t.read().strip()
      if text_from_file != generated_text:
        print(text_from_file)
        print(generated_text)
        raise Exception('The CSV and files texts do not match')


# Validate the GSML:
# - make sure that the tokens in the GSML match the tokens found at the respective positions in raw text
texts = {}
matches = 0
with open('gsml.csv', newline='') as csvfile:
  # Setup the CSV reader and skip the headers
  reader = csv.reader(csvfile, delimiter=',', quotechar='"')
  next(reader, None)

  # Iterate the CSV rows
  for i, row in enumerate(reader):
    text_id = row[0]
    target = row[3]

    # WebAnno IDs start at 1 not 0 like the python lists used to check here
    start = int(row[6]) - 1
    end = int(row[7])

    with open(f'texts/{text_id}', 'r') as fh_t:
      if text_id not in texts:
        texts[text_id] = fh_t.read().split()
      found = ' '.join(texts[text_id][start:end])
      if found != target:
        ex_str = f'No MATCH {text_id}, {i}, {start}, {end}, "{found}", "{target}"'
        raise Exception(ex_str)
      else:
        print(f'matched ({text_id}): {found} == {target}')
        matches += 1
        
print(f'{matches} lines matched, all token spans have been found in the source text files.')

def sentence_to_tokens(sentence):
  tokens = [t for t in sentence.strip().split(' ')]
  return tokens + ['.']

# Check that the sentencization works, and that only single period characters are sentence delimiting
# - Compares the texts in games.csv with the WebAnno export (all tokens, not just errors)
token_matches = 0
with open('games.csv', newline='') as csvfile:
  json_lines = []

  reader = csv.reader(csvfile, delimiter=',', quotechar='"')
  next(reader, None)

  for i, row in enumerate(reader):
    text_id = row[0][:4]
    # These are excluded for now because they include " characters as tokens which is breaking the CSV reader
    
    # Load the text from the file
    with open(f'texts/{text_id}.txt') as text_fh:
      text = text_fh.read().strip().replace('\n', '') + ' END'
      sentences = [sentence_to_tokens(s) for s in text.split('.')]

      sentence_lookup = {}

      for sentence_id, sentence in enumerate(sentences):
        sentence_lookup[sentence_id+1] = {i+1:t for i,t in enumerate(sentence)}
        period_chars = [(i,t) for i, t in enumerate(sentence) if t == '.']
        for c in period_chars:
          # Check that period characters are only ever the last element of a sentence
          if not (c[1] == '.' and (c[0]+1) == len(sentence)):
            raise Exception(f'Non-ending period char {text_id}, {c[0]} for sentence {sentence_id}')

        # Check the last element for each sentence is a period character
        if period_chars[-1][1] != '.':
          raise Exception(f'Ending char not period for {text_id}, {c[1]} for sentence {sentence_id}')

      # Now check if the sentences by the period split, are the same as the sentences in WebAnno
      # - Note that WebAnno indexes from 1
      glob_text = f'curation/{text_id}*/*.tsv'
      print(glob_text)
      # pp.pprint(sentence_lookup)
      for webanno_filename in sorted(glob.glob(glob_text)):
        print(webanno_filename)
        with open (webanno_filename,'r') as webanno_fh:
          webanno_reader = csv.reader(webanno_fh, delimiter='\t', quotechar=None)
          next(webanno_fh) # skip first row
          for webanno_row in webanno_reader:
            if len(webanno_row) > 0:
              if webanno_row[0][0] != '#':
                ids = [int(x) for x in webanno_row[0].split('-')]
                sentence_id, token_id = ids[0], ids[1]
                # We used the special token 000 (which does not appear in the corpus) to
                #   replace apostrophes for loading into WebAnno, as it was splitting them
                #   into sep tokens.  These should not be in the texts folder, but will be in WebAnno data:
                replacements = {
                  '000':  "'",
                  'NULL': 'N/A',
                  'COLON': ':',
                }

                webanno_token_text = webanno_row[2]

                for rep_from, rep_to in replacements.items():
                  if rep_from in sentence_lookup[sentence_id][token_id]:
                    ext_str =f'{rep_from} character found {sentence_lookup[sentence_id][token_id]}'
                    print(ext_str)
                    raise Exception(ext_str)

                  webanno_token_text = webanno_token_text.replace(rep_from, rep_to)

                sentence_token_text = sentence_lookup[sentence_id][token_id]
                if webanno_token_text != sentence_token_text:
                  print(webanno_row)
                  raise Exception(f'Invalid token for {text_id} for sentence {sentence_id}, got {sentence_token_text}, expected {webanno_token_text}')
                else:
                  token_matches += 1

print(f'There were {token_matches} token matches between period splitting and WebAnno.')