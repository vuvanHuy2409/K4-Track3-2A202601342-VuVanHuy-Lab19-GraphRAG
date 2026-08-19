import json

with open('Day19_GraphRAG_vs_FlatRAG_Production_Lab_Guide.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, c in enumerate(nb['cells']):
    ctype = c['cell_type']
    src = ''.join(c['source']).strip()
    if ctype == 'markdown' and src.startswith('#'):
        print(f"[{i}] {src.split(chr(10))[0]}")
    elif 'TODO' in src or 'YOUR CODE HERE' in src:
        print(f"[{i}] CODE TASK: {src[:50]}...")
