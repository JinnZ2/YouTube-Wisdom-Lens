from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

knowledge_embeddings = {
    'western_science': model.encode("Peer-reviewed research findings"),
    'taoism': model.encode("Nature harmony balance wu wei"),
    'ubuntu': model.encode("Community shared humanity interconnectedness")
}

def verify_claim(text):
    text_embedding = model.encode(text)
    similarities = {}
    
    for source, emb in knowledge_embeddings.items():
        similarities[source] = util.cos_sim(text_embedding, emb).item()
    
    consensus = sum(similarities.values()) / len(similarities)
    
    return {
        'claim': text,
        'source_agreements': similarities,
        'consensus_score': consensus,
        'verdict': 'Multiple Confirmations' if consensus > 0.7 else 'Contested Claim'
    }
