from sqlalchemy import Table, Column, Integer, String
from base import Base

class Patient(Base):
    """ Represents a patient """

    __tablename__ = "patient"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    clinical_area = Column(String(100), nullable=True)
    bed_num = Column(Integer, nullable=True)
    acuity = Column(Integer, nullable=False)

    def __init__(self, id: int, first_name: str, last_name: str, clinical_area: str, bed_num: int, acuity: int) -> None:
        """ Validates and Initializes a Patient """
        Patient._validate_positive_integer("Patient ID", id)
        self.id = id

        Patient._validate_string_250("First name", first_name)
        self.first_name = first_name

        Patient._validate_string_250("Last name", last_name)
        self.last_name = last_name

        Patient._validate_string_250("Clinical area", clinical_area)
        self.clinical_area = clinical_area

        Patient._validate_positive_integer("bed_num number", bed_num)
        self.bed_num = bed_num

        Patient._validate_positive_integer("acuity", acuity)
        self.acuity = acuity

    ###############################################
    #                Public Methods               #
    ###############################################
    def get_id(self) -> int:
        """ get id of patient """
        return self.id

    def get_name(self) -> str:
        """ get full name of patient """
        return self.first_name + self.last_name
    
    def get_clinical_area(self) -> str:
        """ get clinical area that patient is currently assigned """
        return self.clinical_area
    
    def get_bed_num(self) -> int:
        """ get bed number that patient is currently assigned """
        return self.bed_num

    def get_acuity(self) -> int:
        """ get acuity of the patient"""
        return self.acuity
    
    ###############################################
    #                Public Methods               #
    ###############################################
    def to_dict(self) -> dict:
        """ Returns patient information in a dictionary """
        patient_dict = {}

        patient_dict['id'] = self.id
        patient_dict['first_name'] = self.first_name
        patient_dict['last_name'] = self.last_name
        patient_dict['clinical_area'] = self.clinical_area
        patient_dict['bed_num'] = self.bed_num
        patient_dict['acuity'] = self.acuity

        return patient_dict
    

    ###############################################
    #              Validator Methods              #
    ###############################################
    @staticmethod
    def _validate_string_250(input_value: str, str_value: str) -> None:
        """ Checks if input is string """
        if str_value is None or not isinstance(str_value, str):
            raise ValueError(input_value + " is not a string.")
        if str_value == "":
            raise ValueError(input_value + " cannot be empty.")
        if len(str_value) > 250:
            raise ValueError(input_value + " cannot be longer than 250 characters.")
    
    @staticmethod
    def _validate_positive_integer(input_value: str, int_value: int) -> None:
        """ Checks if input is integer and not negative """
        if not isinstance(int_value, int):
            raise ValueError(input_value + " is not an integer.")
        if int_value is None:
            raise ValueError(input_value + " cannot be empty.")
        if int_value < 0:
            raise ValueError(input_value + " cannot be negative.")