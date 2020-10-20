from nurse import Nurse
from patient import Patient
import json
from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector
import os

# test purpose
import webbrowser


app = Flask(__name__, instance_relative_config=True)
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
        if password == password_conf:
            cursor.execute(
                'INSERT INTO users (username, password, first_name, last_name) '
                'VALUES (%s, md5(%s), %s, %s)', (username,
                                                 password, first_name, last_name)
            )
            db.commit()
            return render_template('mainPage.html', loggedin=session['loggedin'])
        else:
            return render_template('register.html', msg="Passwords do not match", loggedin=session['loggedin'])


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
                'SELECT * FROM users WHERE username = %s AND password = md5(%s)', (
                    username, password,)
            )
            account = cursor.fetchone()
            if account:
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


@app.route("/nurseRecords", methods=["GET"])
def nurse_records():
    # Grabs all nurses
    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()
    return render_template("./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list)


@app.route("/nurseRecordsSubmit", methods=['POST'])
def nurse_records_submit():
    return


@app.route("/patientRecords", methods=["GET"])
def patient_records():
    # Grabs all patients
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template("./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list)


@app.route("/patientRecordsSubmit", methods=['POST'])
def patient_records_submit():
    return


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

    # hard match nurses with patients they've been with (regardless of pod)
    #   In the case of multiple previous patients:
    #       - check skill-level
    #       - check geography (if needed)

    # MBC trained nurses go to "Rabbit Pod" as much as needed

    # Keep a clinical area "empty"

    # split the remaining nurses according to "pod's needs"
    #       - A-trained
    #       - number of patients in a pod
    #       - transfer available for patient who needs it
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
