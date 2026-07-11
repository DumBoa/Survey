import json

def check_lengths():
    with open('alldata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # We will check common CharFields to see if they exceed their max_length
    max_lengths = {
        'survey.section': {'code': 10},
        'survey.survey': {'code': 20, 'slug': 255},
        'survey.question': {'component_type': 50, 'title': 500},
        'analytics.targetgroup': {'code': 50, 'name': 255},
        'survey.surveyassignment': {'form_code': 20, 'target_group_code': 50},
        'survey.surveyprogress': {'form_code': 20},
        'survey.surveyparticipant': {'target_group_code': 50},
    }
    
    for item in data:
        model = item['model']
        if model in max_lengths:
            for field, max_len in max_lengths[model].items():
                val = item['fields'].get(field)
                if val and isinstance(val, str) and len(val) > max_len:
                    print(f"Model: {model}, pk: {item['pk']}, Field: {field}, Length: {len(val)}, Value: {val}")

if __name__ == "__main__":
    check_lengths()
