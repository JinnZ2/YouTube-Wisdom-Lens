#  YouTube Wisdom Lens Prototype

**Version 0.1 – Cultural Context & Bias Detection**

A culturally-aware AI video analyzer that identifies language patterns, cultural perspective markers, semantic bias, and ethical red flags in YouTube video metadata and titles.  
Designed to support deeper understanding across worldviews, prevent unconscious bias, and surface pluralistic knowledge representations.

---

##  Core Features

- **Language Detection** using multilingual models
- **Cultural Perspective Analysis** with predefined cultural marker databases
- **Fact Similarity Scoring** using sentence embeddings across multiple knowledge domains
- **Bias & Sensitivity Alerts** including Western-centrism, sacred term misuse, and indigenous reference flags
- **Real-time YouTube Metadata Pull** using YouTube Data API v3
- **Disaster Footage Coupling Check** (`disaster_footage_check.py`, standard library only): before sharing a disaster clip, answer a short set of questions about whether the scene's layers react to each other (birds and animals first, trees from the base, one light direction). Returns `COUPLING_BROKEN`, `COUPLING_CONSISTENT` or `NOT_EVALUABLE`, never REAL or FAKE, and always prints the provenance steps. Title and description are scanned for "share before they delete it" pressure. Accuracy unmeasured.

---

## GitHub Topics (for desktop users)

If viewing on desktop, please help tag this repo using:

ai
nlp
cultural-intelligence
youtube-analysis
bias-detection
transcript-analysis
open-source
indigenous-knowledge
ethics


# Dependencies

Install all required packages with:


bash
pip install -q google-api-python-client transformers langdetect sentence-transformers pandas




How It Works


	1.	Fetches YouTube video metadata via video_id
 
	2.	Runs cultural context and perspective detection on the title
 
	3.	Checks semantic similarity against wisdom-domain embeddings (e.g., Taoism, Ubuntu, Western Science)
 
	4.	Flags potential cultural biases or ethical risks
	
        5.	Outputs structured results for human or downstream system review



Example:

video_id = "dQw4w9WgXcQ"  # Replace with your video ID


video_data = get_video_context(video_id)
title = video_data['items'][0]['snippet']['title']


lens = CulturalLens()
cultural_analysis = lens.analyze(title)
fact_check = verify_claim(title)
sensitivity = cultural_sensitivity_check(title)


print(pd.Series(cultural_analysis))
print(pd.Series(fact_check))
print("Sensitivity Check:", sensitivity)



Cultural Model Structure


Example cultural marker definitions:


'zh': {
  'keywords': ['道', '仁', '阴阳'],
  'perspective': 'East Asian'
}


These can be expanded to include Indigenous, Latin American, Islamic, or other traditions as needed.



Ethical Safeguards


The system includes a cultural_sensitivity_check() that detects usage of sacred or protected terms from spiritual and indigenous contexts, issuing soft alerts to prevent misuse or extraction without context.



Examples:

	•	“elder wisdom” → Indigenous term alert
 
	•	“initiation ritual” → Spiritual context alert
 


Authors


Created by JinnZ2 with support from ChatGPT

Built to inspire pluralistic, culturally respectful AI systems.




 License
 

Dedicated to the public domain under CC0-1.0 – free to use, modify, and share; attribution appreciated, not required.

Relicensed from MIT to CC0-1.0 on 2026-09-24; earlier copies obtained under MIT remain under MIT.
Licensed under CC0 1.0 Universal – Free to use, modify, and share. No attribution required.


# YouTube-Wisdom-Lens


Built to inspire pluralistic, culturally respectful AI systems.
