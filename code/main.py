from flask import Flask
from nurse import Nurse
from patient import Patient
import json

app = Flask(__name__, instance_relative_config=True)


@app.route('/assign', methods=['GET'])
def assign_nurse_patient() -> dict:
    """ Assign nurses to patients"""
    nurse_jag = Nurse(1, "Jaguar", "Perlas", "A", 7)
    nurse_eugene = Nurse(2, "Eugene", "lastname", "B", 8)
    nurse_nathan = Nurse(3, "Nathan", "Broyles", "C", 9)
    nurses = [nurse_jag.get_name(), nurse_eugene.get_name(), nurse_nathan.get_name()]

    patient_1 = Patient(1, "patient1", "last", "A", 7, 1)
    patient_2 = Patient(2, "patient2", "last2", "B", 8, 1)
    patient_3 = Patient(3, "patient3", "last3", "c", 9, 1)
    patients = [patient_1.get_name(), patient_2.get_name(), patient_3.get_name()]

    assignments = {}
    for i in range(len(nurses)):
        assignments[nurses[i]] = patients[i]

    response = app.response_class(status=200, response=json.dumps(assignments))
    return response



if __name__ == "__main__":
    app.run()