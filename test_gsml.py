# Validate the GSML:
# - make sure that the tokens in the GSML match the tokens found at the respective positions in raw text
texts = {}
matches = 0
with open('gsml.csv', 'r') as fh:
  for i, line in enumerate(fh.readlines()):
    if i == 0: continue
    arr = line.split('","')
    text_id = arr[0].replace('"','')
    target = arr[3]

    # WebAnno IDs start at 1 not 0 like the python lists used to check here
    start = int(arr[6]) - 1
    end = int(arr[7])

    with open(f'/home/badger/Development/gsml/texts/{text_id}', 'r') as fh_t:
      if text_id not in texts:
        texts[text_id] = fh_t.read().split()
      found = ' '.join(texts[text_id][start:end])
      if found != target:
        raise Exception(f'No MATCH {text_id}, {i}, {start}, {start}, "{found}", "{target}"')
      else:
        matches += 1
print(f'{matches} lines matched, all token spans have been found in the source text files.')