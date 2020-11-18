import json

flags = {
    'skill_level': 0,
    'a_trained': 0,
    'transfer': 0,
    'twin': 0,
    '1:1': 0,
    'iv': 0,
    'clinical_area': 0,
    'previous_patient': 0,
    'priority': 0
}

assignments = ""

with open("./cache/current_shift/curr_assignment.json", 'r') as jsonfile:
        json.dump(assignments, jsonfile)

curr_assignment = json.loads(assignments)
nurse_id = argument_1
patient_id = argument_2

cursor.execute('SELECT * FROM nurse WHERE nurse_id={0}'.format(nurse_id))
nurse = cursor.fetchall()

cursor.execute('SELECT * FROM patient WHERE patient_id={0}'.format(patient_id))
patient = cursor.fetchall()

cursor.execute('SELECT id FROM nurse WHERE current_shift=1')
nurse_list = cursor.fetchall()

# Flag skill level
if nurse[7] < patient[4]:
    flags['skill_level'] = 1

# Flag A trained
if nurse[8] < patient[5]:
    flags['a_trained'] = 1

# Flag Transfer
if nurse[9] < patient[6]:
    flags['transfer'] = 1

# Flag twin
if patient[13]:
    flags['twin'] = 1

# Flag 1:1
# case 1: current patient is 1:1
if patient[8]:
    if len(curr_assignment[nurse[0]]['patients']) > 1:
        flags['1:1'] = 1
else:
    # case 2: nurse being assigned is already assigned to another 1:1 patient
    for p in curr_assignment[nurse[0]]['patients']:
        cursor.execute('SELECT one_to_one FROM patient WHERE id={0}'.format(p))
        if list(cursor.fetchall())[0]:
            flags['1:1'] = 1

# Flag iv
if nurse[10] < patient[7] + 1:
    flags['iv'] = 1

# Flag clinical area
if nurse[2] != patient[2]:
    flags['clinical_area'] = 1

# Flag previous patient
for n in patient[9].strip('][').split(', '):
    if n in list(nurse_list):
        if nurse[0] != n:
            flags['previous_patient'] = 1

# Get DTA
flags['dta'] = nurse[13]

# Get Comments
flags['comments'] = nurse[14]
