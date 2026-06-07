import json
with open('documents/Asthma.json', encoding='utf-8') as f:
    d = json.load(f)
print(d['content'][-300:])