import json

with open('Day19_GraphRAG_vs_FlatRAG_Production_Lab_Guide.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Patch Cell 8 (Near Dedup - Challenge A)
# Find cell 8
cell8_idx = -1
for i, c in enumerate(nb['cells']):
    if c['cell_type'] == 'code' and '1.5 — Loader + exact dedup + chunking' in c['source'][0]:
        cell8_idx = i
        break

if cell8_idx != -1:
    source = "".join(nb['cells'][cell8_idx]['source'])
    new_source = source.replace(
        """    before = len(df)
    df = df.drop_duplicates("dedup_key").drop(columns="dedup_key").reset_index(drop=True)
    print(f"Exact dedup: {before:,} -> {len(df):,}")""",
        """    # AI Coding Agent Challenge A — Near Dedup using Embedding + ANN FAISS
    before = len(df)
    
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        
        # We use a small, fast embedding model for dedup
        embedder_dedup = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        texts_to_embed = df["title"] + " " + df["text"].str[:200]
        embeddings = embedder_dedup.encode(texts_to_embed.tolist(), show_progress_bar=True, normalize_embeddings=True).astype('float32')
        
        d = embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        index.add(embeddings)
        
        # Search for nearest neighbors
        sims, nbrs = index.search(embeddings, 2)
        
        to_drop = set()
        threshold = 0.92  # High threshold for near-duplicate detection
        
        for i in range(len(df)):
            if i in to_drop:
                continue
            for j, sim in zip(nbrs[i], sims[i]):
                if j != i and j != -1 and sim > threshold:
                    # Mark the later one to drop
                    to_drop.add(max(i, int(j)))
                    
        df = df.drop(index=list(to_drop)).reset_index(drop=True)
        print(f"Near Dedup (Embedding+ANN): {before:,} -> {len(df):,} (Dropped {len(to_drop)} duplicates)")
    except Exception as e:
        print(f"Near dedup failed ({e}), falling back to exact dedup")
        df = df.drop_duplicates("dedup_key").reset_index(drop=True)
        print(f"Exact dedup: {before:,} -> {len(df):,}")
    
    df = df.drop(columns="dedup_key", errors="ignore")"""
    )
    # Split back into lines
    lines = [line + '\n' for line in new_source.split('\n')]
    if lines:
        lines[-1] = lines[-1][:-1] # remove last newline
    nb['cells'][cell8_idx]['source'] = lines


# Patch Cell 16 (Entity Resolution Lexical Guard - Challenge B)
cell16_idx = -1
for i, c in enumerate(nb['cells']):
    if c['cell_type'] == 'code' and '2.2 — Entity resolution' in c['source'][0]:
        cell16_idx = i
        break

if cell16_idx != -1:
    source = "".join(nb['cells'][cell16_idx]['source'])
    new_source = source.replace(
        """def merge_guard(a, b):
    na, nb = strip_suffix(a), strip_suffix(b)
    if na == nb:
        return True
    return SequenceMatcher(None, na, nb).ratio() >= 0.72""",
        """def merge_guard(a, b, typ="Company"):
    from difflib import SequenceMatcher
    na, nb = strip_suffix(a), strip_suffix(b)
    if na == nb:
        return True
        
    # AI Coding Agent Challenge B: Cải tiến Lexical Guard
    
    if typ == "Company":
        # Product containing company name (e.g. Apple vs Apple Music)
        # Avoid merging a short company name with a much longer name that contains it
        words_a = set(na.split())
        words_b = set(nb.split())
        if (words_a.issubset(words_b) and len(words_b) > len(words_a)) or \\
           (words_b.issubset(words_a) and len(words_a) > len(words_b)):
            return False
            
    if typ == "Person":
        # People with same last name but different first name
        parts_a = na.split()
        parts_b = nb.split()
        if len(parts_a) > 1 and len(parts_b) > 1:
            if parts_a[-1] == parts_b[-1] and parts_a[0] != parts_b[0]:
                return False
                
    # Strict fallback using SequenceMatcher
    return SequenceMatcher(None, na, nb).ratio() >= 0.80"""
    )
    
    # We also need to update the call site in build_resolution_map from merge_guard(names[i], names[j]) to merge_guard(names[i], names[j], typ)
    new_source = new_source.replace("ok = merge_guard(names[i], names[j])", "ok = merge_guard(names[i], names[j], typ)")
    
    lines = [line + '\n' for line in new_source.split('\n')]
    if lines:
        lines[-1] = lines[-1][:-1]
    nb['cells'][cell16_idx]['source'] = lines

with open('Day19_GraphRAG_vs_FlatRAG_Production_Lab_Guide.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
