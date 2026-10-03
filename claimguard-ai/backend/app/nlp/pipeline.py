import math
import re
from collections import Counter
from datetime import datetime
from functools import lru_cache
from typing import Any

import numpy as np
from langdetect import detect_langs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SUPPORTED_LANGS = {'en': 'English', 'hi': 'Hindi', 'te': 'Telugu'}
ENTITY_PATTERNS = {
    'MONEY': r'(?:INR|Rs\.?|\$)\s?\d+[\d,]*(?:\.\d+)?',
    'DATE': r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[A-Za-z]+)\b',
    'TIME': r'\b\d{1,2}:\d{2}(?:\s?[APMapm]{2})?\b',
    'POLICY': r'\b(?:POL|PLC|POLICY)[-\s]?\w+\b',
    'VEHICLE': r'\b(?:Honda|Hyundai|Maruti|Tata|Toyota|Mahindra)\s+\w+\b',
    'LOCATION': r'\b(?:Hyderabad|Delhi|Mumbai|Bengaluru|Chennai|Pune|Kolkata)\b',
}
EVENT_KEYWORDS = {
    'POLICY_PURCHASE': ['policy purchased', 'bought policy'],
    'ACCIDENT': ['accident', 'collision', 'crash'],
    'THEFT': ['theft', 'stolen'],
    'DAMAGE': ['damaged', 'damage'],
    'POLICE_REPORT': ['police report', 'fir'],
    'HOSPITAL_VISIT': ['hospital', 'injury', 'admitted'],
    'REPAIR': ['repair', 'garage'],
    'CLAIM_SUBMISSION': ['claim submitted', 'submitted claim'],
    'SURVEY': ['surveyor', 'survey'],
}


def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def sentence_tokenize(text: str) -> list[str]:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def tokenize_text(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9'-]+", text.lower())


def lemmatize_text(text: str) -> list[str]:
    words = tokenize_text(text)
    lemmas = []
    for w in words:
        if w.endswith('ing') and len(w) > 4:
            lemmas.append(w[:-3])
        elif w.endswith('ed') and len(w) > 3:
            lemmas.append(w[:-2])
        else:
            lemmas.append(w)
    return lemmas


def normalize_dates(text: str) -> str:
    return re.sub(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', r'\1-\2-\3', text)


def normalize_money(text: str) -> str:
    return re.sub(r'Rs\.?\s?', 'INR ', text, flags=re.IGNORECASE)


def clean_noise(text: str) -> str:
    return re.sub(r'[^\w\s.,:/-]', '', text)


def preprocess_text(text: str) -> dict[str, Any]:
    normalized = normalize_text(text)
    normalized = normalize_dates(normalized)
    normalized = normalize_money(normalized)
    cleaned = clean_noise(normalized)
    return {
        'normalized_text': cleaned,
        'sentences': sentence_tokenize(cleaned),
        'tokens': tokenize_text(cleaned),
        'lemmas': lemmatize_text(cleaned),
    }


def detect_language(text: str) -> dict[str, Any]:
    try:
        candidates = detect_langs(text)
        best = candidates[0]
        code = best.lang
        return {
            'language': SUPPORTED_LANGS.get(code, code),
            'code': code,
            'confidence': round(best.prob, 4),
            'original_text': text,
            'normalized_text': normalize_text(text),
        }
    except Exception:
        return {'language': 'Unknown', 'code': 'unknown', 'confidence': 0.0, 'original_text': text, 'normalized_text': text}


def extract_entities(text: str) -> list[dict[str, str]]:
    entities = []
    for label, pattern in ENTITY_PATTERNS.items():
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            entities.append({'text': m.group(0), 'label': label})
    for m in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text):
        entities.append({'text': m.group(0), 'label': 'PERSON'})
    unique = {(e['text'], e['label']): e for e in entities}
    return list(unique.values())


def extract_relations(text: str, entities: list[dict[str, str]]) -> list[dict[str, str]]:
    by_label = {}
    for e in entities:
        by_label.setdefault(e['label'], []).append(e['text'])
    relations = []
    if by_label.get('PERSON') and by_label.get('VEHICLE'):
        relations.append({'source': by_label['PERSON'][0], 'relation': 'OWNS', 'target': by_label['VEHICLE'][0]})
    if by_label.get('VEHICLE') and any(k in text.lower() for k in ['accident', 'collision', 'crash']):
        relations.append({'source': by_label['VEHICLE'][0], 'relation': 'INVOLVED_IN', 'target': 'ACCIDENT'})
    if any(k in text.lower() for k in ['accident', 'collision']) and by_label.get('LOCATION'):
        relations.append({'source': 'ACCIDENT', 'relation': 'OCCURRED_AT', 'target': by_label['LOCATION'][0]})
    if by_label.get('DATE'):
        relations.append({'source': 'CLAIM', 'relation': 'SUBMITTED_ON', 'target': by_label['DATE'][0]})
    return relations


def extract_events(text: str) -> list[dict[str, Any]]:
    lowered = text.lower()
    entities = extract_entities(text)
    date = next((e['text'] for e in entities if e['label'] == 'DATE'), '')
    time = next((e['text'] for e in entities if e['label'] == 'TIME'), '')
    location = next((e['text'] for e in entities if e['label'] == 'LOCATION'), '')
    events = []
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            events.append({
                'event_type': event_type,
                'event_text': text,
                'date': date,
                'time': time,
                'location': location,
                'confidence': 0.72,
            })
    return events


def _softmax(vals: list[float]) -> list[float]:
    e = np.exp(vals - np.max(vals))
    return (e / e.sum()).tolist()


def classify_claim(text: str) -> dict[str, Any]:
    lowered = text.lower()
    score = 0
    for token in ['urgent', 'cash', 'immediately', 'stolen', 'multiple', 'contradiction']:
        if token in lowered:
            score += 1
    logits = [max(0.0, 3.0 - score), 2.0 + abs(2 - score), 1.0 + score]
    probs = _softmax(np.array(logits, dtype=float))
    labels = ['LOW_SUSPICION', 'MEDIUM_SUSPICION', 'HIGH_SUSPICION']
    idx = int(np.argmax(probs))
    return {
        'label': labels[idx],
        'probabilities': {labels[i]: round(float(p), 4) for i, p in enumerate(probs)},
        'confidence': round(float(probs[idx]), 4),
        'method': 'lightweight-fallback-classifier',
    }


def generate_embedding(text: str) -> list[float]:
    vec = np.zeros(64)
    for i, token in enumerate(tokenize_text(text)):
        vec[i % 64] += (sum(ord(c) for c in token) % 97) / 97
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.round(6).tolist()


def similarity_search(text: str, corpus: list[dict[str, str]], top_k: int = 5) -> list[dict[str, Any]]:
    docs = [text] + [c['claim_text'] for c in corpus]
    if len(corpus) == 0:
        return []
    v = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = v.fit_transform(docs)
    scores = cosine_similarity(matrix[0:1], matrix[1:])[0]
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    out = []
    for idx, score in ranked:
        c = corpus[idx]
        out.append({
            'claim_id': c.get('claim_id', f'C{idx+1}'),
            'similarity_score': round(float(score), 4),
            'claim_text': c['claim_text'],
            'claim_type': c.get('claim_type', 'GENERAL'),
            'historical_status': c.get('status', 'ANALYZED'),
        })
    return out


def detect_duplicates(text: str, corpus: list[dict[str, str]]) -> dict[str, Any]:
    sims = similarity_search(text, corpus, top_k=10)
    exact = [s for s in sims if normalize_text(s['claim_text']).lower() == normalize_text(text).lower()]
    near = [s for s in sims if s['similarity_score'] >= 0.8]
    prob = min(1.0, 0.25 * len(near) + 0.6 * len(exact))
    patterns = Counter()
    for s in near:
        for token in set(tokenize_text(s['claim_text'])):
            if len(token) > 4:
                patterns[token] += 1
    common_patterns = [p for p, _ in patterns.most_common(5)]
    return {
        'duplicate_probability': round(prob, 4),
        'related_claims': near,
        'common_patterns': common_patterns,
    }


def detect_contradiction(a: str, b: str) -> dict[str, Any]:
    ea = extract_entities(a)
    eb = extract_entities(b)
    dates_a = {e['text'] for e in ea if e['label'] == 'DATE'}
    dates_b = {e['text'] for e in eb if e['label'] == 'DATE'}
    loc_a = {e['text'] for e in ea if e['label'] == 'LOCATION'}
    loc_b = {e['text'] for e in eb if e['label'] == 'LOCATION'}
    contradiction = (dates_a and dates_b and dates_a != dates_b) or (loc_a and loc_b and loc_a != loc_b)
    if contradiction:
        rel, conf = 'CONTRADICTION', 0.84
    elif set(tokenize_text(a)).intersection(set(tokenize_text(b))):
        rel, conf = 'ENTAILMENT', 0.7
    else:
        rel, conf = 'NEUTRAL', 0.55
    return {'statement_a': a, 'statement_b': b, 'relationship': rel, 'confidence': conf}


def summarize_text(text: str) -> dict[str, Any]:
    sentences = sentence_tokenize(text)
    short = ' '.join(sentences[:1]) if sentences else text
    detailed = ' '.join(sentences[: min(3, len(sentences))]) if sentences else text
    key_points = sentences[:5]
    return {'short_summary': short, 'detailed_summary': detailed, 'key_points': key_points}


def discover_topics(texts: list[str]) -> dict[str, Any]:
    buckets = {
        'Vehicle Accident': ['accident', 'collision', 'vehicle'],
        'Theft': ['theft', 'stolen'],
        'Fire': ['fire', 'burn'],
        'Medical': ['hospital', 'injury', 'medical'],
        'Property Damage': ['property', 'house', 'damage'],
        'Natural Disaster': ['flood', 'storm', 'earthquake'],
    }
    topics = []
    for t in texts:
        lower = t.lower()
        assigned = 'Other'
        for topic, kws in buckets.items():
            if any(k in lower for k in kws):
                assigned = topic
                break
        topics.append({'text': t, 'topic': assigned})
    return {'topics': topics}


def calculate_risk_score(classification: dict[str, Any], similarity_signal: float, contradiction_signal: float, temporal_signal: float, structured_signal: float = 0.0) -> dict[str, Any]:
    weights = {
        'transformer': 0.31,
        'similarity': 0.22,
        'contradiction': 0.28,
        'temporal': 0.09,
        'structured': 0.10,
    }
    cls_map = {'LOW_SUSPICION': 25, 'MEDIUM_SUSPICION': 55, 'HIGH_SUSPICION': 85}
    transformer_value = cls_map.get(classification.get('label', 'LOW_SUSPICION'), 25)
    score = (
        weights['transformer'] * transformer_value
        + weights['similarity'] * similarity_signal
        + weights['contradiction'] * contradiction_signal
        + weights['temporal'] * temporal_signal
        + weights['structured'] * structured_signal
    )
    score = max(0.0, min(100.0, score))
    level = 'LOW_SUSPICION' if score <= 30 else 'MEDIUM_SUSPICION' if score <= 70 else 'HIGH_SUSPICION'
    return {
        'risk_score': round(score, 2),
        'risk_level': level,
        'signal_breakdown': {
            'Transformer NLP Signal': f"{int(weights['transformer'] * 100)}%",
            'Similarity Signal': f"{int(weights['similarity'] * 100)}%",
            'Contradiction Signal': f"{int(weights['contradiction'] * 100)}%",
            'Temporal Signal': f"{int(weights['temporal'] * 100)}%",
            'Structured Signal': f"{int(weights['structured'] * 100)}%",
        },
    }


def claim_completeness(text: str, claim_type: str = 'GENERAL') -> dict[str, Any]:
    missing = []
    for label, desc in [('DATE', 'Incident date'), ('TIME', 'Incident time'), ('LOCATION', 'Incident location')]:
        if not any(e['label'] == label for e in extract_entities(text)):
            missing.append(desc)
    if 'police' in claim_type.lower() and 'fir' not in text.lower():
        missing.append('Police report number')
    score = max(0, 100 - 20 * len(missing))
    return {'completeness_score': score, 'missing_information': missing, 'reasoning': 'Derived from expected incident context fields and claim narrative evidence.'}
