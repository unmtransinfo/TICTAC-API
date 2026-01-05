from sqlalchemy import BigInteger, Column, Text

from app.db.database import Base


class Study(Base):
    """Model for core.study table."""

    __tablename__ = "study"
    __table_args__ = {"schema": "core"}

    study_id = Column(BigInteger, primary_key=True, autoincrement=True)
    nct_id = Column(Text, nullable=False, unique=True)
