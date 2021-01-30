import csv

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
    text_id = row[0].replace('"','')
    target = row[3]

    # WebAnno IDs start at 1 not 0 like the python lists used to check here
    start = int(row[6]) - 1
    end = int(row[7])

    with open(f'/home/badger/Development/gsml/texts/{text_id}', 'r') as fh_t:
      if text_id not in texts:
        texts[text_id] = fh_t.read().split()
      found = ' '.join(texts[text_id][start:end])
      if found != target:
        raise Exception(f'No MATCH {text_id}, {i}, {start}, {start}, "{found}", "{target}"')
      else:
        matches += 1
        
print(f'{matches} lines matched, all token spans have been found in the source text files.')