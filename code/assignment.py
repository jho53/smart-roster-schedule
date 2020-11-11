from nurse import Nurse
from patient import Patient


def main_assign(cursor):
    assignments = {}
    twins = []

    patients = []
    patients, twins = grab_patients(patients, cursor, twins)

    nurses = []
    nurses, assignments = grab_nurses(nurses, assignments, cursor)

    for p in patients:
        if p.get_assigned() == 0:
            transfer, a_trained, acuity, picc, one_to_one, clinical_area, twin = get_patient_constraints(p)
            eligible_nurses = make_and_execute_sql_query(acuity, transfer, a_trained, cursor)
            eligible_nurse_objects, assignments = to_object(eligible_nurses, assignments)
            eligible_max_nurses = calculate_weights(eligible_nurse_objects, clinical_area, picc, p)
            sorted_eligible_nurses = sort_eligible_nurse_objects_acuity(eligible_nurse_objects)
            assignments = assign(sorted_eligible_nurses, eligible_max_nurses, assignments, one_to_one, p, twin, twins)
    print(assignments)


def grab_patients(patients, cursor, twins):
    cursor.execute(
        'SELECT * FROM patients WHERE discharged_date="-" ORDER BY length(previous_nurses) DESC, one_to_one DESC, twin DESC, acuity DESC, a_trained DESC, transfer DESC, iv DESC;')
    patient_list = cursor.fetchall()

    for row in patient_list:
        x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13])
        patients.append(x)
        if row[13]  == "1":
            twins.append(x)
    return patients, twins


def grab_nurses(nurses, assignments, cursor):
    cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    nurse_list = cursor.fetchall()

    for row in nurse_list:
        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                  row[12], row[13], row[14], row[15], row[16])
        nurses.append(x)
        assignments[row[0]] = {'num_patients': 0, 'patients': [], 'prev_p': []}
    return nurses, assignments


def get_patient_constraints(p):
    transfer = p.get_transfer()
    a_trained = p.get_a_trained()
    acuity = p.get_acuity()
    picc = p.get_picc()
    one_to_one = p.get_one_to_one()
    clinical_area = p.get_clinical_area()
    twin = p.get_twin()
    return transfer, a_trained, acuity, picc, one_to_one, clinical_area, twin


def make_and_execute_sql_query(acuity, transfer, a_trained, cursor):
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


def calculate_weights(eligible_nurse_objects, clinical_area, picc, p):
    nurse_weights = {}
    max_points = 0

    for eno in eligible_nurse_objects:
        if eno.get_id() not in nurse_weights:
            nurse_weights[eno.get_id()] = 0

        # if nurse matches clinical area, give nurse points
        if eno.get_clinical_area() == clinical_area:
            nurse_weights[eno.get_id()] += 2

        # if nurse matches picc, give nurse 3 points
        if eno.get_picc() == picc:
            nurse_weights[eno.get_id()] += 2

        # if nurse has less patients, then give nurse 6 points

        # if nurse matches priority, give nurse points
        if eno.get_priority() == 1:
            nurse_weights[eno.get_id()] += 7

        # if nurse has previous assignments, give nurse points
        prev_p = eno.get_previous_patients().strip('][').split(', ')

        if prev_p != "[]":
            if str(p.get_id()) in prev_p:
                nurse_weights[eno.get_id()] += 10

        if nurse_weights[eno.get_id()] > max_points:
            max_points = nurse_weights[eno.get_id()]

    eligible_max_nurses = []

    for eno in eligible_nurse_objects:
        if nurse_weights[eno.get_id()] == max_points:
            eligible_max_nurses.append(eno.get_id())
    return eligible_max_nurses


def sort_eligible_nurse_objects_acuity(eligible_nurse_objects):
    # algorithm that matches nurse to patient starting from lowest skill level
    sorted_eligible_nurses = sorted(
        eligible_nurse_objects, key=lambda x: x.skill_level, reverse=False)
    return sorted_eligible_nurses


def assign(sorted_eligible_nurses, eligible_max_nurses, assignments, one_to_one, p, twin, twins):
    for sen in sorted_eligible_nurses:
        if sen.get_id() in eligible_max_nurses:
            if sen.get_id() not in assignments:
                assignments[sen.get_id()]["num_patients"] = 0
                assignments[sen.get_id()]["patients"] = []

            if twin == "1":
                for twin_object in twins:
                    if p.get_name() == twin_object.get_name():
                        continue
                    elif p.get_last_name() == twin_object.get_last_name():
                        assignments[sen.get_id()]["num_patients"] += 1
                        assignments[sen.get_id()]["patients"].append(twin_object.get_id())
                        twin_object.set_assigned(1)
                        twins.remove(twin_object)
                        twins.remove(p)
                        break

            if one_to_one:
                assignments[sen.get_id()]["num_patients"] = 98
            assignments[sen.get_id()]["num_patients"] += 1
            assignments[sen.get_id()]["patients"].append(p.get_id())

            # set patient to be assigned
            p.set_assigned(1)
            return assignments


cursor.execute('SELECT * FROM patients WHERE discharged_date="-"')
patient_list = cursor.fetchall()
