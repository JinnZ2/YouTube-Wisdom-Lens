Respect Statement

This tool is designed to listen, not overwrite.

It does not aim to reduce cultures to keywords, but to raise awareness about hidden structures of meaning, encourage ethical engagement, and support mutual respect across paradigms of knowledge.

</details>

---

## ✅ 2. `cultural_lens.py`

```python
from langdetect import detect
from transformers import pipeline

class CulturalLens:
    def __init__(self):
        self.classifier = pipeline("text-classification", 
                                   model="papluca/xlm-roberta-base-language-detection")
        self.cultural_db = {
            'en': {'keywords': ['democracy', 'individualism', 'scientific method'],
                   'perspective': 'Western'},
            'zh': {'keywords': ['道', '仁', '阴阳'],
                   'perspective': 'East Asian'},
            'sw': {'keywords': ['ujamaa', 'harambee'],
                   'perspective': 'East African'}
        }

    def analyze(self, text):
        lang = detect(text)
        results = {
            'detected_language': lang,
            'cultural_markers': [],
            'perspective_warnings': []
        }

        if lang in self.cultural_db:
            culture = self.cultural_db[lang]
            results['primary_perspective'] = culture['perspective']
            results['cultural_markers'] = [w for w in culture['keywords'] if w in text]
        
        if lang == 'en' and len(results['cultural_markers']) > 3:
            results['perspective_warnings'].append("Potential Western-centric bias")

        return results

