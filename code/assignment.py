from nurse import Nurse
from patient import Patient


def main_assign(cursor) -> dict:
    """ Driver function of assignment"""
    # Store assignments in a dict
    assignments = {}

    # Used to pair twins with the same nurse
    twins = []

    # Grab all patients that aren't discharged
    patients = []
    patients, twins = grab_patients(patients, cursor, twins)

    # Grab all nurses that are currently on shift
    nurses = []
    nurses, assignments = grab_nurses(nurses, assignments, cursor)

    for p in patients:
        # If patient is not assigned
        if p.get_assigned() == 0:
            # Get patient constraints
            transfer, a_trained, acuity, picc, one_to_one, clinical_area, twin = get_patient_constraints(
                p)
            # Grab all nurses that are "hard constraint eligible" using patient hard constraints
            eligible_nurses = make_and_execute_sql_query(
                acuity, transfer, a_trained, cursor)
            # Turn eligible_nurses into objects
            eligible_nurse_objects, assignments = to_object(
                eligible_nurses, assignments)
            # calculate weights of eligible_nurse_objects
            eligible_max_nurses = calculate_weights(
                eligible_nurse_objects, clinical_area, picc, p, assignments, cursor)
            # Sort eligible_max_nurses
            sorted_eligible_nurses = sort_eligible_nurse_objects_acuity(
                eligible_nurse_objects)
            # Assign and append to assignments dict
            assignments = assign(
                sorted_eligible_nurses, eligible_max_nurses, assignments, one_to_one, p, twin, twins)
    print(assignments)

    # Check if a patient is not set as assigned
    for p in patients:
        if p.get_assigned() != 1:
            print("Patient", p.get_id(), " is not assigned!")

    return assignments


def grab_patients(patients, cursor, twins):
    """ Grabs all patients who haven't been discharged """
    # Get patients who haven't been discharged. Patients that are most in need are prioritized first.
    cursor.execute(
        'SELECT * FROM patients WHERE discharged_date="-" ORDER BY length(previous_nurses) DESC, one_to_one DESC, twin DESC, acuity DESC, a_trained DESC, transfer DESC, iv DESC;')
    patient_list = cursor.fetchall()

    # Turn them into an object
    for row in patient_list:
        x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13])
        patients.append(x)
        # If they have a twin, make a note.
        if row[13] == "1":
            twins.append(x)
    return patients, twins


def grab_nurses(nurses, assignments, cursor):
    """ Grabs all nurses who are currently on shift """
    cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    nurse_list = cursor.fetchall()

    # Turn them into an object
    for row in nurse_list:
        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                  row[12], row[13], row[14], row[15], row[16])
        nurses.append(x)
        # Initialize the assignments dict with all the nurses
        assignments[row[0]] = {'num_patients': 0, 'patients': [], 'prev_p': []}
    return nurses, assignments


def get_patient_constraints(p):
    """ Get all the patient constraints and cache them """
    transfer = p.get_transfer()
    a_trained = p.get_a_trained()
    acuity = p.get_acuity()
    picc = p.get_picc()
    one_to_one = p.get_one_to_one()
    clinical_area = p.get_clinical_area()
    twin = p.get_twin()
    return transfer, a_trained, acuity, picc, one_to_one, clinical_area, twin


def make_and_execute_sql_query(acuity, transfer, a_trained, cursor):
    """ Customize SQL query depending on patient hard constraints"""
    # get nurses that match the hard constraints
    base = "SELECT * FROM nurses WHERE current_shift=1 AND skill_level>=%d" % acuity

    if transfer:
        base += " AND transfer=1"
    if a_trained:
        base += " AND a_trained=1"

    cursor.execute(base)
    eligible_nurses = cursor.fetchall()
    return eligible_nurses


def to_object(eligible_nurses, assignments):
    """ Turn nurses into objects.
        We also consider the amount of patients a nurse has in a while loop here.
        For the very first patient, nurses do not have any patients assigned to them,
        therefore all eligible nurses are considered when it comes to assigning.

        When it comes to near the end of the patients list, we have nurses who have
        already been assigned to a patient. There is a chance that all nurses who
        meet hard constraints are already assigned. If so, we then consider nurses
        who have 1 patient, then 2 patients, and so on up to 3."""
    eligible_nurse_objects = []
    i = 0
    while len(eligible_nurse_objects) < 1 and i < 3:
        for row in eligible_nurses:
            # if nurse assigned
            if row[0] in assignments:
                # if nurse has i patients (we use this if our eligible nurses are all assigned. Then we
                # resort to assigning nurses with more than 1 patient)
                if assignments[row[0]]["num_patients"] == i:
                    x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16])
                    eligible_nurse_objects.append(x)
            # if nurse is not assigned
            elif row[0] not in assignments:
                x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                          row[10], row[11], row[12], row[13], row[14], row[15], row[16])
                eligible_nurse_objects.append(x)
        # for the next iteration, start considering nurses with i += 1 patients.
        if len(eligible_nurse_objects) < 1:
            i += 1
    return eligible_nurse_objects, assignments


def calculate_weights(eligible_nurse_objects, clinical_area, picc, p, assignments, cursor) -> list:
    """ Calculate the soft constraint weight of the nurse """
    nurse_weights = {}
    max_points = 0

    for eno in eligible_nurse_objects:
        # Cache nurse attributes (soft constraint attributes)
        eno_id = eno.get_id()
        eno_area = eno.get_clinical_area()
        eno_picc = eno.get_picc()
        eno_priority = eno.get_priority()
        eno_prev_p = eno.get_previous_patients()

        if eno_id not in nurse_weights:
            nurse_weights[eno_id] = 0

        # if nurse matches clinical area, give nurse 2 points
        if eno_area == clinical_area:
            nurse_weights[eno_id] += 2

        # if nurse matches picc, give nurse 2 points
        if eno_picc == picc:
            nurse_weights[eno_id] += 2

        # if nurse matches priority, give nurse 7 points
        if eno_priority == 1:
            nurse_weights[eno_id] += 7

        # if nurse has previous assignments, give nurse 10 points
        prev_p = eno_prev_p.strip('][').split(', ')

        if prev_p != "[]":
            if str(p.get_id()) in prev_p:
                nurse_weights[eno_id] += 10

        # if secondary patient is in the same clinical area as the nurse's first assigned patient, give 7 points
        # This is so that the nurse can stay in the same area when he/she has more than 2 patients.
        if eno_id in assignments:
            if len(assignments[eno_id]['patients']) > 0:
                first_prev_patient_id = assignments[eno_id]['patients'][0]
                cursor.execute(
                    f"SELECT clinical_area FROM patients WHERE id={first_prev_patient_id}")
                first_prev_patient_pod = cursor.fetchone()
                if p.get_clinical_area() == first_prev_patient_pod[0]:
                    nurse_weights[eno_id] += 7

        # if nurse weight exceeds max points, replace it.
        if nurse_weights[eno_id] > max_points:
            max_points = nurse_weights[eno_id]

    eligible_max_nurses = []

    # take nurses who have the highest points and store them in eligible_max_nurses
    for eno in eligible_nurse_objects:
        eno_id = eno.get_id()
        if nurse_weights[eno_id] == max_points:
            eligible_max_nurses.append(eno_id)
    return eligible_max_nurses


def sort_eligible_nurse_objects_acuity(eligible_nurse_objects):
    """ Sort eligible_nurse_objects by skill level ascending.
        In case we have nurses with the same max weight, we choose
        the nurse with the lowest skill level."""
    sorted_eligible_nurses = sorted(
        eligible_nurse_objects, key=lambda x: x.skill_level, reverse=False)
    return sorted_eligible_nurses


def assign(sorted_eligible_nurses, eligible_max_nurses, assignments, one_to_one, p, twin, twins):
    """ Assign nurse and patient. Special assignments are also considered here."""
    # SEN stands for Sorted Eligible Nurses

    for sen in sorted_eligible_nurses:
        # Initialize assignments dict with chosen nurse
        sen_id = sen.get_id()
        if sen_id in eligible_max_nurses:
            if sen_id not in assignments:
                assignments[sen_id]["num_patients"] = 0
                assignments[sen_id]["patients"] = []

            # If patient has a twin, check if the other twin is also a patient. If so, assign both to the same nurse.
            if twin == "1":
                for twin_object in twins:
                    if p.get_name() == twin_object.get_name():
                        continue
                    elif p.get_last_name() == twin_object.get_last_name():
                        assignments[sen_id]["num_patients"] += 1
                        assignments[sen_id]["patients"].append(
                            twin_object.get_id())
                        twin_object.set_assigned(1)
                        twins.remove(twin_object)
                        twins.remove(p)
                        break

            # If patient is one_to_one, make that nurse unassignable.
            if one_to_one:
                assignments[sen_id]["num_patients"] = 98
            assignments[sen_id]["num_patients"] += 1
            assignments[sen_id]["patients"].append(p.get_id())

            # set patient to be assigned
            p.set_assigned(1)
            return assignments
