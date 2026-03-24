"""Cultural sensitivity detection for protected terms.

Scans text for terms related to indigenous and spiritual traditions
that may require special contextual handling.
"""

import re

# Protected terms by category
PROTECTED_TERMS = {
    "indigenous": ["sacred", "ceremony", "elder wisdom"],
    "spiritual": ["ritual", "initiation", "mystery"],
}


def _word_in_text(word, text):
    """Check if word appears as a whole word (case-insensitive)."""
    pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
    return pattern.search(text) is not None


def cultural_sensitivity_check(text):
    """Detect protected cultural and spiritual terms in text.

    Args:
        text: Input text to scan.

    Returns:
        list[str]: Warning messages for each category with matches.
            Returns empty list if no protected terms are found.

    Algorithm:
        For each category in PROTECTED_TERMS:
            Match terms using word-boundary regex (case-insensitive)
            If any terms found, append warning with category and terms
    """
    warnings = []
    for category, terms in PROTECTED_TERMS.items():
        found = [t for t in terms if _word_in_text(t, text)]
        if found:
            warnings.append(
                f"Contains protected {category} terms: {', '.join(found)}"
            )
    return warnings
