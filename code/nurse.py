from sqlalchemy import Table, Column, Integer, String
from base import Base

class Nurse(Base):
    """ Represents a nurse """

    __tablename__ = "nurse"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    pod = Column(String(100), nullable=True)
    bed = Column(Integer, nullable=True)