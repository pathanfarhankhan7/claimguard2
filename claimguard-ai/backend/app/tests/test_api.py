from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_preprocess_endpoint():
    r = client.post('/api/nlp/preprocess', json={'text': 'Ravi met with accident on 15/09/2026 at 10:30 PM in Hyderabad.'})
    assert r.status_code == 200
    data = r.json()['data']
    assert 'normalized_text' in data


def test_entities_and_relations():
    text = "Ravi's Honda City had an accident near Hyderabad on 15 September."
    entities = client.post('/api/nlp/entities', json={'text': text}).json()['data']['entities']
    assert any(e['label'] == 'VEHICLE' for e in entities)
    rel = client.post('/api/nlp/relations', json={'text': text}).json()['data']['relations']
    assert isinstance(rel, list)


def test_claim_analysis_pipeline():
    r = client.post('/api/claims/analyze', json={'text': 'My car was stolen in Hyderabad on 10/10/2026 and claim submitted urgently.'})
    assert r.status_code == 200
    data = r.json()['data']
    assert 'classification' in data
    assert 'risk' in data


def test_contradiction_detection():
    r = client.post('/api/nlp/contradiction', json={'statement_a': 'Accident happened on 10/10/2026 in Hyderabad.', 'statement_b': 'Accident happened on 11/10/2026 in Mumbai.'})
    assert r.status_code == 200
    assert r.json()['data']['relationship'] in {'CONTRADICTION', 'ENTAILMENT', 'NEUTRAL'}
