from nurse import Nurse
from patient import Patient
# from assignment import main_assign

from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime

import json
import mysql.connector
import os
import bcrypt

# test purpose
import webbrowser

app = Flask(__name__,
            static_url_path="",
            static_folder="./static",
            instance_relative_config=True)

app.config.update(
    TESTING=True,
    TEMPLATES_AUTO_RELOAD=True
)

app.secret_key = os.urandom(12).hex()

db = mysql.connector.connect(
    host="localhost",
    user="charge_nurse",
    passwd="Password",
    database="smartroster",
    auth_plugin="mysql_native_password"
)

cursor = db.cursor()


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)


#### Global Variables ####
DIRNAME = os.path.dirname(__file__)
# Headers
PATIENT_HEADERS = ["ID", "Name", "Clinical Area", "Bed #", "Acuity Level",
                   "A-trained Req", "Transfer Req", "IV Req", "1:1", "Previous Nurses", "Date Admitted",
                   "Discharged Date", "Comments"]
NURSE_HEADERS = ["ID", "Name", "Clinical Area", "Rotation", "Group", "FTE",
                 "Skill Level", "A Trained", "Transfer", "IV Trained", "Advanced Role", "Previous Patients", "DTA",
                 "Comments"]


# Login and Mainpage


@app.route("/")
def home():
    if 'loggedin' in session:
        curr_nurse_ids = []
        supp_nurse_ids = []
        cn_nurse_ids = []

        # Grab database information
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()

        for nurse in nurse_list:
            if nurse[-1] == 1:
                curr_nurse_ids.append(nurse[0])
                if nurse[11] == "Charge":
                    cn_nurse_ids.append(nurse[0])
                if nurse[11] == "Support":
                    supp_nurse_ids.append(nurse[0])

        return render_template('mainPage.html',
                               loggedin=session['loggedin'],
                               nurseList=nurse_list,
                               patientList=patient_list,
                               currNurseIds=curr_nurse_ids,
                               suppNursesIds=supp_nurse_ids,
                               cnNurseIds=cn_nurse_ids)
    return redirect(url_for('login'))


@app.route("/modalSubmit", methods=["POST"])
def update_current_nurses():
    if "loggedin" in session:
        current_nurses_id = "({0})".format(request.form['current_nurses_list'])

        if list(current_nurses_id)[1] == ",":
            current_nurses_id = current_nurses_id[:1] + current_nurses_id[2:]

        try:
            cursor.execute("UPDATE nurses SET current_shift = 0")
            cursor.execute("UPDATE nurses SET current_shift = 1 WHERE id in {0}".format(
                current_nurses_id))
            db.commit()
            return redirect(url_for('home'))
        except Exception as error:
            print(error)


@app.route("/modalSubmit2", methods=["POST"])
def update_cn_supp():
    if "loggedin" in session:
        support_nurses_id = "({0})".format(request.form['support_nurses_list'])
        charge_nurses_id = "({0})".format(request.form['charge_nurses_list'])

        if list(support_nurses_id)[1] == ",":
            support_nurses_id = support_nurses_id[:1] + support_nurses_id[2:]

        if list(charge_nurses_id)[1] == ",":
            charge_nurses_id = charge_nurses_id[:1] + charge_nurses_id[2:]

        try:
            cursor.execute(
                "UPDATE smartroster.nurses SET advanced_role = '' WHERE current_shift = 1 and advanced_role != 'Code' and advanced_role NOT LIKE 'L%'")
            cursor.execute("UPDATE smartroster.nurses SET advanced_role = 'Support' WHERE id in {0}".format(
                support_nurses_id))
            cursor.execute("UPDATE smartroster.nurses SET advanced_role = 'Charge' WHERE id in {0}".format(
                charge_nurses_id))
            db.commit()
            return redirect(url_for('home'))
        except Exception as error:
            print(error)


@app.route("/register", methods=['GET'])
def register():
    if 'loggedin' in session:
        return render_template('register.html', loggedin=session['loggedin'])
    return redirect(url_for('login'))


@app.route("/registerUser", methods=['POST'])
def register_user():
    if 'username' in request.form and 'first_name' in request.form \
            and 'last_name' in request.form and 'password' in request.form \
            and 'password_conf' in request.form:
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        password_conf = request.form['password_conf']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Username already taken.'
        elif password != password_conf:
            msg = 'Passwords do not match.'
        else:
            encrypted_password = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt())
            cursor.execute(
                'INSERT INTO users (username, password, first_name, last_name) '
                'VALUES (%s, %s, %s, %s)', (username,
                                            encrypted_password, first_name, last_name)
            )
            db.commit()
            return redirect(url_for('home'))
        return render_template('register.html', msg=msg, loggedin=session['loggedin'])


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/loginUser', methods=['POST'])
def login_user():
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Backdoor sign in with charge_nurse
        if username == "charge_nurse" and password == "Password":
            session['loggedin'] = True
            session['id'] = "charge_nurse"
            session['username'] = username
            return redirect(url_for('home'))

        else:
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (username,)
            )

            account = cursor.fetchone()

            if account and bcrypt.checkpw(password.encode(), account[2].encode()):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = username
                return redirect(url_for('home'))
            else:
                return render_template("login.html", msg="Invalid Login")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Records


@app.route("/nurseRecords", methods=["GET"])
def nurse_records():
    if 'loggedin' in session:
        # Grabs all nurses
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()

        return render_template(
            "./Records/nurseRecord.html",
            loggedin=session['loggedin'],
            nurseList=nurse_list,
            nurseHeaders=NURSE_HEADERS
        )
    return redirect(url_for('login'))


@app.route("/addNurseRecords", methods=["POST"])
def add_nurse_records():
    nurse_name = request.form['create_nurse_name']
    nurse_area = request.form['create_nurse_area']
    nurse_rotation = request.form['create_nurse_rotation']
    nurse_group = request.form['create_nurse_group']
    nurse_fte = request.form['create_nurse_fte']
    nurse_skill = request.form['create_nurse_skill']
    nurse_a_trained = request.form['create_nurse_a_trained']
    nurse_transfer = request.form['create_nurse_transfer']
    nurse_iv = request.form['create_nurse_iv']
    nurse_adv_role = request.form['create_nurse_adv_role']
    nurse_prev_pat = request.form['create_nurse_prev_pat']
    nurse_DTA = request.form['create_nurse_DTA']
    nurse_comments = request.form['create_nurse_comments']

    query = "insert into smartroster.nurses(name, clinical_area, rotation, group_num, fte, " \
            " skill_level, a_trained, transfer, iv, advanced_role, previous_patients, dta, comments) " \
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_group,
                 nurse_fte, nurse_skill, nurse_a_trained, nurse_transfer, nurse_iv, nurse_adv_role, nurse_prev_pat,
                 nurse_DTA, nurse_comments)

    try:
        cursor.execute(query, arguments)
        db.commit()


    except Exception as error:
        print(error)

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()
    return render_template("./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list,
                           nurseHeaders=NURSE_HEADERS)


@app.route("/editNurseRecords", methods=["POST"])
def edit_nurse_records():
    nurse_id = request.form['edit_nurse_id']
    nurse_name = request.form['edit_nurse_name']
    nurse_area = request.form['edit_nurse_area']
    nurse_rotation = request.form['edit_nurse_rotation']
    nurse_group = request.form['edit_nurse_group']
    nurse_fte = request.form['edit_nurse_fte']
    nurse_skill = request.form['edit_nurse_skill']
    nurse_a_trained = request.form['edit_nurse_a_trained']
    nurse_transfer = request.form['edit_nurse_transfer']
    nurse_iv = request.form['edit_nurse_iv']
    nurse_adv_role = request.form['edit_nurse_adv_role']
    nurse_prev_pat = request.form['edit_nurse_prev_pat']
    nurse_DTA = request.form['edit_nurse_DTA']
    nurse_comments = request.form['edit_nurse_comments']

    query = "UPDATE smartroster.nurses SET name = %s, clinical_area = %s, rotation = %s, group_num = %s, fte = %s, " \
            " skill_level = %s, a_trained = %s, transfer = %s, iv = %s, advanced_role = %s, previous_patients = %s, dta = %s, comments = %s WHERE id = %s"

    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_group,
                 nurse_fte, nurse_skill, nurse_a_trained, nurse_transfer, nurse_iv, nurse_adv_role, nurse_prev_pat,
                 nurse_DTA, nurse_comments, nurse_id)

    try:
        cursor.execute(query, arguments)
        db.commit()
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        return render_template("./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list,
                               nurseHeaders=NURSE_HEADERS)

    except Exception as error:
        print(error)

    return redirect(url_for('nurse_records'))


@app.route("/deleteNurseRecords", methods=["POST"])
def delete_nurse_records():
    nurse_id = request.form['remove_nurse_id']
    query = "DELETE FROM smartroster.nurses WHERE id = %s" % (nurse_id)

    try:
        cursor.execute(query)
        db.commit()
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        return render_template("./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list,
                               nurseHeaders=NURSE_HEADERS)

    except Exception as error:
        print(error)

    return redirect(url_for('nurse_records'))


@app.route("/patientRecords", methods=["GET"])
def patient_records():
    # Grabs all patients
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template(
        "./Records/patientRecord.html",
        loggedin=session['loggedin'],
        patientList=patient_list,
        patientHeaders=PATIENT_HEADERS
    )


@app.route("/addPatientRecords", methods=["POST"])
def add_patient_records():
    # Checks for required fields

    patient_name = request.form['create_name']
    patient_clinical_area = request.form['create_clinical_area']
    patient_bed = request.form['create_bed_num']
    patient_acuity = request.form['create_acuity']
    patient_a_trained = request.form['create_a_trained']
    patient_transfer = request.form['create_patient_transfer']
    patient_iv = request.form['create_patient_iv']
    patient_one_to_one = request.form['create_patient_one_to_one']
    patient_previous_nurses = request.form['create_patient_previous_nurses']
    patient_date_admitted = request.form['create_patient_date_admitted']
    patient_comments = request.form['create_patient_comments']

    query = "insert into smartroster.patients(name, clinical_area, bed_num, acuity, a_trained, transfer, iv, one_to_one, previous_nurses, admission_date, comments )" \
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    arguments = (patient_name, patient_clinical_area, patient_bed, patient_acuity,
                 patient_a_trained, patient_transfer, patient_iv, patient_one_to_one, patient_previous_nurses,
                 patient_date_admitted, patient_comments)

    try:
        cursor.execute(query, arguments)
        db.commit()

        # Grabs all patients
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()
        return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list,
                               patientHeaders=PATIENT_HEADERS)

    except Exception as error:
        print(error)

    return redirect(url_for('patient_records'))


@app.route("/editPatientRecords", methods=["POST"])
def edit_patient_records():
    # Grabs discharge data so it knows if the patient has been discharged

    patientid = request.form['edit_patient_id']
    patient_name = request.form['edit_name']
    patient_clinical_area = request.form['edit_clinical_area']
    patient_bed = request.form['edit_bed_num']
    patient_acuity = request.form['edit_acuity']
    patient_a_trained = request.form['edit_a_trained']
    patient_transfer = request.form['edit_patient_transfer']
    patient_iv = request.form['edit_patient_iv']
    patient_one_to_one = request.form['edit_patient_one_to_one']
    patient_previous_nurses = request.form['edit_patient_previous_nurses']
    patient_date_admitted = request.form['edit_patient_date_admitted']
    patient_date_discharged = request.form['edit_patient_date_discharge']
    patient_comments = request.form['edit_patient_comments']

    query = "UPDATE smartroster.patients SET name = %s, clinical_area = %s, bed_num = %s, acuity = %s, a_trained = %s, " \
            " transfer = %s, iv = %s, one_to_one = %s, previous_nurses = %s, admission_date = %s, discharged_date = %s, comments = %s WHERE id = %s"

    arguments = (patient_name, patient_clinical_area, patient_bed, patient_acuity, patient_a_trained, patient_transfer,
                 patient_iv, patient_one_to_one, patient_previous_nurses, patient_date_admitted,
                 patient_date_discharged, patient_comments, patientid)

    try:
        cursor.execute(query, arguments)
        db.commit()
        # Grabs all patients
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()
        return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list,
                               patientHeaders=PATIENT_HEADERS)

    except Exception as error:
        print(error)

    return redirect(url_for('patient_records'))


@app.route("/deletePatientRecords", methods=["POST"])
def delete_patient_records():
    # grabs patient id
    patient_id = request.form['remove_patient_id']

    query = "DELETE FROM smartroster.patients WHERE id = %s" % \
            (patient_id)

    try:
        cursor.execute(query)
        db.commit()
        # Grabs all patients

        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()
        return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list,
                               patientHeaders=PATIENT_HEADERS)

    except Exception as error:
        print(error)


@app.route("/patientRecordsSubmit", methods=['POST'])
def patient_records_submit():
    return


# Account


@app.route("/profile", methods=['GET'])
def profile():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE username = %s',
                       (session['username'],))
        account = cursor.fetchone()
        return render_template(
            './Account/profile.html', account=account, loggedin=session['loggedin']
        )
    return redirect(url_for('login'))


@app.route("/settings")
def settings():
    if 'loggedin' in session:
        return render_template("./Account/settings.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


# Assignment Sheets


@app.route("/currentCAASheet")
def current_CAASheet():
    # Grab nurse and patient tables
    cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    nurse_list = cursor.fetchall()
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()

    return render_template("./Assignment Sheets/cur_caaSheet.html", loggedin=session['loggedin'], nurseList=nurse_list,
                           patientList=patient_list)


@app.route("/currentPNSheet")
def current_PNSheet():
    if 'loggedin' in session:
        # Grab nurse and patient tables
        cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
        nurse_list = cursor.fetchall()
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()

    return render_template("./Assignment Sheets/cur_pnSheet.html", loggedin=session['loggedin'], nurseList=nurse_list,
                           patientList=patient_list)


@app.route("/pastCAASheet")
def past_CAASheet():
    if 'loggedin' in session:
        return render_template("./Assignment Sheets/past_caaSheet.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


@app.route("/pastPNSheet")
def past_PNSheet():
    if 'loggedin' in session:
        return render_template("./Assignment Sheets/past_pnSheet.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


@app.route('/assign', methods=['GET'])
def assign_nurse_patient() -> dict:
    """ Assign nurses to patients"""
    assignments = {}
    twins = []

    # Grab Patients
    patients = []
    cursor.execute(
        'SELECT * FROM patients WHERE discharged_date="-" ORDER BY length(previous_nurses) DESC, one_to_one DESC, twin DESC, acuity DESC, a_trained DESC, transfer DESC, iv DESC;')
    patient_list = cursor.fetchall()

    for row in patient_list:
        x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13])
        if row[13]  == "1":
            twins.append(x)
        patients.append(x)

    # Grab Nurses
    nurses = []
    cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    nurse_list = cursor.fetchall()

    for row in nurse_list:
        x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                  row[12], row[13], row[14], row[15], row[16])
        nurses.append(x)

        assignments[row[0]] = {'num_patients': 0, 'patients': [], 'prev_p': []}

    # Get all nurses that are eligible for each patient
    for p in patients:
        if p.get_assigned() == 0:
            transfer = p.get_transfer()
            a_trained = p.get_a_trained()
            acuity = p.get_acuity()
            picc = p.get_picc()
            one_to_one = p.get_one_to_one()
            clinical_area = p.get_clinical_area()
            twin = p.get_twin()

            # get nurses that match the hard constraints
            base = "SELECT * FROM nurses WHERE current_shift=1 AND skill_level>=%d" % acuity

            if transfer:
                base += " AND transfer=1"
            if a_trained:
                base += " AND a_trained=1"

            cursor.execute(base)
            eligible_nurses = cursor.fetchall()
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

            # Calculate soft constraint weights
            nurse_weights = {}
            max_points = 0

            for eno in eligible_nurse_objects:
                if eno.get_id() not in nurse_weights:
                    nurse_weights[eno.get_id()] = 0

                # if nurse matches clinical area, give nurse 2 points
                if eno.get_clinical_area() == clinical_area:
                    nurse_weights[eno.get_id()] += 2

                # if nurse matches picc, give nurse 3 points
                if eno.get_picc() == picc:
                    nurse_weights[eno.get_id()] += 2

                # if nurse matches priority, give nurse 7 points
                if eno.get_priority() == 1:
                    nurse_weights[eno.get_id()] += 7

                # if nurse has previous assignments, give nurse 10 points
                prev_p = eno.get_previous_patients().strip('][').split(', ')
                if prev_p != "[]":
                    if str(p.get_id()) in prev_p:
                        nurse_weights[eno.get_id()] += 10

                # calculate the highest weight a nurse achieved
                if nurse_weights[eno.get_id()] > max_points:
                    max_points = nurse_weights[eno.get_id()]

            eligible_max_nurses = []

            for eno in eligible_nurse_objects:
                if nurse_weights[eno.get_id()] == max_points:
                    eligible_max_nurses.append(eno.get_id())

            # algorithm that matches nurse to patient starting from lowest skill level
            sorted_eligible_nurses = sorted(
                eligible_nurse_objects, key=lambda x: x.skill_level, reverse=False)

            # assign
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
                    break

    # We run through to check for one-to-one and fix appropriately
    print(assignments)

    cursor.execute(
        'SELECT * FROM patients WHERE discharged_date="-"')
    patient_list = cursor.fetchall()

    # Store in cache
    os.mkdir("./cache/current_shift")
    with open("./cache/current_shift/somejson.json", 'w') as jsonfile:
        json.dump(assignments, jsonfile)

    try:
        response = app.response_class(
            status=200, response=json.dumps(assignments))
        return render_template("./assign.html", response=assignments, nurseList=nurse_list, patientList=patient_list)
    except ValueError as error:
        response = app.response_class(status=400, response=str(error))


if __name__ == "__main__":
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)
    app.run()
