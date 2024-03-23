from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from .base import Base


class ExecutionLog(Base):
    __tablename__ = 'execution_logs'

    execution_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('code_files.file_id'), nullable=False)
    execution_time = Column(DateTime(timezone=True), server_default=func.now())
    exit_code = Column(Integer, nullable=False)
    execution_output = Column(Text, default='')