import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), default="strategic")  # pricing, inventory, marketing, cost_reduction, growth
    description = Column(Text, nullable=False)
    
    # Rigorous Grounding & Reasoning
    rationale = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False)      # underlying KPIs, metrics, datasets cited
    assumptions = Column(JSON, nullable=False)   # explicit assumptions list
    expected_impact = Column(JSON, nullable=False) # financial/operational impact breakdown
    
    # Multi-Option evaluation matrix
    options_matrix = Column(JSON, nullable=True) # evaluated options with profit, risk, feasibility scores
    recommended_option = Column(String(100), nullable=True)
    
    confidence_score = Column(Float, default=0.85) # 0.0 - 1.0
    risk_level = Column(String(20), default="medium") # low, medium, high, critical
    
    # Human-in-the-Loop Lifecycle
    status = Column(String(50), default="proposed") # proposed, approved, rejected, implemented
    reviewed_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    organization = relationship("Organization", back_populates="decisions")
