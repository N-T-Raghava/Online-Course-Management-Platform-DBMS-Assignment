from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func

from app.database import Base


class AdminAudit(Base):
    __tablename__ = "admin_audit"

    audit_id = Column(Integer, primary_key=True, index=True)

    admin_user_id = Column(Integer, nullable=False)
    admin_level = Column(String(20))

    action = Column(String(255))
    method = Column(String(10))

    status_code = Column(Integer)

    timestamp = Column(
        TIMESTAMP,
        server_default=func.now()
    )