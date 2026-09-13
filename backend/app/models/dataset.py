import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False, default="csv")  # csv, excel, json, demo
    file_path = Column(String(512), nullable=True)
    table_name = Column(String(100), nullable=False, index=True)  # DuckDB table reference
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    
    # Metadata & Quality
    schema_info = Column(JSON, nullable=True)       # detected columns, inferred types, null counts
    quality_score = Column(Float, default=100.0)    # 0.0 - 100.0
    quality_report = Column(JSON, nullable=True)    # detailed metrics, issues found
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    organization = relationship("Organization", back_populates="datasets")
