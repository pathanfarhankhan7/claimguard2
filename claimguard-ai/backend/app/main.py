from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .database import Base, engine

app = FastAPI(title='ClaimGuard AI', description='Understand Claims. Detect Patterns. Investigate Smarter.')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

Base.metadata.create_all(bind=engine)
app.include_router(router)


@app.get('/health')
def health():
    return {'status': 'ok'}
