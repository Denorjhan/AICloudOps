from sqlalchemy import Column, Integer, VARCHAR, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Script(Base):
    __tablename__ = 'scripts'

    script_id = Column(Integer, primary_key=True)
    script_name = Column(VARCHAR(127), nullable=False, unique=True)
    script_content = Column(Text, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    executed_at = Column(TIMESTAMP(timezone=True))
    
    # Constraints
    __table_args__ = (
        CheckConstraint('length(script_content) > 0'),
        CheckConstraint('created_at <= CURRENT_TIMESTAMP'),
        CheckConstraint('executed_at IS NULL OR executed_at <= CURRENT_TIMESTAMP')
    )


class Vector(Base):
    __tablename__ = 'vectors'

    vector_id = Column(Integer, ForeignKey('scripts.script_id', ondelete="CASCADE"), primary_key=True)
    vector = Column(Vector(1536), nullable=False)

    # Relationship
    script = relationship('Script', backref='vectors')
