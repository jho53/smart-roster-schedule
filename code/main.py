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
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)

    app.run()
