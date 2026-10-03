from typing import Any
from ..nlp.pipeline import similarity_search


_policy_chunks: list[dict[str, Any]] = []


def upload_policy(policy_id: str, title: str, text: str) -> dict[str, Any]:
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    for i, chunk in enumerate(chunks):
        _policy_chunks.append({'policy_id': policy_id, 'title': title, 'chunk_index': i, 'chunk_text': chunk})
    return {'policy_id': policy_id, 'chunks': len(chunks)}


def query_policy(question: str) -> dict[str, Any]:
    corpus = [{'claim_id': f"{c['policy_id']}-{c['chunk_index']}", 'claim_text': c['chunk_text'], 'claim_type': 'POLICY', 'status': 'ACTIVE'} for c in _policy_chunks]
    hits = similarity_search(question, corpus, top_k=3)
    answer = 'No matching clause found.'
    if hits:
        answer = ' '.join(h['claim_text'] for h in hits[:2])[:700]
    return {
        'answer': answer,
        'sources': [h['claim_id'] for h in hits],
        'relevant_chunks': hits,
        'confidence': round(hits[0]['similarity_score'], 4) if hits else 0.0,
    }
