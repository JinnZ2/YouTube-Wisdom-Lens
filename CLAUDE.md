# YouTube Wisdom Lens

Culturally-aware AI video analyzer that detects language patterns, cultural perspective markers, semantic bias, and ethical red flags in YouTube video transcripts and metadata.

## Project Structure

```
api_keys_config.py       # YouTube API config, shared constants, env-based key management
cultural_lens.py         # CulturalLens class: language detection + cultural marker analysis
fact_verifier.py         # Semantic similarity fact-checking across knowledge domains
sensitivity_check.py     # Protected term detection for indigenous/spiritual content
transcript_nlp_pipeline.py  # Main orchestration pipeline: transcript -> chunked analysis
YouTube-analysis.ipynb   # Interactive notebook for exploration and demos
```

## Architecture

### Data Flow

```
YouTube Video ID
    -> get_transcript()              [transcript_nlp_pipeline.py]
    -> analyze_transcript()          [transcript_nlp_pipeline.py]
        -> nltk.sent_tokenize()      (sentence splitting)
        -> for each chunk:
            -> langdetect.detect()   (language identification)
            -> CulturalLens.analyze() [cultural_lens.py]
            -> verify_claim()         [fact_verifier.py]
            -> cultural_sensitivity_check() [sensitivity_check.py]
    -> list[dict] results
```

### Module Dependencies

```
api_keys_config.py          (no internal deps — constants & YouTube client)
    ├── cultural_lens.py     (imports WESTERN_BIAS_MARKER_THRESHOLD)
    ├── fact_verifier.py     (imports CONSENSUS_THRESHOLD)
    └── transcript_nlp_pipeline.py (imports DEFAULT_CHUNK_SIZE)
        ├── cultural_lens.py
        ├── fact_verifier.py
        └── sensitivity_check.py  (standalone, no internal deps)
```

## Key Algorithms & Equations

### Consensus Scoring (fact_verifier.py)

```
similarity(claim, domain) = cos_sim(embed(claim), embed(domain_ref))
    where cos_sim(a, b) = (a · b) / (||a|| × ||b||)

consensus = (1/N) × Σ similarity_i    for i in {western_science, taoism, ubuntu}

verdict = "Multiple Confirmations"  if consensus >= CONSENSUS_THRESHOLD (0.7)
          "Contested Claim"         otherwise
```

- Model: `sentence-transformers/all-mpnet-base-v2`
- Embedding dimension: 768
- All domains weighted equally (arithmetic mean)

### Cultural Bias Detection (cultural_lens.py)

```
markers = [keyword for keyword in cultural_db[lang] if keyword ∈ text]
bias_warning triggered when: lang == "en" AND len(markers) >= WESTERN_BIAS_MARKER_THRESHOLD (2)
```

- Matching: whole-word, case-insensitive regex
- Languages supported: en (Western), zh (East Asian), sw (East African)

### Sensitivity Detection (sensitivity_check.py)

```
For each category in {indigenous, spiritual}:
    found = [term for term in protected_terms[category] if term matches word-boundary in text]
    if found: emit warning
```

- Matching: `\b`-bounded regex, case-insensitive

## Configuration

All tunable constants live in `api_keys_config.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `CONSENSUS_THRESHOLD` | 0.7 | Min cosine similarity mean for "confirmed" verdict |
| `DEFAULT_CHUNK_SIZE` | 3 | Sentences per analysis chunk |
| `WESTERN_BIAS_MARKER_THRESHOLD` | 2 | Min markers to flag Western-centrism |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `YOUTUBE_API_KEY` | Yes | YouTube Data API v3 key |

## Naming Conventions

- **Files**: `snake_case.py` (PEP 8)
- **Functions**: `snake_case` (PEP 8)
- **Classes**: `PascalCase` (PEP 8)
- **Constants**: `UPPER_SNAKE_CASE` (PEP 8)
- **Private helpers**: `_leading_underscore`

## Development

```bash
pip install -r requirements.txt
python -m nltk.downloader punkt punkt_tab
export YOUTUBE_API_KEY="your-key-here"
```

## Code Quality Notes

- Models are lazy-loaded (not at import time) in `fact_verifier.py`
- `sensitivity_check.py` is standalone with no external model dependencies
- All text matching uses word-boundary or whole-word regex (no naive substring)
- Return types are consistent (always list, never mixed list/string)
- Logging via `logging` module (no bare `print` statements)
