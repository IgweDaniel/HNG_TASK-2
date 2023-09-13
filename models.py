from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    age = Column(Integer, nullable=True)
    married = Column(Boolean, default=False)
