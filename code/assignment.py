from nurse import Nurse
from patient import Patient
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="charge_nurse",
    passwd="Password",
    database="smartroster",
    auth_plugin="mysql_native_password"
)

cursor = db.cursor()

def main():
    patients = grab_patients()
    nurses = grab_nurses()

    assignments = {}

    # Pair previous patient with nurse. Assume that hard constraints are not checked
    for n in nurses:
        prev_p = n.get_previous_patients()
        prev_p_list = prev_p.split(",") # assume that prev_p is a comma separated list of patient IDs

        for p in patients:
            if p.get_id() == prev_p_list[-1]:
                if n.get_id() not in assignments:
                    assignments[n.get_id()]["num_patients"] = 0
                    assignments[n.get_id()]["patients"] = []

                assignments[n.get_id()]["num_patients"] += 1
                assignments[n.get_id()]["patients"].append(p.get_id())
                # set patient to be assigned
                p.set_assigned(True)

    # Get all nurses that are eligible for each patient
    for p in patients:
        if p.get_assigned != True:
            transfer = p.get_transfer()
            a_trained = p.get_a_trained()
            acuity = p.get_acuity()
            picc = p.get_picc()
            one_to_one = p.get_one_to_one()
            clinical_area = p.get_clinical_area()
            twin = p.get_twin()
            priority = p.get_priority()

            # get nurses that match the hard constraints
            sql_query = customize_sql(transfer, a_trained, acuity)
            cursor.execute(sql_query)
            eligible_nurses = cursor.fetchall()
            eligible_nurse_objects = []

            i = 0
            while len(eligible_nurse_objects) < 1 and i < 4:
                for row in eligible_nurses:
                    # if nurse assigned
                    if row[0] in assignments:
                        # if nurse has i patients (we use this if our eligible nurses are all assigned. Then we
                        # resort to assigning nurses with more than 1 patient)
                        if assignments[row[0]]["num_patients"] == i:
                            x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18])
                            eligible_nurse_objects.append(x)
                    # if nurse is not assigned
                    elif row[0] not in assignments:
                        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18])
                        eligible_nurse_objects.append(x)
                # for the next iteration, start considering nurses with i += 1 patients.
                if len(eligible_nurse_objects) < 1:
                    i += 1


            nurse_weights = {}
            max_points = 0


            for eno in eligible_nurse_objects:
                if eno.get_id() not in nurse_weights:
                    nurse_weights[eno.get_id()] = 0

                # if nurse matches clinical area, give nurse 4 points
                if eno.get_clinical_area() == clinical_area:
                    nurse_weights[eno.get_id()] += 4

                # if nurse matches picc, give nurse 3 points
                if eno.get_picc() == picc:
                    nurse_weights[eno.get_id()] += 3

                # if nurse matches priority, give nurse 2 points
                if eno.get_priority() == priority:
                    nurse_weights[eno.get_id()] += 2
                
                if nurse_weights[eno.get_id()] > max_points:
                    max_points = nurse_weights[eno.get_id()]

            eligible_max_nurses = []

            for eno in eligible_nurse_objects:
                if nurse_weights[eno.get_id()] == max_points:
                    eligible_max_nurses.append(eno.get_id())
            
            # algorithm that matches nurse to patient starting from lowest skill level
            sorted_eligible_nurses = sorted(eligible_nurse_objects, key=lambda x: x.skill_level, reverse=False)

            for sen in sorted_eligible_nurses:
                if sen.get_id() in eligible_max_nurses:
                    if sen.get_id() not in assignments:
                        assignments[sen.get_id()]["num_patients"] = 0
                        assignments[sen.get_id()]["patients"] = []

                    assignments[sen.get_id()]["num_patients"] += 1
                    assignments[sen.get_id()]["patients"].append(p.get_id())
                    # set patient to be assigned
                    p.set_assigned(True)

            # We haven't iterated by num_patients yet
            # 1:1 can be overridden when we run out of nurses

            print(eligible_nurses)

def grab_patients():
    patients = []

    cursor.execute("SELECT * FROM patients WHERE current=True")
    patient_list = cursor.fetchall()

    for row in patient_list:
        x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                         row[12], row[13], row[14])
        patients.append(x)
    
    return patients

def grab_nurses():
    nurses = []

    cursor.execute("SELECT * FROM nurses WHERE current=True")
    nurse_list = cursor.fetchall()

    for row in nurse_list:
        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                         row[12], row[13], row[14], row[15], row[16], row[17], row[18])
        nurses.append(x)
    
    return nurses

def customize_sql(transfer, a_trained, acuity):
    base = "SELECT * FROM nurses WHERE current=True AND acuity>=%d" % acuity

    if transfer:
        base += " AND transfer=True"
    if a_trained:
        base += " AND a_trained=True"
    
    return base



# Patient #5
# - transfer - False
# - atrained - True
# - acuity - 3
# - picc - False
# - one-to-one - False
# - clinical area - C
# - twin - 'other person'

# nurses:
# - transfer - doesn't matter
# - atrained - True
# - skill level - 3 or more
# - num_patients - 0
# - clinical area (soft) - B (2)
# - prev_patients - #5, #6, #1 (1)

# iterate by patients
# 1st iteration (num_patients = 0)
#  select statement in current nurses
# 2nd iteration (num_patients = 1)
# 3rd iteration (num_patients = 2)

# SOFT CONSTRAINTS
# clinical area
# 1:1
# picc
# priority