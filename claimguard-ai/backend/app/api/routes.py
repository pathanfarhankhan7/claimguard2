from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from ..documents.processor import extract_text
from ..nlp import pipeline
from ..rag.service import query_policy, upload_policy
from ..schemas.schemas import ClaimCreate, FeedbackRequest, GenericResponse, NLIRequest, TextRequest
from ..services.store import add_claim, get_claim, get_claims

router = APIRouter(prefix='/api')


def _disclaimer_payload(data):
    return GenericResponse(data=data)


@router.post('/nlp/preprocess')
def nlp_preprocess(payload: TextRequest):
    return _disclaimer_payload(pipeline.preprocess_text(payload.text))


@router.post('/nlp/language-detect')
def nlp_language(payload: TextRequest):
    return _disclaimer_payload(pipeline.detect_language(payload.text))


@router.post('/nlp/entities')
def nlp_entities(payload: TextRequest):
    return _disclaimer_payload({'text': payload.text, 'entities': pipeline.extract_entities(payload.text)})


@router.post('/nlp/relations')
def nlp_relations(payload: TextRequest):
    entities = pipeline.extract_entities(payload.text)
    return _disclaimer_payload({'relations': pipeline.extract_relations(payload.text, entities)})


@router.post('/nlp/events')
def nlp_events(payload: TextRequest):
    return _disclaimer_payload({'events': pipeline.extract_events(payload.text)})


@router.post('/nlp/classify')
def nlp_classify(payload: TextRequest):
    return _disclaimer_payload(pipeline.classify_claim(payload.text))


@router.post('/nlp/embed')
def nlp_embed(payload: TextRequest):
    return _disclaimer_payload({'embedding': pipeline.generate_embedding(payload.text)})


@router.post('/nlp/similarity')
def nlp_similarity(payload: TextRequest):
    return _disclaimer_payload({'results': pipeline.similarity_search(payload.text, get_claims(), top_k=10)})


@router.post('/nlp/duplicate-detection')
def nlp_duplicate(payload: TextRequest):
    return _disclaimer_payload(pipeline.detect_duplicates(payload.text, get_claims()))


@router.post('/nlp/contradiction')
def nlp_contradiction(payload: NLIRequest):
    return _disclaimer_payload(pipeline.detect_contradiction(payload.statement_a, payload.statement_b))


@router.post('/nlp/summarize')
def nlp_summarize(payload: TextRequest):
    return _disclaimer_payload(pipeline.summarize_text(payload.text))


@router.post('/nlp/topics')
def nlp_topics(payload: dict):
    texts = payload.get('texts', [])
    return _disclaimer_payload(pipeline.discover_topics(texts))


@router.post('/claims')
def create_claim(payload: ClaimCreate):
    claim = payload.model_dump()
    add_claim(claim)
    return _disclaimer_payload(claim)


@router.get('/claims/{claim_id}/timeline')
def claim_timeline(claim_id: str):
    c = get_claim(claim_id)
    if not c:
        raise HTTPException(404, 'Claim not found')
    events = pipeline.extract_events(c['claim_text'])
    events_sorted = sorted(events, key=lambda x: x.get('date') or '9999-99-99')
    return _disclaimer_payload({'claim_id': claim_id, 'timeline': events_sorted})


@router.post('/documents/upload')
def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix
    temp = Path('/tmp') / file.filename
    temp.write_bytes(file.file.read())
    try:
        data = extract_text(temp)
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        temp.unlink(missing_ok=True)
    return _disclaimer_payload(data)


@router.post('/rag/upload')
def rag_upload(payload: dict):
    return _disclaimer_payload(upload_policy(payload['policy_id'], payload['title'], payload['text']))


@router.post('/rag/query')
def rag_query(payload: TextRequest):
    return _disclaimer_payload(query_policy(payload.text))


@router.post('/investigation/chat')
def investigation_chat(payload: dict):
    claim_id = payload.get('claim_id')
    question = payload.get('question', '')
    claim = get_claim(claim_id) if claim_id else None
    if not claim:
        raise HTTPException(404, 'Claim not found for investigation')
    summary = pipeline.summarize_text(claim['claim_text'])
    cls = pipeline.classify_claim(claim['claim_text'])
    dup = pipeline.detect_duplicates(claim['claim_text'], [c for c in get_claims() if c['claim_id'] != claim_id])
    response = {
        'question': question,
        'answer': f"Claim {claim_id} classified as {cls['label']} with duplicate probability {dup['duplicate_probability']}.",
        'evidence': {
            'summary': summary,
            'classification': cls,
            'duplicate_detection': dup,
        },
    }
    return _disclaimer_payload(response)


@router.post('/feedback')
def feedback(payload: FeedbackRequest):
    return _disclaimer_payload(payload.model_dump())


@router.post('/claims/analyze')
def analyze_claim(payload: TextRequest):
    pre = pipeline.preprocess_text(payload.text)
    lang = pipeline.detect_language(payload.text)
    ents = pipeline.extract_entities(payload.text)
    rel = pipeline.extract_relations(payload.text, ents)
    events = pipeline.extract_events(payload.text)
    cls = pipeline.classify_claim(payload.text)
    sims = pipeline.similarity_search(payload.text, get_claims(), top_k=5)
    dup = pipeline.detect_duplicates(payload.text, get_claims())
    contradiction_signal = 80 if 'contradiction' in payload.text.lower() else 20
    risk = pipeline.calculate_risk_score(cls, similarity_signal=dup['duplicate_probability']*100, contradiction_signal=contradiction_signal, temporal_signal=10)
    return _disclaimer_payload({
        'pipeline': ['Document Processing', 'Language Detection', 'Preprocessing', 'NER', 'Relations', 'Events', 'Classification', 'Similarity', 'Contradictions', 'Summarization', 'Policy Retrieval', 'Risk Assessment'],
        'language': lang,
        'preprocessing': pre,
        'entities': ents,
        'relations': rel,
        'events': events,
        'classification': cls,
        'similar_claims': sims,
        'duplicate_detection': dup,
        'summary': pipeline.summarize_text(payload.text),
        'risk': risk,
        'completeness': pipeline.claim_completeness(payload.text),
    })
