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

    def __init__(self, id, first_name, last_name, pod, bed):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.pod = pod
        self.bed = bed

    def get_metadata(self) -> dict:
        nurse_dict = {'id': self.id,
                      'first_name': self.first_name,
                      'last_name': self.last_name,
                      'pod': self.pod,
                      'bed': self.bed}
        return nurse_dict