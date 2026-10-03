# ClaimGuard AI

**Understand Claims. Detect Patterns. Investigate Smarter.**

ClaimGuard AI is an NLP-powered insurance claim intelligence and fraud-risk investigation platform that uses transformer-based language understanding, named entity recognition, relation and event extraction, semantic similarity, natural language inference, document intelligence, text summarization, retrieval-augmented generation, knowledge graphs, and explainable AI to support human investigation of insurance claims.

## Disclaimer
ClaimGuard AI provides AI-assisted claim analysis and investigation support. AI predictions are not definitive determinations of fraud, liability, or coverage.

## Structure
- `frontend/` React + TypeScript + Vite
- `backend/` FastAPI + SQLAlchemy + Alembic
- `data/` Synthetic Demonstration Data
- `docs/` API and academic documentation

## Quick Start
```bash
docker compose up --build
```

## Backend
```bash
cd backend
pip install -r requirements.txt
pytest app/tests -q
uvicorn app.main:app --reload
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
See `.env.example` for model and runtime configuration:
- `CLASSIFICATION_MODEL`
- `EMBEDDING_MODEL`
- `NLI_MODEL`
- `SUMMARIZATION_MODEL`

## Demo Credentials
Create users via API/DB seeding for `ADMIN` and `INVESTIGATOR` roles.

## API Docs
- FastAPI OpenAPI at `/docs`
- Extended reference at `docs/api.md`

## Dataset Format
`data/synthetic_claims.csv` includes multilingual synthetic claims labeled as `Synthetic Demonstration Data`.

## Testing
Includes API and NLP tests under `backend/app/tests`.

## Limitations & Future Scope
See `docs/future-scope.md` and `docs/model-evaluation.md` for roadmap and evaluation expansion.
