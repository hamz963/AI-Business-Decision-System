import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class KPIDefinition(Base):
    __tablename__ = "kpi_definitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    category = Column(String(50), default="financial")  # financial, sales, marketing, operations, customer
    description = Column(String(500), nullable=True)
    
    # Formula & aggregation
    formula = Column(String(255), nullable=False)  # formula or SQL expression
    unit = Column(String(20), default="$")         # $, %, count, ratio
    target_value = Column(Float, nullable=True)
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    
    # Current cached values
    current_value = Column(Float, nullable=True)
    previous_value = Column(Float, nullable=True)
    change_pct = Column(Float, nullable=True)
    status = Column(String(20), default="healthy")  # healthy, warning, critical
    
    metadata_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    organization = relationship("Organization", back_populates="kpis")
