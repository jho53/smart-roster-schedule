from flask import Flask
from nurse import Nurse
from patient import Patient
import json

app = Flask(__name__, instance_relative_config=True)


@app.route('/assign', methods=['GET'])
def assign_nurse_patient() -> dict:
    """ Assign nurses to patients"""

    # These nurse and patient objects are hardcoded for now
    nurse_jag = Nurse(1, "Jaguar", "Perlas", "A", 7, 5, 0)
    nurse_eugene = Nurse(2, "Eugene", "lastname", "B", 8, 3, 0)
    nurse_nathan = Nurse(3, "Nathan", "Broyles", "C", 9, 4, 0)
    nurses = {
        nurse_jag.get_id(): [
            nurse_jag.get_name(),
            nurse_jag.get_skill_level(),
            nurse_jag.get_num_patients()
        ],
        nurse_eugene.get_id(): [
            nurse_eugene.get_name(),
            nurse_eugene.get_skill_level(),
            nurse_eugene.get_num_patients()
        ],
        nurse_nathan.get_id(): [
            nurse_nathan.get_name(),
            nurse_nathan.get_skill_level(),
            nurse_nathan.get_num_patients()
        ],
    }

    patient_1 = Patient(1, "patient1", "last", "A", 7, 5, 0)
    patient_2 = Patient(2, "patient2", "last2", "B", 8, 4, 0)
    patient_3 = Patient(3, "patient3", "last3", "c", 9, 3, 0)
    patient_4 = Patient(4, "patient4", "last3", "c", 9, 5, 0)
    patient_5 = Patient(5, "patient5", "last5", "c", 9, 3, 0)
    patients = {
        patient_1.get_id: [
            patient_1.get_name(),
            patient_1.get_acuity(),
            patient_1.get_num_nurses()
        ],
        patient_2.get_id: [
            patient_2.get_name(),
            patient_2.get_acuity(),
            patient_2.get_num_nurses()
        ],
        patient_3.get_id: [
            patient_3.get_name(),
            patient_3.get_acuity(),
            patient_3.get_num_nurses()
        ],
        patient_4.get_id: [
            patient_4.get_name(),
            patient_4.get_acuity(),
            patient_4.get_num_nurses()
        ],
        patient_5.get_id: [
            patient_5.get_name(),
            patient_5.get_acuity(),
            patient_5.get_num_nurses()
        ],
    }

    assignments = {}

    # Match first valid pair
    for i in patients.keys():
        for j in nurses.keys():
            if (nurses[j][2] < 1) and (patients[i][2] < 1):
                if nurses[j][1] >= patients[i][1]:
                    try:
                        assignments[nurses[j][0]] = patients[i][0]
                        nurses[j][2] += 1
                        patients[i][2] += 1
                    except IndexError:
                        assignments["null" + str(i)] = patients[i][0]

    try:
        response = app.response_class(status=200, response=json.dumps(assignments))
    except ValueError as error:
        response = app.response_class(status=400, response=str(error))
        
    return response



if __name__ == "__main__":
    app.run()