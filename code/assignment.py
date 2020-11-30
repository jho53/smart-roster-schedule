from nurse import Nurse
from patient import Patient
import random
import math
import numpy
import time
import matplotlib.pyplot as plt

HIGH_WEIGHT = 0


def main_assign(cursor):
    timer_start = time.time()
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
            eligible_max_nurses = calculate_weights(eligible_nurse_objects, clinical_area, picc, p, assignments, cursor)
            sorted_eligible_nurses = sort_eligible_nurse_objects_acuity(eligible_nurse_objects)
            assignments = assign(sorted_eligible_nurses, eligible_max_nurses, assignments, one_to_one, p, twin, twins)
    assignments = algorithms_main(assignments, cursor)

    # Check if a patient is not set as assigned
    for p in patients:
        if p.get_assigned() != 1:
            print("Patient", p.get_id(), " is not assigned!")

    timer_end = time.time()
    execution_time = timer_end - timer_start
    print("This took:", execution_time, "seconds.")

    return assignments


def grab_patients(patients, cursor, twins):
    cursor.execute(
        'SELECT * FROM patients WHERE discharged_date="-" ORDER BY length(previous_nurses) DESC, one_to_one DESC, twin DESC, acuity DESC, a_trained DESC, transfer DESC, iv DESC;')
    patient_list = cursor.fetchall()

    for row in patient_list:
        x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13])
        patients.append(x)
        if row[13] == "1":
            twins.append(x)
    return patients, twins


def grab_nurses(nurses, assignments, cursor):
    cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    nurse_list = cursor.fetchall()

    for row in nurse_list:
        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                  row[12], row[13], row[14], row[15], row[16])
        nurses.append(x)
        assignments[row[0]] = {'num_patients': 0, 'patients': []}
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


def calculate_weights(eligible_nurse_objects, clinical_area, picc, p, assignments, cursor):
    nurse_weights = {}
    max_points = 0

    for eno in eligible_nurse_objects:
        eno_id = eno.get_id()
        eno_area = eno.get_clinical_area()
        eno_picc = eno.get_picc()
        eno_priority = eno.get_priority()
        eno_prev_p = eno.get_previous_patients()

        if eno_id not in nurse_weights:
            nurse_weights[eno_id] = 0

        # if nurse matches clinical area, give nurse points
        if eno_area == clinical_area:
            nurse_weights[eno_id] += 2

        # if nurse matches picc, give nurse 3 points
        if eno_picc == picc:
            nurse_weights[eno_id] += 2

        # if nurse matches priority, give nurse points
        if eno_priority == 1:
            nurse_weights[eno_id] += 7

        # if nurse has previous assignments, give nurse points
        prev_p = eno_prev_p.strip('][').split(', ')

        if prev_p != "[]":
            if str(p.get_id()) in prev_p:
                nurse_weights[eno_id] += 10

        # if secondary patient is in the same clinical area as the nurse's first assigned patient, give 7 points
        # This is so that the nurse can stay in the same area when he/she has more than 2 patients.
        if eno_id in assignments:
            if len(assignments[eno_id]['patients']) > 0:
                first_prev_patient_id = assignments[eno_id]['patients'][0]
                cursor.execute(f"SELECT clinical_area FROM patients WHERE id={first_prev_patient_id}")
                first_prev_patient_pod = cursor.fetchone()
                if p.get_clinical_area() == first_prev_patient_pod[0]:
                    nurse_weights[eno_id] += 7

        if nurse_weights[eno_id] > max_points:
            max_points = nurse_weights[eno_id]

    eligible_max_nurses = []

    global HIGH_WEIGHT
    HIGH_WEIGHT += max_points

    for eno in eligible_nurse_objects:
        eno_id = eno.get_id()
        if nurse_weights[eno_id] == max_points:
            eligible_max_nurses.append(eno_id)
    return eligible_max_nurses


def sort_eligible_nurse_objects_acuity(eligible_nurse_objects):
    # algorithm that matches nurse to patient starting from lowest skill level
    sorted_eligible_nurses = sorted(
        eligible_nurse_objects, key=lambda x: x.skill_level, reverse=False)
    return sorted_eligible_nurses


def assign(sorted_eligible_nurses, eligible_max_nurses, assignments, one_to_one, p, twin, twins):
    for sen in sorted_eligible_nurses:
        sen_id = sen.get_id()
        if sen_id in eligible_max_nurses:
            if sen_id not in assignments:
                assignments[sen_id]["num_patients"] = 0
                assignments[sen_id]["patients"] = []

            if twin == "1":
                for twin_object in twins:
                    if p.get_name() == twin_object.get_name():
                        continue
                    elif p.get_last_name() == twin_object.get_last_name():
                        assignments[sen_id]["num_patients"] += 1
                        assignments[sen_id]["patients"].append(twin_object.get_id())
                        twin_object.set_assigned(1)
                        twins.remove(twin_object)
                        twins.remove(p)
                        break

            if one_to_one:
                assignments[sen_id]["num_patients"] = 98
            assignments[sen_id]["num_patients"] += 1
            assignments[sen_id]["patients"].append(p.get_id())

            # set patient to be assigned
            p.set_assigned(1)
            return assignments


#####################################################################################

def algorithms_main(assignments, cursor):
    assignments_short = {}
    assignments_og = {}
    assignments2 = {}
    # nurse_objects = {}
    # patient_objects = {}
    for i in assignments:
        # nurse_objects[i] = to_object_nurse(i, cursor)
        assignments_short[i] = assignments[i]['patients']
        # for p in assignments_short[i]:
        #     patient_objects[p] = to_object_patient(p, cursor)
        assignments_og[i] = assignments[i]['patients']
    assignments, x_points, y_points = simulated_annealing(assignments_short, cursor, assignments_og)
    # gwo(assignments_short, cursor, assignments_og)
    for i in assignments:
        assignments2[i] = {'num_patients': 0, 'patients': []}
        assignments2[i]['num_patients'] = 0
        assignments2[i]['patients'] = assignments[i]
    # print(len(nurse_objects))
    # print(len(patient_objects))
    make_graph(x_points, y_points)
    return assignments2
    # return assignments


def simulated_annealing(assignments_short, cursor, assignments):
    assignments_short2 = assignments_short
    highest_weight = calculate_total_weight(assignments_short, cursor)
    x_points = []
    y_points = []
    # num_iterations = 150
    start_temp = 30000
    cooling_rate = 0.95
    best_weight = 0
    counter = 0
    best_assignment = {}
    # for i in range(num_iterations):
    while start_temp > 0.1:
        rand_a = 0
        rand_b = 0
        previous_a = 0
        previous_b = 0
        valid = False
        while not valid:
            valid = True
            rand_a = list(assignments_short.keys())[random.randint(1, len(assignments_short)) - 1]
            rand_b = list(assignments_short.keys())[random.randint(1, len(assignments_short)) - 1]
            nurse_a = to_object_nurse(rand_a, cursor)
            nurse_b = to_object_nurse(rand_b, cursor)
            previous_a = assignments_short[rand_a]
            previous_b = assignments_short[rand_b]
            assignments_short2.update({rand_a: assignments_short[rand_b]})
            assignments_short2.update({rand_b: previous_a})
            if not check_hard_constraints(nurse_a, assignments_short[rand_a], cursor):
                assignments_short2.update({rand_a: previous_a})
                assignments_short2.update({rand_b: previous_b})
                valid = False
            if valid:
                if not check_hard_constraints(nurse_b, assignments_short[rand_b], cursor):
                    assignments_short2.update({rand_a: previous_a})
                    assignments_short2.update({rand_b: previous_b})
                    valid = False
            # print('previous a', previous_a)
            # print('previous b', previous_b)
        current_weight = calculate_total_weight(assignments_short2, cursor)
        if current_weight > highest_weight:
            highest_weight = current_weight
            assignments_short = assignments_short2
        elif (math.exp(current_weight - highest_weight) / start_temp) < random.random():
            assignments_short2.update({rand_a: previous_a})
            assignments_short2.update({rand_b: previous_b})
        elif (math.exp(current_weight - highest_weight) / start_temp) > random.random():
            assignments_short = assignments_short2
        start_temp *= cooling_rate
        total_weight = calculate_total_weight(assignments_short2, cursor)
        if total_weight > best_weight:
            best_weight = total_weight
            best_assignment = assignments_short2
        x_points.append(counter)
        y_points.append(total_weight)
        # print('----------')
        # print(calculate_total_weight(assignments_short2, cursor))
        # print(assignments_short2)
        # print('original:')
        # print(assignments)
        print(start_temp)
        counter += 1
    print("Best weight found:", best_weight)
    print("Best assignment:")
    print(best_assignment)
    print('original:')
    print(assignments)
    print("iterations:", counter)
    return best_assignment, x_points, y_points

def make_graph(x, y):
    plt.plot(x,y)
    plt.xlabel('Iterations')
    plt.ylabel('Fitness Score (Higher is better)')
    plt.title('Simulated Annealing Results')
    plt.show()


def gwo(assignments_short, cursor, assignments):
    # Max_iter=1000
    # lb=-100
    # ub=100
    # dim=30
    # SearchAgents_no=5

    Alpha_pos, Beta_pos, Delta_pos = find_best_nurses(assignments_short, cursor)
    print(Alpha_pos, Beta_pos, Delta_pos)

    # initialize alpha, beta, and delta_pos
    # Alpha_pos = numpy.zeros(dim)
    # Alpha_score = float("inf")
    #
    # Beta_pos = numpy.zeros(dim)
    # Beta_score = float("inf")
    #
    # Delta_pos = numpy.zeros(dim)
    # Delta_score = float("inf")
    #
    # if not isinstance(lb, list):
    #     lb = [lb] * dim
    # if not isinstance(ub, list):
    #     ub = [ub] * dim
    #
    # # Initialize the positions of search agents
    # Positions = numpy.zeros((SearchAgents_no, dim))
    # for i in range(dim):
    #     Positions[:, i] = numpy.random.uniform(0, 1, SearchAgents_no) * (ub[i] - lb[i]) + lb[i]
    #
    # Convergence_curve = numpy.zeros(Max_iter)
    # s = solution()
    #
    # # Loop counter
    # print("GWO is optimizing  \"" + objf.__name__ + "\"")
    #
    # timerStart = time.time()
    # s.startTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    # # Main loop
    # for l in range(0, Max_iter):
    #     for i in range(0, SearchAgents_no):
    #
    #         # Return back the search agents that go beyond the boundaries of the search space
    #         for j in range(dim):
    #             Positions[i, j] = numpy.clip(Positions[i, j], lb[j], ub[j])
    #
    #         # Calculate objective function for each search agent
    #         fitness = objf(Positions[i, :])
    #
    #         # Update Alpha, Beta, and Delta
    #         if fitness < Alpha_score:
    #             Delta_score = Beta_score  # Update delte
    #             Delta_pos = Beta_pos.copy()
    #             Beta_score = Alpha_score  # Update beta
    #             Beta_pos = Alpha_pos.copy()
    #             Alpha_score = fitness;  # Update alpha
    #             Alpha_pos = Positions[i, :].copy()
    #
    #         if (fitness > Alpha_score and fitness < Beta_score):
    #             Delta_score = Beta_score  # Update delte
    #             Delta_pos = Beta_pos.copy()
    #             Beta_score = fitness  # Update beta
    #             Beta_pos = Positions[i, :].copy()
    #
    #         if (fitness > Alpha_score and fitness > Beta_score and fitness < Delta_score):
    #             Delta_score = fitness  # Update delta
    #             Delta_pos = Positions[i, :].copy()
    #
    #     a = 2 - l * ((2) / Max_iter);  # a decreases linearly fron 2 to 0
    #
    #     # Update the Position of search agents including omegas
    #     for i in range(0, SearchAgents_no):
    #         for j in range(0, dim):
    #             r1 = random.random()  # r1 is a random number in [0,1]
    #             r2 = random.random()  # r2 is a random number in [0,1]
    #
    #             A1 = 2 * a * r1 - a;  # Equation (3.3)
    #             C1 = 2 * r2;  # Equation (3.4)
    #
    #             D_alpha = abs(C1 * Alpha_pos[j] - Positions[i, j]);  # Equation (3.5)-part 1
    #             X1 = Alpha_pos[j] - A1 * D_alpha;  # Equation (3.6)-part 1
    #
    #             r1 = random.random()
    #             r2 = random.random()
    #
    #             A2 = 2 * a * r1 - a;  # Equation (3.3)
    #             C2 = 2 * r2;  # Equation (3.4)
    #
    #             D_beta = abs(C2 * Beta_pos[j] - Positions[i, j]);  # Equation (3.5)-part 2
    #             X2 = Beta_pos[j] - A2 * D_beta;  # Equation (3.6)-part 2
    #
    #             r1 = random.random()
    #             r2 = random.random()
    #
    #             A3 = 2 * a * r1 - a;  # Equation (3.3)
    #             C3 = 2 * r2;  # Equation (3.4)
    #
    #             D_delta = abs(C3 * Delta_pos[j] - Positions[i, j]);  # Equation (3.5)-part 3
    #             X3 = Delta_pos[j] - A3 * D_delta;  # Equation (3.5)-part 3
    #
    #             Positions[i, j] = (X1 + X2 + X3) / 3  # Equation (3.7)
    #
    #     Convergence_curve[l] = Alpha_score;
    #
    #     if (l % 1 == 0):
    #         print(['At iteration ' + str(l) + ' the best fitness is ' + str(Alpha_score)]);
    #
    # timerEnd = time.time()
    # s.endTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    # s.executionTime = timerEnd - timerStart
    # s.convergence = Convergence_curve
    # s.optimizer = "GWO"
    # s.objfname = objf.__name__
    #
    # return s


#####################################################################################
# def swap(assignments, cursor):
#     temp_assignments = {}
#     temp_assignments2 = {}
#     # print(HIGH_WEIGHT)
#     temp_high_weight = 0
#
#     cursor.execute("SELECT * FROM patients WHERE discharged_date='-'")
#     patient_list = cursor.fetchall()
#     patients = []
#     for row in patient_list:
#         x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
#                     row[12], row[13])
#         patients.append(x)
#     cursor.execute("SELECT * from nurses where current_shift=1")
#     nurse_list = cursor.fetchall()
#     nurses = []
#     for row in nurse_list:
#         x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
#                   row[10], row[11], row[12], row[13], row[14], row[15], row[16])
#         nurses.append(x)
#
#     for i in assignments:
#         temp_assignments[i] = assignments[i]['patients']
#         # rand = random.randint(1, len(assignments))
#         # cursor.execute(f"SELECT * from nurses where id={rand}")
#         # nurse_obj = cursor.fetchone()
#     print(calculate_total_weight(temp_assignments, cursor))
#     print(temp_assignments)
#     print('------------')
#
#
#
#     # possible_combinations = []
#     o = 0
#     while o < 10:
#         weights = {}
#         temp_assignments2 = {}
#         for i in temp_assignments:
#             # if o < 1:
#             #     temp_assignments2[i] = [99]
#             #     continue
#             # temp_high_weight = 0
#             # cursor.execute(f"SELECT * from nurses where id={i}")
#             # row = cursor.fetchone()
#             # xx = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
#             #           row[10], row[11], row[12], row[13], row[14], row[15], row[16])
#             # for p_index in range(len(temp_assignments[i])):
#             #     p = temp_assignments[i][p_index]
#             #     cursor.execute(f"SELECT * from patients where id={p}")
#             #     row = cursor.fetchone()
#             #     xp = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],row[11],
#             #                 row[12], row[13])
#                 # temp_high_weight += calculate_weight(x, xp, temp_assignments, cursor)
#             for j in temp_assignments:
#                 _break = ''
#                 temp_list = {}
#                 rand = random.randint(1, len(temp_assignments))
#                 temp_high_weight2 = 0
#                 if i == j:
#                     continue
#                 try:
#                     if temp_assignments[j] in list(temp_assignments2.values()):
#                         continue
#                 except:
#                     print()
#                 temp_list[i] = temp_assignments[j]
#                 # possible_combinations.append(temp_assignments2)
#                 cursor.execute(f"select * from nurses where id={j}")
#                 row = cursor.fetchone()
#                 x = to_object_nurse(row)
#                 for p in temp_list[i]:
#                     cursor.execute(f"SELECT * from patients where id={p}")
#                     row = cursor.fetchone()
#                     xp = to_object_patient(row)
#                     # if (x.get_skill_level() < xp.get_acuity()) or (x.get_a_trained() < xp.get_a_trained()) or (x.get_transfer() < xp.get_transfer()):
#                     #     temp_assignments2[i] = []
#                     if (x.get_skill_level() >= xp.get_acuity()) and (x.get_a_trained() >= xp.get_a_trained()) and (x.get_transfer() >= xp.get_transfer()):
#                         temp_assignments2[i] = temp_assignments[j]
#                         _break = True
#                         # _break = True
#                         # try:
#                         #     weight = weights[x.get_id()]
#                         #     replacement = calculate_weight(xx, xp, temp_assignments2, cursor)
#                         #     if replacement > weight:
#                         #         temp_assignments2[i] = temp_assignments[j]
#                         # except:
#                         #     weight = calculate_weight(xx, xp, temp_assignments2, cursor)
#                         #     weights[x.get_id()] = weight
#                         #     temp_assignments2[i] = temp_assignments[j]
#                     #
#                     else:
#                         # if temp_assignments[i] in list(temp_assignments2.values()):
#                         #     continue
#                         temp_assignments2[i] = temp_assignments[i]
#                 if _break == True:
#                     break
#                 # except:
#                 #     continue
#
#                 # temp_high_weight2 += calculate_weight(x, xp, temp_assignments2, cursor)
#                 # print(temp_high_weight2, temp_high_weight, "aaaaaaaaaaa")
#                 # if temp_high_weight2 < temp_high_weight:
#                 #     del temp_assignments2[i]
#             #temp_assignments2[rand] = temp_assignments[i]
#         # if o > 1:
#         temp_assignments = temp_assignments2
#
#         temp_high_weight = calculate_total_weight(temp_assignments, cursor)
#         print(temp_high_weight)
#         print(temp_assignments)
#         o += 1
#     # for k in possible_combinations:
#     #     print(k)
#
#     # temp_high_weight = calculate_total_weight(temp_assignments2, cursor)
#     # print(temp_high_weight)
#     # print(temp_assignments2)
#
#     ########brute force#########
#     # i = 0
#     # weights = {}
#     # while i < 10:
#     #     for n in nurses:
#     #         temp_high_weight = 0
#     #         for p in patients:
#     #             temp_high_weight2 = 0
#     #             if i > 0:
#     #                 x = []
#     #                 x.append(p.get_id())
#     #                 if x in list(temp_assignments2.values()):
#     #                     continue
#     #             if (n.get_skill_level() < p.get_acuity()) or (n.get_a_trained() < p.get_a_trained()) or (n.get_transfer() < p.get_transfer()):
#     #                 continue
#     #             temp_high_weight2 = calculate_weight(n, p, temp_assignments2, cursor)
#     #             # print(temp_high_weight2, 'vs', temp_high_weight)
#     #             if i > 0:
#     #                 # print(temp_high_weight2, 'vs', weights[n.get_id()])
#     #                 if temp_high_weight2 > weights[n.get_id()]:
#     #                     temp_high_weight = temp_high_weight2
#     #                     temp_assignments2[n.get_id()] = []
#     #                     temp_assignments2[n.get_id()].append(p.get_id())
#     #                     weights[n.get_id()] = temp_high_weight2
#     #                     # print('assssignnnneeedd')
#     #             elif i == 0:
#     #                 temp_high_weight = temp_high_weight2
#     #                 temp_assignments2[n.get_id()] = []
#     #                 temp_assignments2[n.get_id()].append(p.get_id())
#     #                 weights[n.get_id()] = 0
#     #     i += 1
#     #     print(weights)
#     #     total_weight = calculate_total_weight(temp_assignments2, cursor)
#     #     print('iteration', i, 'wieght', total_weight)
#     #     print(temp_assignments2)

# def find_best_nurses(assignments_short, cursor):
#     best_nurses = [0, 0, 0]
#     best_weights = [0, 0, 0]
#     for nurse_id in assignments_short:
#         total_weight = 0
#         nurse = to_object_nurse(nurse_id, cursor)
#         for patient_id in assignments_short[nurse_id]:
#             patient = to_object_patient(patient_id, cursor)
#             total_weight += calculate_weight(nurse, patient, assignments_short, cursor)
#         if total_weight > best_weights[0]:
#             best_weights[0] = total_weight
#             best_nurses[0] = nurse.get_id()
#         elif total_weight > best_weights[1]:
#             best_weights[1] = total_weight
#             best_nurses[1] = nurse.get_id()
#         elif total_weight > best_weights[2]:
#             best_weights[2] = total_weight
#             best_nurses[2] = nurse.get_id()
#
#         print(best_nurses)
#         print(best_weights)
#     return best_nurses[0], best_nurses[1], best_nurses[2]


def check_hard_constraints(nurse, patients, cursor):
    if type(nurse) == int:
        nurse = to_object_nurse(nurse, cursor)
    for patient in patients:
        if type(patient) == int:
            patient = to_object_patient(patient, cursor)
        if (nurse.get_skill_level() >= patient.get_acuity()) and (
                nurse.get_a_trained() >= patient.get_a_trained()) and (nurse.get_transfer() >= patient.get_transfer()):
            # print('nurse id:', nurse.get_id(), 'patient id:', patient.get_id())
            # print(nurse.get_skill_level(), patient.get_acuity())
            # print(nurse.get_a_trained(), patient.get_a_trained())
            # print(nurse.get_transfer(), patient.get_transfer())
            continue
        else:
            # print('false!')
            return False
    return True


def calculate_total_weight(temp_assignments, cursor):
    temp_high_weight = 0
    for i in temp_assignments:
        rand = random.randint(1, len(temp_assignments))
        x = to_object_nurse(i, cursor)
        for p_index in range(len(temp_assignments[i])):
            p = temp_assignments[i][p_index]
            xp = to_object_patient(p, cursor)
            temp_high_weight += calculate_weight(x, xp, temp_assignments, cursor)
    return temp_high_weight


def to_object_nurse(n, cursor):
    cursor.execute(f"SELECT * from nurses where id={n}")
    row = cursor.fetchone()
    x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
              row[10], row[11], row[12], row[13], row[14], row[15], row[16])
    return x


def to_object_patient(p, cursor):
    cursor.execute(f"SELECT * from patients where id={p}")
    row = cursor.fetchone()
    xp = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                 row[12], row[13])
    return xp


def calculate_weight(eno, p, assignments, cursor):
    nurse_weight = 0
    clinical_area = p.get_clinical_area()
    picc = p.get_picc()

    eno_id = eno.get_id()
    eno_area = eno.get_clinical_area()
    eno_picc = eno.get_picc()
    eno_priority = eno.get_priority()
    eno_prev_p = eno.get_previous_patients()

    # if nurse matches clinical area, give nurse points
    if eno_area == clinical_area:
        nurse_weight += 2

    # if nurse matches picc, give nurse 3 points
    if eno_picc == picc:
        nurse_weight += 2

    # if nurse matches priority, give nurse points
    if eno_priority == 1:
        nurse_weight += 7

    # if nurse has previous assignments, give nurse points
    prev_p = eno_prev_p.strip('][').split(', ')

    if prev_p != "[]":
        if str(p.get_id()) in prev_p:
            nurse_weight += 10

    # if secondary patient is in the same clinical area as the nurse's first assigned patient, give 7 points
    # This is so that the nurse can stay in the same area when he/she has more than 2 patients.
    if eno_id in assignments:
        if len(assignments[eno_id]) > 0:
            first_prev_patient_id = assignments[eno_id][0]
            cursor.execute(f"SELECT clinical_area FROM patients WHERE id={first_prev_patient_id}")
            first_prev_patient_pod = cursor.fetchone()
            if p.get_clinical_area() == first_prev_patient_pod[0]:
                nurse_weight += 7
    return nurse_weight
