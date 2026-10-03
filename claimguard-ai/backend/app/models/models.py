from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))
    role: Mapped[Role] = relationship()


class Claim(Base, TimestampMixin):
    __tablename__ = 'claims'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[str] = mapped_column(String(64), unique=True)
    customer_id: Mapped[str] = mapped_column(String(64), default='UNKNOWN')
    policy_id: Mapped[str] = mapped_column(String(64), default='UNKNOWN')
    claim_text: Mapped[str] = mapped_column(Text)
    claim_type: Mapped[str] = mapped_column(String(64), default='GENERAL')
    claim_amount: Mapped[float] = mapped_column(Float, default=0.0)
    incident_date: Mapped[str] = mapped_column(String(32), default='')
    incident_time: Mapped[str] = mapped_column(String(32), default='')
    incident_location: Mapped[str] = mapped_column(String(128), default='')
    previous_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default='NEW')


class ClaimDocument(Base, TimestampMixin):
    __tablename__ = 'claim_documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128))
    extracted_text: Mapped[str] = mapped_column(Text, default='')


class ClaimEntity(Base):
    __tablename__ = 'claim_entities'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    text: Mapped[str] = mapped_column(String(255))
    label: Mapped[str] = mapped_column(String(64))


class ClaimRelation(Base):
    __tablename__ = 'claim_relations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    source: Mapped[str] = mapped_column(String(255))
    relation: Mapped[str] = mapped_column(String(64))
    target: Mapped[str] = mapped_column(String(255))


class ClaimEvent(Base):
    __tablename__ = 'claim_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    event_type: Mapped[str] = mapped_column(String(64))
    event_text: Mapped[str] = mapped_column(Text)
    date: Mapped[str] = mapped_column(String(32), default='')
    time: Mapped[str] = mapped_column(String(32), default='')
    location: Mapped[str] = mapped_column(String(128), default='')
    confidence: Mapped[float] = mapped_column(Float, default=0.0)


class ClaimAnalysis(Base, TimestampMixin):
    __tablename__ = 'claim_analyses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    classification_label: Mapped[str] = mapped_column(String(64), default='LOW_SUSPICION')
    classification_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    summary: Mapped[str] = mapped_column(Text, default='')


class ClaimSimilarity(Base):
    __tablename__ = 'claim_similarity'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    similar_claim_id: Mapped[str] = mapped_column(String(64))
    similarity_score: Mapped[float] = mapped_column(Float, default=0.0)


class ClaimCluster(Base):
    __tablename__ = 'claim_clusters'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cluster_name: Mapped[str] = mapped_column(String(100))


class NLPResult(Base, TimestampMixin):
    __tablename__ = 'nlp_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    stage: Mapped[str] = mapped_column(String(64))
    result_json: Mapped[str] = mapped_column(Text)


class PolicyDocument(Base, TimestampMixin):
    __tablename__ = 'policy_documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)


class PolicyChunk(Base):
    __tablename__ = 'policy_chunks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_document_id: Mapped[int] = mapped_column(ForeignKey('policy_documents.id'))
    chunk_index: Mapped[int] = mapped_column(Integer)
    chunk_text: Mapped[str] = mapped_column(Text)


class InvestigatorFeedback(Base, TimestampMixin):
    __tablename__ = 'investigator_feedback'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    reviewer: Mapped[str] = mapped_column(String(100))
    ai_prediction: Mapped[str] = mapped_column(String(64))
    ai_risk_score: Mapped[float] = mapped_column(Float)
    decision: Mapped[str] = mapped_column(String(64))
    comments: Mapped[str] = mapped_column(Text, default='')


class ModelRun(Base, TimestampMixin):
    __tablename__ = 'model_runs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(128))
    metrics_json: Mapped[str] = mapped_column(Text)


class Dataset(Base, TimestampMixin):
    __tablename__ = 'datasets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    rows: Mapped[int] = mapped_column(Integer, default=0)
    columns: Mapped[int] = mapped_column(Integer, default=0)


class Report(Base, TimestampMixin):
    __tablename__ = 'reports'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id_fk: Mapped[int] = mapped_column(ForeignKey('claims.id'))
    report_text: Mapped[str] = mapped_column(Text)
