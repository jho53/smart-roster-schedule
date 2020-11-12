from sqlalchemy import Table, Column, Integer, String, Boolean
from base import Base


class Patient(Base):
    """ Represents a patient """

    __tablename__ = "patient"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    clinical_area = Column(String(100), nullable=True)
    bed_num = Column(Integer, nullable=True)
    acuity = Column(Integer, nullable=True)
    a_trained = Column(Boolean, nullable=True)
    transfer = Column(Boolean, nullable=True)
    picc = Column(Boolean, nullable=True)
    one_to_one = Column(Boolean, nullable=True)
    previous_nurses = Column(String(250), nullable=True)
    admission_date = Column(String(250), nullable=True)  # could use datetime
    discharge_date = Column(String(250), nullable=True)  # this as well
    comments = Column(String(250), nullable=True)
    twin = Column(String(250), nullable=True)

    def __init__(self, id: int, name: str, clinical_area: str, bed_num: int,
                 acuity: int, a_trained: int, transfer: int, picc: int, one_to_one: int,
                 previous_nurses: str, admission_date: str, discharge_date: str, comments: str,
                 twin: int) -> None:
        """ Validates and Initializes a Patient """
        Patient._validate_positive_integer("Patient ID", id)
        self.id = id

        Patient._validate_string_250("Name", name)
        self.name = name

        # Patient._validate_string_250("Clinical area", clinical_area)
        self.clinical_area = clinical_area

        Patient._validate_positive_integer("Bed number", bed_num)
        self.bed_num = bed_num

        Patient._validate_positive_integer("Acuity", acuity)
        self.acuity = acuity

        # Patient._validate_boolean("A-Trained value", a_trained)
        self.a_trained = a_trained

        # Patient._validate_boolean("Transfer value", transfer)
        self.transfer = transfer

        # Patient._validate_boolean("1:1 value", one_to_one)
        self.one_to_one = one_to_one

        # Patient._validate_boolean("PICC value", picc)
        self.picc = picc

        # Patient._validate_string_250("Previous Nurses", previous_nurses)
        self.previous_nurses = previous_nurses

        # Patient._validate_string_250("Admission Date", admission_date)
        self.admission_date = admission_date

        # Patient._validate_string_250("Discharge Date", discharge_date)
        self.discharge_date = discharge_date

        # Patient._validate_string_250("Twin", twin)
        self.twin = twin

        self.assigned = 0

    ###############################################
    #                Public Methods               #
    ###############################################

    # ---------------------------------------------#
    #                   GETTERS                   #
    # ---------------------------------------------#
    def get_id(self) -> int:
        """ get id of patient """
        return self.id

    def get_name(self) -> str:
        """ get first name of patient """
        return self.name

    def get_last_name(self) -> str:
        """ get last name of patient """
        return self.name.split(' ')[1]

    def get_clinical_area(self) -> str:
        """ get clinical area that patient is currently assigned """
        return self.clinical_area

    def get_bed_num(self) -> int:
        """ get bed number that patient is currently assigned """
        return self.bed_num

    def get_acuity(self) -> int:
        """ get acuity of the patient """
        return self.acuity

    def get_transfer(self) -> bool:
        """ get transfer value of the patient """
        return self.transfer

    def get_a_trained(self) -> bool:
        """ get a-trained value of the patient """
        return self.a_trained

    def get_one_to_one(self) -> bool:
        """ get 1:1 value of the patient """
        return self.one_to_one

    def get_picc(self) -> bool:
        """ get picc value of the patient """
        return self.picc

    def get_previous_nurses(self) -> str:
        """ get previous nurses that the patient had"""
        return self.previous_nurses

    def get_admission_date(self) -> str:
        """ get admission date of the patient"""
        return self.admission_date

    def get_discharge_date(self) -> str:
        """get discharge date of the patient"""
        return self.discharge_date

    def get_twin(self) -> bool:
        """get twin of the patient"""
        return self.twin
    
    def get_assigned(self) -> int:
        return self.assigned

    # ---------------------------------------------#
    #                  SETTERS                    #
    # ---------------------------------------------#
    # def set_num_nurses(self, num_nurses: int) -> None:
    #     """ set the number of nurses """
    #     self.num_nurses = num_nurses

    def set_previous_nurses(self, previous_nurses) -> None:
        """ set the previous nurses of the patient"""
        self.previous_nurses = previous_nurses
    
    def set_assigned(self, assigned) -> None:
        self.assigned = assigned

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
        patient_dict['a_trained'] = self.a_trained
        patient_dict['transfer'] = self.transfer
        patient_dict['picc'] = self.picc
        patient_dict['one_to_one'] = self.one_to_one
        patient_dict['previous_nurses'] = self.previous_nurses
        patient_dict['admission_date'] = self.admission_date
        patient_dict['discharge_date'] = self.discharge_date
        patient_dict['comments'] = self.comments
        patient_dict['twin'] = self.twin

        return patient_dict

    ###############################################
    #              Validator Methods              #
    ###############################################
    @staticmethod
    def _validate_string_250(input_value: str, str_value: str) -> None:
        """ Checks if input is string with 250 max characters """
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
    def _validate_boolean(input_value: str, bool_value: bool) -> None:
        """ Checks if input is boolean """
        if not isinstance(bool_value, bool):
            raise ValueError(input_value + " is not a boolean.")
        if bool_value is None:
            raise ValueError(input_value + " cannot be empty.")
