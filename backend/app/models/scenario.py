import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Base dataset reference
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    
    # Input parameters for simulation
    # e.g., {"price_change_pct": 5, "marketing_spend_pct": 10, "operating_cost_pct": -5, "churn_rate_pct": -2}
    parameters = Column(JSON, nullable=False)
    
    # Baseline vs Projected outputs
    # e.g., {"baseline": {"revenue": 1000000, "profit": 150000}, "projected": {"revenue": 1045000, "profit": 182000}, "deltas": {...}}
    results = Column(JSON, nullable=False)
    
    risk_score = Column(Float, default=0.0)      # 0 - 100
    risk_assessment = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    organization = relationship("Organization", back_populates="scenarios")
    creator = relationship("User", back_populates="scenarios")
