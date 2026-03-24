"""Semantic similarity fact verification across knowledge domains.

Compares input claims against reference embeddings from multiple
knowledge traditions using cosine similarity.
"""

import logging

from sentence_transformers import SentenceTransformer, util

from api_keys_config import CONSENSUS_THRESHOLD

logger = logging.getLogger(__name__)

# Model name for sentence embeddings
_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

# Reference phrases for each knowledge domain
KNOWLEDGE_REFERENCES = {
    "western_science": "Peer-reviewed research findings",
    "taoism": "Nature harmony balance wu wei",
    "ubuntu": "Community shared humanity interconnectedness",
}

# Lazy-loaded globals
_model = None
_knowledge_embeddings = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        logger.info("Loading sentence transformer model: %s", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def _get_knowledge_embeddings():
    """Lazy-load and cache knowledge domain embeddings."""
    global _knowledge_embeddings
    if _knowledge_embeddings is None:
        model = _get_model()
        _knowledge_embeddings = {
            domain: model.encode(reference)
            for domain, reference in KNOWLEDGE_REFERENCES.items()
        }
    return _knowledge_embeddings


def verify_claim(text):
    """Score a claim's similarity to multiple knowledge domains.

    Args:
        text: The claim text to verify.

    Returns:
        dict with keys:
            - claim (str): original input text
            - source_agreements (dict[str, float]): cosine similarity
              per knowledge domain
            - consensus_score (float): mean similarity across all domains
            - verdict (str): "Multiple Confirmations" if consensus_score
              >= CONSENSUS_THRESHOLD, else "Contested Claim"

    Equations:
        similarity(claim, domain) = cos_sim(embed(claim), embed(domain))
            where cos_sim(a, b) = (a . b) / (||a|| * ||b||)

        consensus = (1/N) * sum(similarity_i for i in domains)
            where N = number of knowledge domains

        verdict = "Multiple Confirmations" if consensus >= threshold
                  else "Contested Claim"
    """
    model = _get_model()
    embeddings = _get_knowledge_embeddings()

    text_embedding = model.encode(text)
    similarities = {}

    for source, emb in embeddings.items():
        similarities[source] = util.cos_sim(text_embedding, emb).item()

    consensus = sum(similarities.values()) / len(similarities)

    return {
        "claim": text,
        "source_agreements": similarities,
        "consensus_score": round(consensus, 4),
        "verdict": (
            "Multiple Confirmations"
            if consensus >= CONSENSUS_THRESHOLD
            else "Contested Claim"
        ),
    }
