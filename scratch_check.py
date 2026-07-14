import json
lines = open('sipas_backup.sql', encoding='utf-8').read().split('\n')
r21 = [l for l in lines if '\t21\t' in l and '{' in l]

empty_responses = sum(1 for l in r21 if '{}' in l)
print('Empty (Drafts):', empty_responses)

# Get some responses that are NOT empty and don't have new keys
other_responses = [l for l in r21 if '{}' not in l and '"6896"' not in l and '"6947"' not in l]
print('Other non-empty responses without 6896/6947:', len(other_responses))
if other_responses:
    print('Sample keys from one of them:', list(json.loads(other_responses[0].split('\t')[8]).keys()))
