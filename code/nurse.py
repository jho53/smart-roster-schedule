from sqlalchemy import Table, Column, Integer, String
from base import Base


class Nurse(Base):
    """ Represents a nurse """

    # Creating table schema for nurse
    __tablename__ = "nurse"

    # Defining column names and types
    id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    clinical_area = Column(String(250), nullable=True)
    bed_num = Column(Integer, nullable=True)
    skill_level = Column(Integer, nullable=True)

    def __init__(self, id: int, first_name: str, last_name: str, clinical_area: str, bed_num: int, skill_level: int, num_patients: int) -> None:
        """ Validates and Initializes a Nurse """
        Nurse._validate_positive_integer("Nurse ID", id)
        self.id = id

        Nurse._validate_string_250("First name", first_name)
        self.first_name = first_name

        Nurse._validate_string_250("Last name", last_name)
        self.last_name = last_name

        Nurse._validate_string_250("Clinical area", clinical_area)
        self.clinical_area = clinical_area

        Nurse._validate_positive_integer("Bed number", bed_num)
        self.bed_num = bed_num

        Nurse._validate_positive_integer("Skill level", skill_level)
        self.skill_level = skill_level

        Nurse._validate_positive_integer("Number of patients", num_patients)
        self.num_patients = num_patients

    ###############################################
    #                Public Methods               #
    ###############################################
    def get_id(self) -> int:
        """ get id of nurse """
        return self.id

    def get_name(self) -> str:
        """ get full name of nurse """
        return self.first_name + self.last_name

    def get_clinical_area(self) -> str:
        """ get clinical area that nurse is currently assigned """
        return self.clinical_area

    def get_bed_num(self) -> int:
        """ get bed number that nurse is currently assigned """
        return self.bed_num

    def get_skill_level(self) -> int:
        """ get skill level that nurse is currently assigned """
        return self.skill_level

    def get_num_patients(self) -> int:
        """ get number of patients that nurse is currently assigned """
        return self.num_patients

    def set_num_patients(self, num_patients):
        """ set the number of patients """
        self.num_patients = num_patients


    ###############################################
    #                Public Methods               #
    ###############################################
    def to_dict(self) -> dict:
        """ Returns nurse information in a dictionary """
        nurse_dict = {}

        nurse_dict['id'] = self.id
        nurse_dict['first_name'] = self.first_name
        nurse_dict['last_name'] = self.last_name
        nurse_dict['clinical_area'] = self.clinical_area
        nurse_dict['bed_num'] = self.bed_num

        return nurse_dict

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
