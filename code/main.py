from nurse import Nurse
from patient import Patient
import json
from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime
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


# Login and Mainpage


@app.route("/")
def home():
    if 'loggedin' in session:
        return render_template('mainPage.html', loggedin=session['loggedin'])
    return redirect(url_for('login'))


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
            encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute(
                'INSERT INTO users (username, password, first_name, last_name) '
                'VALUES (%s, %s, %s, %s)', (username, encrypted_password, first_name, last_name)
            )
            db.commit()
            return render_template("mainPage.html", loggedin=session['loggedin'])
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
            return render_template("mainPage.html", loggedin=session['loggedin'])

        else:
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (username,)
            )

            account = cursor.fetchone()

            if account and bcrypt.checkpw(password.encode(), account[2].encode()):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = username
                return render_template("mainPage.html", loggedin=session['loggedin'])
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
            "./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list
        )
    return redirect(url_for('login'))


@app.route("/nurseRecords", methods=["POST"])
def add_nurse_records():
    if 'nurse_name' in request.form and 'nurse_area' in request.form \
            and 'nurse_rotation' in request.form and 'nurse_fte' in request.form \
            and 'nurse_a_trained' in request.form and 'nurse_skill' in request.form \
            and 'nurse_transfer' in request.form and 'nurse_adv_role' in request.form \
            and 'nurse_restrictions' in request.form and 'nurse_iv' in request.form:
        nurse_name = request.form['nurse_name']
        nurse_area = request.form['nurse_area']
        nurse_rotation = request.form['nurse_rotation']
        nurse_fte = request.form['nurse_fte']
        nurse_a_trained = request.form['nurse_a_trained']
        nurse_skill = request.form['nurse_skill']
        nurse_transfer = request.form['nurse_transfer']
        nurse_adv_role = request.form['nurse_adv_role']
        nurse_restrictions = request.form['nurse_restrictions']
        nurse_iv = request.form['nurse_iv']

    query = "INSERT INTO nurses(" \
            "nurse_name, nurse_area, nurse_rotation, nurse_fte, nurse_a_trained, nurse_skill, " \
            "nurse_transfer, nurse_adv_role, nurse_restrictions, nurse_iv) " \
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    arguments = (
        nurse_name, nurse_area, nurse_rotation, nurse_fte, nurse_a_trained, nurse_skill,
        nurse_transfer, nurse_adv_role, nurse_restrictions, nurse_iv
    )

    try:
        cursor.execute(query, arguments)
        db.commit()

    except Exception as error:
        print(error)

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()

    return render_template(
        "./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list
    )


@app.route("/patientRecords", methods=["GET"])
def patient_records():
    if 'loggedin' in session:
        # Grabs all patients
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()
        print(patient_list)
        return render_template(
            "./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list
        )
    return redirect(url_for('login'))


@app.route("/patientRecords", methods=["POST"])
def add_patient_records():
    if 'patient_name' in request.form and 'patient_bed' in request.form and 'patient_acuity' in request.form and 'patient_date_admitted' in request.form and 'patient_a_trained' in request.form and 'patient_transfer' in request.form:
        patient_name = request.form['patient_name']
        patient_bed = request.form['patient_bed']
        patient_acuity = request.form['patient_acuity']
        patient_date_admitted = request.form['patient_date_admitted']
        patient_a_trained = request.form['patient_a_trained']
        patient_transfer = request.form['patient_transfer']

    query = "insert into smartroster.patients(" \
            "patient_name, patient_bed, patient_acuity, patient_date_admitted, " \
            "patient_a_trained, patient_transfer)" \
            "VALUES (%s,%s,%s,%s,%s,%s)"

    arguments = (
        patient_name, patient_bed, patient_acuity, patient_date_admitted,
        patient_a_trained, patient_transfer
    )

    try:
        cursor.execute(query, arguments)
        db.commit()

    except Exception as error:
        print(error)

    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template(
        "./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list
    )


@app.route("/patientRecordsSubmit", methods=['POST'])
def patient_records_submit():
    return


# Account


@app.route("/profile", methods=['GET'])
def profile():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
        account = cursor.fetchone()
        return render_template(
            './Account/profile.html', account=account, loggedin=session['loggedin']
        )
    return redirect(url_for('login'))


@app.route("/settings")
def settings():
    return render_template("./Account/settings.html", loggedin=session['loggedin'])


# Assignment Sheets


@app.route("/currentCAASheet")
def current_CAASheet():
    return render_template("./Assignment Sheets/cur_caaSheet.html", loggedin=session['loggedin'])


@app.route("/currentPNSheet")
def current_PNSheet():
    return render_template("./Assignment Sheets/cur_pnSheet.html", loggedin=session['loggedin'])


@app.route("/pastCAASheet")
def past_CAASheet():
    return render_template("./Assignment Sheets/past_caaSheet.html", loggedin=session['loggedin'])


@app.route("/pastPNSheet")
def past_PNSheet():
    return render_template("./Assignment Sheets/past_pnSheet.html", loggedin=session['loggedin'])


@app.route('/assign', methods=['GET'])
def assign_nurse_patient() -> dict:
    """ Assign nurses to patients"""

    # nurse_jag = Nurse(1, "Jaguar", "Perlas", "A", 7, 5, 0, True, True)
    # nurses = {
    #     nurse_jag.get_id(): [
    #     ],
    # }

    # patient_1 = Patient(1, "patient1", "last", "A", 7, 5, 0, False)
    # patients = {
    #     patient_1.get_id: [

    #     ],
    # }

    assignments = {}

    # Create "pod" data structure that stores: num_patients, how many transfers, skill level counts, how many a-trained

    pods = {
        "A": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
        "B": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
        "C": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
        "D": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
        "E": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0},
        "F": {"patients": 0, "transfers": 0, "level": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, "a-trained": 0}
    }

    cursor.execute("SELECT * FROM patients")  # We can modularize this. This gets all patients.
    patient_list = cursor.fetchall()
    cursor.execute("SELECT * FROM nurses")  # We can also modularize this.
    nurse_list = cursor.fetchall()

    for row in patient_list:

        pods[row[2][0]]["patients"] += 1  # row[2] points to the bed column in patient list
        # row[2][0] points to the first letter in bed column which is the pod.
        # pods[#][0] points to the num_patients of the pod object.

        pods[row[2][0]]["level"][row[3]] += 1  # Increment skill level counts

        if row[7]:
            pods[row[2][0]]["a-trained"] += 1  # Increment amount of a-trained in pod object if patient needs a-trained
        if row[6]:
            pods[row[2][0]]["transfers"] += 1  # Increment amount of transfers in pod object if patient needs transfer

    print(pods)

    # hard match nurses with patients they've been with (regardless of pod)
    #   In the case of multiple previous patients:
    #       - check skill-level
    #       - check geography (if needed)

    for nurse in nurse_list:
        for patient in patient_list:
            if nurse[2] == patient[2]:
                assignments[nurse[1]] = patient[
                    1]  # this only assigns matching pod and bed. im just going with the test data here LOL

    # MBC trained nurses go to "Rabbit Pod" as much as needed

    for nurse in nurse_list:
        if nurse[9]:
            nurse[3] = 'F'  # Sets nurse pod to MBC clinical area
            nurse[10] = True  # Marks the nurse as assigned

    # split the remaining nurses according to "pod's needs"
    #       - A-trained

    ##################### PSEUDO CODE #########################
    ## Adds nurse to pod with a_trained ##
    # for pod in pods:
    #   count = pod["a_trained"]
    #   for _ in range(count):
    #       for nurse in nurse_list:
    #           if nurse[10] == False and nurse[6] == True:
    #               nurse[3] = pod  # Sets nurse to pod
    #               nurse[10] = True
    ###########################################################

    #       - transfer available for patient who needs it

    ##################### PSEUDO CODE #########################
    ## Adds nurse to pod with transfer ##
    # for pod in pods:
    #   count = pod["transfers"]
    #   for _ in range(count):
    #       for nurse in nurse_list:
    #           if nurse[10] == False and nurse[7] == True:
    #               nurse[3] = pod  # Sets nurse to pod
    #               nurse[10] = True
    ###########################################################

    #       - number of patients in a pod
    #       - Ensure enough skill level per pod
    #       - ensure PICC match

    # Special Role Assignments (note: not assigned to a pod/patient)

    # Assign nurses to patients
    #       - 1:1 (we think) hard constraint
    #       - A-trained match
    #       - Transfer match
    #       - PICC match
    #       - sort by skill level and pair the lower skill-level nurses first

    # Match first valid pair
    # for i in patients.keys():
    #     for j in nurses.keys():
    #         if (nurses[j][2] < 1) and (patients[i][2] < 1):
    #             if nurses[j][1] >= patients[i][1]:
    #                 try:
    #                     assignments[nurses[j][0]] = patients[i][0]
    #                     nurses[j][2] += 1
    #                     patients[i][2] += 1
    #                 except IndexError:
    #                     assignments["null" + str(i)] = patients[i][0]

    try:
        response = app.response_class(status=200, response=json.dumps(assignments))
    except ValueError as error:
        response = app.response_class(status=400, response=str(error))

    return response


if __name__ == "__main__":
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)
    app.run()
