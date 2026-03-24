"""Main NLP pipeline for YouTube transcript analysis.

Orchestrates transcript retrieval, cultural analysis, fact verification,
and sensitivity checking across chunked transcript text.
"""

import logging

import nltk
from langdetect import detect, LangDetectException
from youtube_transcript_api import YouTubeTranscriptApi

from api_keys_config import DEFAULT_CHUNK_SIZE
from cultural_lens import CulturalLens
from fact_verifier import verify_claim
from sensitivity_check import cultural_sensitivity_check

logger = logging.getLogger(__name__)

# Download punkt tokenizer data (idempotent)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


def get_transcript(video_id, lang="en"):
    """Retrieve and concatenate a YouTube video transcript.

    Args:
        video_id: YouTube video ID string.
        lang: Language code for transcript (default: "en").

    Returns:
        str: Full transcript text, or None if retrieval fails.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=[lang]
        )
        return " ".join(entry["text"] for entry in transcript)
    except Exception as e:
        logger.error("Transcript retrieval failed for %s: %s", video_id, e)
        return None


def analyze_transcript(transcript_text, chunk_size=DEFAULT_CHUNK_SIZE):
    """Run full analysis pipeline on transcript text.

    Args:
        transcript_text: Raw transcript text to analyze.
        chunk_size: Number of sentences per analysis chunk.

    Returns:
        list[dict]: Analysis results per chunk, each containing:
            - text (str): chunk text
            - lang (str): detected language
            - perspective (str): cultural perspective label
            - markers (list[str]): cultural keywords found
            - warnings (list[str]): perspective bias warnings
            - sensitivity (list[str]): protected term warnings
            - fact_check (dict): fact verification results

    Pipeline per chunk:
        1. Sentence tokenization via NLTK punkt
        2. Language detection via langdetect
        3. Cultural perspective analysis via CulturalLens
        4. Semantic fact verification via cosine similarity
        5. Protected term sensitivity scan
    """
    lens = CulturalLens()
    sentences = nltk.sent_tokenize(transcript_text)
    chunks = [
        sentences[i : i + chunk_size]
        for i in range(0, len(sentences), chunk_size)
    ]

    results = []
    for chunk in chunks:
        text = " ".join(chunk)

        try:
            lang = detect(text)
        except LangDetectException:
            lang = "unknown"

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
            "fact_check": fact_result,
        })

    return results
