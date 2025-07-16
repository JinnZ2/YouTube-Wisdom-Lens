from youtube_transcript_api import YouTubeTranscriptApi
from langdetect import detect
import nltk
import spacy
from cultural_lens import CulturalLens
from fact_verifier import verify_claim
from sensitivity_check import cultural_sensitivity_check

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")
lens = CulturalLens()

def get_transcript(video_id, lang='en'):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print("Transcript error:", e)
        return None

def analyze_transcript(transcript_text, chunk_size=3):
    sentences = nltk.sent_tokenize(transcript_text)
    chunks = [sentences[i:i + chunk_size] for i in range(0, len(sentences), chunk_size)]
    
    results = []

    for chunk in chunks:
        text = " ".join(chunk)
        lang = detect(text)
        cultural_result = lens.analyze(text)
        fact_result = verify_claim(text)
        sensitivity = cultural_sensitivity_check(text)

        results.append({
            "text": text,
            "lang": lang,
            "perspective": cultural_result.get("primary_perspective", "unknown"),
            "markers": cultural_result.get("cultural_markers", []),
            "warnings": cultural_result.get("perspective_warnings", []),
            "sensitivity": sensitivity,
            "fact_check": fact_result
        })

    return results
