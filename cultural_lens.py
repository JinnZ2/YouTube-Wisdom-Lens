"""Cultural perspective detection and analysis.

Detects language and identifies cultural markers and perspective bias
in text using keyword matching and language detection.
"""

import logging
import re

from langdetect import detect, LangDetectException

from api_keys_config import WESTERN_BIAS_MARKER_THRESHOLD

logger = logging.getLogger(__name__)

# Cultural marker database: language code -> keywords + perspective label
CULTURAL_DB = {
    "en": {
        "keywords": ["democracy", "individualism", "scientific method"],
        "perspective": "Western",
    },
    "zh": {
        "keywords": ["道", "仁", "阴阳"],
        "perspective": "East Asian",
    },
    "sw": {
        "keywords": ["ujamaa", "harambee"],
        "perspective": "East African",
    },
}


def _find_whole_word(word, text):
    """Check if word appears as a whole word in text (case-insensitive)."""
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    return pattern.search(text) is not None


class CulturalLens:
    """Analyzes text for cultural perspective markers and potential bias.

    Attributes:
        cultural_db: Mapping of language codes to keyword/perspective data.
    """

    def __init__(self, cultural_db=None):
        self.cultural_db = cultural_db or CULTURAL_DB

    def analyze(self, text):
        """Analyze text for cultural markers and perspective bias.

        Args:
            text: Input text string to analyze.

        Returns:
            dict with keys:
                - detected_language (str): ISO 639-1 language code
                - cultural_markers (list[str]): matched cultural keywords
                - perspective_warnings (list[str]): bias warnings
                - primary_perspective (str): identified cultural perspective

        Algorithm:
            1. Detect language via langdetect
            2. Match cultural keywords using whole-word case-insensitive search
            3. Flag Western-centrism if marker count >= WESTERN_BIAS_MARKER_THRESHOLD
        """
        results = {
            "detected_language": None,
            "cultural_markers": [],
            "perspective_warnings": [],
        }

        try:
            lang = detect(text)
        except LangDetectException:
            logger.warning("Language detection failed for text: %.80s...", text)
            results["detected_language"] = "unknown"
            return results

        results["detected_language"] = lang

        if lang in self.cultural_db:
            culture = self.cultural_db[lang]
            results["primary_perspective"] = culture["perspective"]
            results["cultural_markers"] = [
                w for w in culture["keywords"] if _find_whole_word(w, text)
            ]

        marker_count = len(results["cultural_markers"])
        if lang == "en" and marker_count >= WESTERN_BIAS_MARKER_THRESHOLD:
            results["perspective_warnings"].append(
                "Potential Western-centric bias"
            )

        return results
