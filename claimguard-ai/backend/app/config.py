from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'ClaimGuard AI'
    database_url: str = 'sqlite:///./claimguard.db'
    jwt_secret: str = 'change-me'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60

    classification_model: str = 'distilbert-base-uncased-finetuned-sst-2-english'
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    nli_model: str = 'cross-encoder/nli-deberta-v3-small'
    summarization_model: str = 'sshleifer/distilbart-cnn-12-6'
    spacy_model: str = 'en_core_web_sm'
    ocr_enabled: bool = True
    use_mock_models: bool = True


settings = Settings()
