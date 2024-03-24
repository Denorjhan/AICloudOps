from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from .base import Base



class CodeFiles(Base):
    __tablename__ = 'code_files'

    file_id = Column(Integer, primary_key=True)
    file_path = Column(String(255), nullable=False) #, unique=True)
    file_hash = Column(String(64), nullable=False, unique=True)


