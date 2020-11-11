from sqlalchemy import Table, Column, Integer, String, Boolean, Float
from base import Base


class Nurse(Base):
    """ Represents a nurse """

    # Creating table schema for nurse
    __tablename__ = "nurse"

    # Defining column names and types
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    clinical_area = Column(String(250), nullable=True)
    bed_num = Column(Integer, nullable=True)
    rotation = Column(String(250), nullable=True)
    group = Column(Integer, nullable=True)
    fte = Column(Float, nullable=True)
    skill_level = Column(Integer, nullable=True)
    a_trained = Column(Boolean, nullable=True)
    transfer = Column(Boolean, nullable=True)
    picc = Column(Boolean, nullable=True)
    advanced_role = Column(String(250), nullable=True)
    previous_patients = Column(String(250), nullable=True)  # not too sure how to store this
    dta = Column(String(250), nullable=True)
    comments = Column(String(250), nullable=True)
    priority = Column(Boolean, nullable=True)  # can someone confirm this is a boolean? i forgot what this was
    current_shift = Column(Boolean, nullable=True)
    num_patients = Column(Integer, nullable=True)

    def __init__(self, id: int, name: str, clinical_area: str, bed_num: int,
                 rotation: str, group: int, fte: float, skill_level: int, a_trained: int, transfer: int, picc: int,
                 advanced_role: str, previous_patients: str, dta: str, comments: str, priority: int,
                 current_shift: int) -> None:
        """ Validates and Initializes a Nurse """
        # Nurse._validate_positive_integer("Nurse ID", id)
        self.id = id

        # Nurse._validate_string_250("Name", name)
        self.name = name

        # Nurse._validate_string_250("Clinical area", clinical_area)
        self.clinical_area = clinical_area

        # Nurse._validate_positive_integer("Bed number", bed_num)
        self.bed_num = bed_num

        # Nurse._validate_string_250("Rotation", rotation)
        self.rotation = rotation

        # Nurse._validate_positive_integer("Group", group)
        self.group = group

        # Nurse._validate_positive_float("fte", fte)
        self.fte = fte

        # Nurse._validate_positive_integer("Skill level", skill_level)
        self.skill_level = skill_level

        # Nurse._validate_boolean("A-Trained value", a_trained)
        self.a_trained = a_trained

        # Nurse._validate_boolean("Transfer value", transfer)
        self.transfer = transfer

        # Nurse._validate_boolean("PICC value", picc)
        self.picc = picc

        # Nurse._validate_string_250("Advanced Role", advanced_role)
        self.advanced_role = advanced_role

        # Nurse._validate_string_250("Previous Patients", previous_patients)
        self.previous_patients = previous_patients

        # Nurse._validate_string_250("dta", dta)
        self.dta = dta

        # Nurse._validate_string_250("Comments", comments)
        # self.comments = comments

        # Nurse._validate_boolean("Priority/Non-Priority", priority)
        self.priority = priority

        # Nurse._validate_boolean("Current Shift", current_shift)
        self.current_shift = current_shift

    ###############################################
    #                Public Methods               #
    ###############################################

    # ---------------------------------------------#
    #                   GETTERS                   #
    # ---------------------------------------------#
    def get_id(self) -> int:
        """ get id of nurse """
        return self.id

    def get_name(self) -> str:
        """ get first name of nurse """
        return self.name

    def get_clinical_area(self) -> str:
        """ get clinical area that nurse is currently assigned """
        return self.clinical_area

    def get_bed_num(self) -> int:
        """ get bed number that nurse is currently assigned """
        return self.bed_num

    def get_skill_level(self) -> int:
        """ get skill level that nurse is currently assigned """
        return self.skill_level

    def get_a_trained(self) -> int:
        """ get a_trained value from nurse"""
        return self.a_trained

    def get_transfer(self) -> int:
        """ get transfer value from nurse"""
        return self.transfer

    def get_picc(self) -> int:
        """ get PICC value from nurse"""
        return self.picc

    def get_rotation(self) -> str:
        """ get rotation value from nurse"""
        return self.rotation

    def get_fte(self) -> float:
        """ get fte value from nurse"""
        return self.fte

    def get_assigned(self) -> int:
        """ get assigned value from nurse"""
        return self.assigned

    def get_previous_patients(self) -> str:
        """ get previous patients from nurse"""
        return self.previous_patients

    def get_dta(self) -> str:
        """ get dta value from nurse"""
        return self.dta

    def get_priority(self) -> int:
        """ get priority value from nurse"""
        return self.priority

    def get_current_shift(self) -> int:
        """ get current shift value from nurse"""
        return self.current_shift

    def get_advanced_role(self) -> str:
        """ get advanced role value from nurse"""
        return self.advanced_role

    def get_group(self) -> int:
        """get group number from nurse"""
        return self.group

    # ---------------------------------------------#
    #                  SETTERS                    #
    # ---------------------------------------------#

    def set_assigned(self, assigned):
        """set if the nurse is assigned"""
        self.assigned = assigned


    ###############################################
    #                Public Methods               #
    ###############################################
    def to_dict(self) -> dict:
        """ Returns nurse information in a dictionary """
        nurse_dict = {}

        nurse_dict['id'] = self.id
        nurse_dict['name'] = self.name
        nurse_dict['clinical_area'] = self.clinical_area
        nurse_dict['bed_num'] = self.bed_num
        nurse_dict['rotation'] = self.rotation
        nurse_dict['fte'] = self.fte
        nurse_dict['group'] = self.group
        nurse_dict['skill_level'] = self.skill_level
        nurse_dict['a_trained'] = self.a_trained
        nurse_dict['transfer'] = self.transfer
        nurse_dict['picc'] = self.picc
        nurse_dict['advanced_role'] = self.advanced_role
        nurse_dict['previous_patients'] = self.previous_patients
        nurse_dict['dta'] = self.dta
        nurse_dict['comments'] = self.comments
        nurse_dict['priority'] = self.priority
        nurse_dict['current shift'] = self.current_shift
        nurse_dict['assigned'] = self.assigned

        return nurse_dict

    ###############################################
    #              Validator Methods              #
    ###############################################
    @staticmethod
    def _validate_string_250(input_value: str, str_value: str) -> None:
        """ Checks if input is string """
        if not isinstance(str_value, str):
            raise ValueError(input_value + " is not a string.")
        if (str_value == "") or (str_value is None):
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

    @staticmethod
    def _validate_positive_float(input_value: str, float_value: float) -> None:
        """ Checks if input is integer and not negative """
        if not isinstance(float_value, float):
            raise ValueError(input_value + " is not a float.")
        if float_value is None:
            raise ValueError(input_value + " cannot be empty.")
        if float_value < 0:
            raise ValueError(input_value + " cannot be negative.")

    @staticmethod
    def _validate_boolean(input_value: str, bool_value: bool) -> None:
        """ Checks if input is boolean """
        if not isinstance(bool_value, bool):
            raise ValueError(input_value + " is not a boolean.")
        if bool_value is None:
            raise ValueError(input_value + " cannot be empty.")
