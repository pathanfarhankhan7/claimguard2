# API Reference

All responses include disclaimer:

> ClaimGuard AI provides AI-assisted claim analysis and investigation support. AI predictions are not definitive determinations of fraud, liability, or coverage.

## NLP
- POST `/api/nlp/preprocess`
- POST `/api/nlp/language-detect`
- POST `/api/nlp/entities`
- POST `/api/nlp/relations`
- POST `/api/nlp/events`
- POST `/api/nlp/classify`
- POST `/api/nlp/embed`
- POST `/api/nlp/similarity`
- POST `/api/nlp/duplicate-detection`
- POST `/api/nlp/contradiction`
- POST `/api/nlp/summarize`
- POST `/api/nlp/topics`

## Claims
- POST `/api/claims`
- POST `/api/claims/analyze`
- GET `/api/claims/{claim_id}/timeline`

## Documents / RAG / Feedback
- POST `/api/documents/upload`
- POST `/api/rag/upload`
- POST `/api/rag/query`
- POST `/api/investigation/chat`
- POST `/api/feedback`
