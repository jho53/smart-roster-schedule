from re import template
from nurse import Nurse
from patient import Patient
from assignment import main_assign

from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory

# Utilized for image upload
from werkzeug.utils import secure_filename

from datetime import datetime

import json
import mysql.connector
import os
import bcrypt
import shutil

# test purpose
import webbrowser

UPLOAD_FOLDER = 'static\\images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__,
            static_url_path="",
            static_folder="./static",
            instance_relative_config=True)

# Testing for profile/background image upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    return {'now': datetime.now()}


@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)


@app.context_processor
def inject_pfp():
    pfp = get_user_pfp()
    return {'pfp': pfp}


def get_user_pfp():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
        account = cursor.fetchone()

        filename = account[5]
        pfp = filename

        return pfp

#### Global Variables ####
CURR_DIR = os.path.dirname(__file__)
AREA_LIST = ["A", "B", "C", "D", "E", "F"]
MAX_BED = 14
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
    """ Displays the home page """
    if 'loggedin' in session:
        curr_nurse_ids = []
        supp_nurse_ids = []
        cn_nurse_ids = []
        code_nurse_ids = []
        group_num = []

        cursor.execute("SELECT DISTINCT group_num FROM nurses")
        for i in cursor.fetchall():
            if i[0] == 0:
                pass
            else:
                group_num.append(i[0])

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
                if nurse[11] == "Code":
                    code_nurse_ids.append(nurse[0])

        return render_template('mainPage.html',
                               loggedin=session['loggedin'],
                               nurseList=nurse_list,
                               patientList=patient_list,
                               currNurseIds=curr_nurse_ids,
                               suppNursesIds=supp_nurse_ids,
                               cnNurseIds=cn_nurse_ids,
                               codeNurseIds=code_nurse_ids,
                               groupNum=group_num)
    return redirect(url_for('login'))


@app.route("/updateCurrNurses", methods=["POST"])
def update_current_nurses():
    """ Updates the current nurses """
    try:
        if "loggedin" in session:
            current_nurses_id = "({0})".format(
                request.form['current_nurses_list'])
            fixed = request.form['fixed']
            flex = request.form['flex']

            if list(current_nurses_id)[1] == ",":
                current_nurses_id = current_nurses_id[:1] + \
                    current_nurses_id[2:]

            try:
                cursor.execute("UPDATE nurses SET current_shift = 0")
                cursor.execute("UPDATE nurses SET current_shift = 1 WHERE id in {0}".format(
                    current_nurses_id))
                cursor.execute("UPDATE nurses SET priority = 0")
                cursor.execute(
                    "UPDATE nurses SET priority = 1 WHERE group_num = {0}".format(flex))
                cursor.execute(
                    "UPDATE nurses SET priority = 2 WHERE group_num = {0}".format(fixed))
                db.commit()
                return redirect(url_for('home'))
            except Exception as error:
                return str(error)
                return str(error)
    except:
        return str(Exception)


@app.route("/updateAdvRole", methods=["POST"])
def update_adv_role():
    if "loggedin" in session:
        support_nurses_id = "({0})".format(
            request.form['support_nurses_list'])
        charge_nurses_id = "({0})".format(
            request.form['charge_nurses_list'])
        code_nurses_id = "({0})".format(request.form['code_nurses_list'])

        if list(support_nurses_id)[1] == ",":
            support_nurses_id = support_nurses_id[:1] + \
                support_nurses_id[2:]

        if list(charge_nurses_id)[1] == ",":
            charge_nurses_id = charge_nurses_id[:1] + charge_nurses_id[2:]

        if list(code_nurses_id)[1] == ",":
            code_nurses_id = code_nurses_id[:1] + code_nurses_id[2:]

        try:
            cursor.execute(
                "UPDATE smartroster.nurses SET advanced_role = '' WHERE current_shift = 1 and advanced_role NOT LIKE 'L%'")
            cursor.execute("UPDATE smartroster.nurses SET advanced_role = 'Support' WHERE id in {0}".format(
                support_nurses_id))
            cursor.execute("UPDATE smartroster.nurses SET advanced_role = 'Charge' WHERE id in {0}".format(
                charge_nurses_id))
            cursor.execute("UPDATE smartroster.nurses SET advanced_role = 'Code' WHERE id in {0}".format(
                code_nurses_id))
            db.commit()
            return redirect(url_for('home'))
        except Exception as error:
            return str(error)


@app.route("/register", methods=['GET'])
def register():
    """ Display the register page """
    if 'loggedin' in session:
        return render_template('register.html', loggedin=session['loggedin'])
    return redirect(url_for('login'))


@app.route("/registerUser", methods=['POST'])
def register_user():
    """ Registers the user """
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
            "INSERT INTO users (username, password, first_name, last_name, profile_img) "
            "VALUES (%s, %s, %s, %s, 'base-avatar.png')", (username,
                                    encrypted_password, first_name, last_name)
            )
            db.commit()
            return redirect(url_for('home'))
        return render_template('register.html', msg=msg, loggedin=session['loggedin'])


@app.route('/login', methods=['GET'])
def login():
    """ Displays the login page """
    return render_template("login.html")


@app.route('/loginUser', methods=['POST'])
def login_user():
    """ Logs the user in """
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            'SELECT * FROM users WHERE username = %s', (username,)
        )

        account = cursor.fetchone()

        if account and bcrypt.checkpw(password.encode(), account[2].encode()):
            if account[1] == "charge_nurse":
                session['loggedin'] = True
                session['id'] = "charge_nurse"
                session['username'] = username
                session['name'] = "Administrator"
            else:
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = username
                session['name'] = account[3] + " " + account[4]
            return redirect(url_for('home'))
        else:
            return render_template("login.html", msg="Invalid Login")


@app.route('/logout')
def logout():
    """ Logs the user out """
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Reference modal

@app.context_processor
def inject_reference():

    cursor.execute("SELECT * FROM reference_page")
    reference = cursor.fetchall()
    return dict(get_reference_data=reference)

@app.route("/editReference", methods=["POST"])
def edit_reference():

    clinical_area = request.form['clinical_area']
    rotation = request.form['rotation']
    group_def = request.form['group']
    fte = request.form['fte']
    skill_level = request.form['skill_level']
    a_trained = request.form['a_trained']
    transfer = request.form['transfer']
    iv_trained = request.form['iv_trained']
    dta = request.form['dta']
    advanced_role = request.form['advanced_role']   
    fixed_ = request.form['fixed']
    flexible = request.form['flexible']

    query = "UPDATE smartroster.reference_page SET clinical_area = %s, rotation = %s, group_def = %s, fte = %s, skill_level = %s, " \
            " a_trained = %s, transfer = %s, iv_trained = %s, advanced_role = %s, dta = %s, fixed_ = %s, flexible = %s WHERE id = 1"

    arguments = (clinical_area, rotation, group_def, fte,
                 skill_level, a_trained, transfer, iv_trained, advanced_role, dta, fixed_, flexible)
    
    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        return str(error)
    return redirect(url_for('settings'))




# Records


@app.route("/nurseRecords", methods=["GET"])
def nurse_records():
    """ Displays the nurse records page """
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
    """ Adds nurse to the nurse records """
    nurse_name = request.form['create_nurse_name']
    nurse_area = request.form['create_nurse_area']
    nurse_rotation = request.form['create_nurse_rotation']
    nurse_group = request.form['create_nurse_group']
    nurse_fte = request.form['create_nurse_fte']
    nurse_skill = request.form['create_nurse_skill']
    try:
        nurse_a_trained = request.form['create_a_trained_toggle']
        nurse_a_trained = 1

    except:
        nurse_a_trained = 0

    try:
        nurse_transfer = request.form['create_transfer_toggle']
        nurse_transfer = 1

    except:
        nurse_transfer = 0

    try:
        nurse_iv = request.form['create_iv_toggle']
        nurse_iv = 2

    except:
        nurse_iv = 1

    try:
        L_check_2 = request.form['L_check_2']
        nurse_iv = 3
    except:
        pass

    nurse_adv_role = request.form['create_advanced_role']
    try:
        L_check_1 = request.form['L_check_1']
        L_check_1 = 'L'
        nurse_adv_role = L_check_1 + " " + nurse_adv_role
    except:
        pass

    nurse_DTA = request.form['create_nurse_dta']
    nurse_comments = request.form['create_nurse_comments']

    query = "insert into smartroster.nurses(name, clinical_area, rotation, group_num, fte, " \
            " skill_level, a_trained, transfer, iv, advanced_role, dta, comments) " \
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_group,
                 nurse_fte, nurse_skill, nurse_a_trained, nurse_transfer, nurse_iv, nurse_adv_role,
                 nurse_DTA, nurse_comments)

    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        return str(error)
    return redirect(url_for('nurse_records'))


@app.route("/editNurseRecords", methods=["POST"])
def edit_nurse_records():
    """ Edits the nurse records """
    nurse_id = request.form['edit_nurse_id']
    nurse_name = request.form['edit_nurse_name']
    nurse_area = request.form['edit_nurse_area']
    nurse_rotation = request.form['edit_nurse_rotation']
    nurse_group = request.form['edit_nurse_group']
    nurse_fte = request.form['edit_nurse_fte']
    nurse_skill = request.form['edit_nurse_skill']
    try:
        nurse_a_trained = request.form['edit_a_trained_toggle']
        nurse_a_trained = 1

    except:
        nurse_a_trained = 0

    try:
        nurse_transfer = request.form['edit_transfer_toggle']
        nurse_transfer = 1

    except:
        nurse_transfer = 0

    try:
        nurse_iv = request.form['edit_iv_toggle']
        nurse_iv = 2

    except:
        nurse_iv = 1

    try:
        L_check_4 = request.form['L_check_4']
        nurse_iv = 3
    except:
        pass

    nurse_adv_role = request.form['edit_advanced_role']
    try:
        L_check_3 = request.form['L_check_3']
        L_check_3 = 'L'
        nurse_adv_role = L_check_3 + " " + nurse_adv_role
    except:
        pass

    nurse_DTA = request.form['edit_nurse_dta']
    nurse_comments = request.form['edit_nurse_comments']

    query = "UPDATE smartroster.nurses SET name = %s, clinical_area = %s, rotation = %s, group_num = %s, fte = %s, " \
            " skill_level = %s, a_trained = %s, transfer = %s, iv = %s, advanced_role = %s, dta = %s, comments = %s WHERE id = %s"

    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_group,
                 str(nurse_fte), nurse_skill, nurse_a_trained, nurse_transfer, nurse_iv, nurse_adv_role,
                 nurse_DTA, nurse_comments, nurse_id)

    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        return str(error)
    return redirect(url_for('nurse_records'))


@app.route("/deleteNurseRecords", methods=["POST"])
def delete_nurse_records():
    """ Delete from nurse records """
    nurse_id = request.form['remove_nurse_id']
    query = "DELETE FROM smartroster.nurses WHERE id = %s" % (nurse_id)

    try:
        cursor.execute(query)
        db.commit()
    except Exception as error:
        return str(error)

    return redirect(url_for('nurse_records'))


@app.route("/patientRecords", methods=["GET"])
def patient_records():
    """ Display the patient records page """
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
    """ Add to the patient records """
    # Checks for required fields

    patient_name = request.form['create_patient_name']
    patient_clinical_area = request.form['create_patient_area']
    patient_bed = request.form['create_patient_bed_number']
    patient_acuity = request.form['create_acuity_level']
    try:
        patient_a_trained = request.form['create_a_trained_toggle']
        patient_a_trained = 1

    except:
        patient_a_trained = 0

    try:
        patient_transfer = request.form['create_transfer_toggle']
        patient_transfer = 1

    except:
        patient_transfer = 0

    try:
        patient_iv = request.form['create_iv_toggle']
        patient_iv = 1

    except:
        patient_iv = 0

    try:
        patient_one_to_one = request.form['create_one_to_one_toggle']
        patient_one_to_one = 1

    except:
        patient_one_to_one = 0

    try:
        patient_twin = request.form['create_twin_toggle']
        patient_twin = 1

    except:
        patient_twin = 0

    patient_date_admitted = request.form['create_patient_date_admitted']
    patient_comments = request.form['create_patient_comments']

    query = "insert into smartroster.patients(name, clinical_area, bed_num, acuity, a_trained, transfer, iv, one_to_one, admission_date, comments, twin )" \
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    arguments = (patient_name, patient_clinical_area, patient_bed, patient_acuity,
                 patient_a_trained, patient_transfer, patient_iv, patient_one_to_one,
                 patient_date_admitted, patient_comments, patient_twin)

    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        return str(error)

    return redirect(url_for('patient_records'))


@app.route("/editPatientRecords", methods=["POST"])
def edit_patient_records():
    """ Edit the patient records """
    # Grabs discharge data so it knows if the patient has been discharged

    patientid = request.form['edit_patient_id']
    patient_name = request.form['edit_patient_name']
    patient_clinical_area = request.form['edit_patient_area']
    patient_bed = request.form['edit_patient_bed_number']
    patient_acuity = request.form['edit_acuity_level']
    try:
        patient_a_trained = request.form['edit_a_trained_toggle']
        patient_a_trained = 1

    except:
        patient_a_trained = 0
    try:
        patient_transfer = request.form['edit_transfer_toggle']
        patient_transfer = 1

    except:
        patient_transfer = 0

    try:
        patient_iv = request.form['edit_iv_toggle']
        patient_iv = 1

    except:
        patient_iv = 0

    try:
        patient_one_to_one = request.form['edit_one_to_one_toggle']
        patient_one_to_one = 1

    except:
        patient_one_to_one = 0

    try:
        patient_twin = request.form['edit_twin_toggle']
        patient_twin = 1

    except:
        patient_twin = 0
    patient_date_admitted = request.form['edit_date_admitted']
    patient_date_discharged = request.form['edit_date_discharged']
    patient_comments = request.form['edit_comments']

    query = "UPDATE smartroster.patients SET name = %s, clinical_area = %s, bed_num = %s, acuity = %s, a_trained = %s, " \
            " transfer = %s, iv = %s, one_to_one = %s, admission_date = %s, discharged_date = %s, comments = %s, twin = %s WHERE id = %s"

    arguments = (patient_name, patient_clinical_area, patient_bed, patient_acuity, patient_a_trained, patient_transfer,
                 patient_iv, patient_one_to_one, patient_date_admitted,
                 patient_date_discharged, patient_comments, patient_twin, patientid)

    try:
        cursor.execute(query, arguments)
        db.commit()
    except Exception as error:
        return str(error)

    return redirect(url_for('patient_records'))


@app.route("/deletePatientRecords", methods=["POST"])
def delete_patient_records():
    """ Delete from patient records """
    # grabs patient id
    patient_id = request.form['remove_patient_id']

    query = "DELETE FROM smartroster.patients WHERE id = %s" % \
            (patient_id)

    try:
        cursor.execute(query)
        db.commit()
    except Exception as error:
        return str(error)
    return redirect(url_for('patient_records'))


@app.route("/profile", methods=['GET'])
def profile():
    """ Display the profile page """
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE username = %s',
                       (session['username'],))
        account = cursor.fetchone()
        return render_template(
            './Account/profile.html', account=account, loggedin=session['loggedin']
        )
    return redirect(url_for('login'))


def allowed_file(filename):
    """ Check if the file uploaded is an image file """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_image', methods=['POST'])
def upload_image():
    """ Upload the profile image """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Remove previous pfp if no one else has it (to reduce storage space needed)
            remove_previous_pfp()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            cursor.execute(
            'UPDATE smartroster.users SET profile_img = %s WHERE username = %s',
            (filename, session['username'],))
            db.commit()
            return redirect(url_for('profile',
                                    filename=filename))
    return redirect(url_for('profile'))


def remove_previous_pfp():
    """ Removes previous profile picture if no other user has it """
    cursor.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
    account = cursor.fetchone()

    current_pfp = account[5]

    if current_pfp == 'base-avatar.png':
        return

    cursor.execute('SELECT * FROM users')
    all_nurses = cursor.fetchall()

    exists = False

    for nurse in all_nurses:
        if nurse[5] == current_pfp and nurse[1] != account[1]:
            exists = True

    if os.path.exists(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], current_pfp)) and not exists:
        os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], current_pfp))


@app.route("/changePassword", methods=["POST"])
def change_password():
    if 'loggedin' in session:
        old_password = request.form['oldPassword']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']

        cursor.execute(
            'SELECT * FROM users WHERE username = %s', (session['username'],)
        )

        account = cursor.fetchone()

        if not bcrypt.checkpw(old_password.encode(), account[2].encode()):
            msg = "Old password does not match."
        elif newPassword != confirmPassword:
            msg = "New passwords do not match."
        else:
            encrypted_password = bcrypt.hashpw(
                newPassword.encode(), bcrypt.gensalt())
            cursor.execute(
                'UPDATE users SET password = %s WHERE username = %s', (encrypted_password, session['username'])
            )
            db.commit()
        return redirect(url_for('profile'))


@app.route("/settings")
def settings():
    """ Display the settings page """
    if 'loggedin' in session:
        return render_template("./Account/settings.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


# Assignment Sheets


@app.route("/currentCAASheet")
def current_CAASheet():
    """ Displays the current clinical area page """
    area_nurse_list = []

    if 'loggedin' in session:
        # Grab nurse and patient tables
        cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
        nurse_list = cursor.fetchall()

        # Load most up-to-date state
        if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
            with open("{0}/cache/current_shift/state.json".format(CURR_DIR), 'r') as jsonfile:
                state = json.load(jsonfile)

            # Create 2d array for storing nurse id per area
            for i, area in enumerate(AREA_LIST):
                area_nurse_list.append([])
                for j in range(MAX_BED):
                    # Works only if there is valid nurse inside
                    try:
                        if state[-1]["assignment"][f"{area}{j + 1}"]['n'][0] not in area_nurse_list[i]:
                            area_nurse_list[i].append(
                                int(state[-1]["assignment"][f"{area}{j + 1}"]['n'][0]))
                    except:
                        continue

            return render_template("./Assignment Sheets/cur_caaSheet.html",
                                   loggedin=session['loggedin'],
                                   nurseList=nurse_list,
                                   areaNurseList=area_nurse_list,
                                   state=state[-1])

        return render_template("./Assignment Sheets/cur_caaSheet_blank.html",
                               loggedin=session['loggedin'])

    return redirect(url_for('login'))


@app.route("/futureCAASheet")
def future_CAASheet():
    """ Displays the future clinical area page """

    if 'loggedin' in session:
        # variables
        future_nurse_list = []
        future_json_list = []
        future_states = []

        # Grab nurse and patient tables
        cursor.execute("SELECT * FROM nurses")
        future_nurse_list = cursor.fetchall()

        # Create future_shift folder on first run
        try:
            os.makedirs("{0}/cache/future_shift".format(CURR_DIR))
        except:
            print("Required directories exist")

        # If future_shift directory is empty
        if len(os.listdir(f"{CURR_DIR}/cache/future_shift/")) == 0:
            pass
        # Else store arrays
        else:
            future_json_list = sorted(os.listdir(
                f"{CURR_DIR}/cache/future_shift/"), reverse=True)
            for file in future_json_list:
                with open(f"{CURR_DIR}/cache/future_shift/{file}", "r") as jsonfile:
                    temp_dict = json.load(jsonfile)
                    future_states.append(temp_dict["shift-datetime"])

        return render_template("./Assignment Sheets/future_caaSheet.html",
                               loggedin=session['loggedin'],
                               states=future_states,
                               futureList=future_nurse_list
                               )
    return redirect(url_for('login'))


@app.route("/futureCAASheetState", methods=["POST"])
def future_CAASheet_state():
    """ Displays the future clinical area page """
    future_nurse_list = []

    if 'loggedin' in session:
        # variables
        future_nurse_list = []
        future_json_list = []
        future_states = []
        state = None

        # POST - position of load date json in file array
        selected_date_pos = request.form['date-select']

        # Grab nurse and patient tables
        cursor.execute("SELECT * FROM nurses")
        future_nurse_list = cursor.fetchall()

        # Grab jsons in dir and store states
        future_json_list = sorted(os.listdir(
            f"{CURR_DIR}/cache/future_shift/"), reverse=True)
        for index, file in enumerate(future_json_list):
            with open(f"{CURR_DIR}/cache/future_shift/{file}", "r") as jsonfile:
                temp_dict = json.load(jsonfile)
                future_states.append(temp_dict["shift-datetime"])
            if index == int(selected_date_pos):
                state = temp_dict

        date_time_obj_formatted = state['shift-datetime']
        date_time_obj = datetime.strptime(
            date_time_obj_formatted, "%B %d, %Y - %I:%M:%S %p")

        date = datetime.strftime(date_time_obj, "%Y-%m-%d")
        time = datetime.strftime(date_time_obj, "%H:%M")

        return render_template("./Assignment Sheets/future_caaSheetState.html",
                               currState=state,
                               states=future_states,
                               date=date,
                               time=time,
                               loggedin=session['loggedin'],
                               futureList=future_nurse_list
                               )
    return redirect(url_for('login'))


@app.route("/futureSave", methods=["POST"])
def future_save():
    cursor.execute("SELECT * FROM nurses")
    full_nurse_list = cursor.fetchall()

    if 'loggedin' in session:
        try:
            # POST variables
            date = request.form['shiftDate']
            time = request.form['shiftTime']

            # Convert date-time -> datetime obj -> string
            date_time_obj = datetime.strptime(
                date + " " + time, '%Y-%m-%d %H:%M')
            date_time_obj_formatted = datetime.strftime(
                date_time_obj, "%B %d, %Y - %I:%M:%S %p")
            filename = datetime.strftime(
                date_time_obj, "%Y-%m-%d-%H-%M")

            # Parse request
            future_data = request.form['saveFutureData']
            future_data = future_data.strip('][').split(',')
            future_data = list(filter(('null').__ne__, future_data))

            # init dict
            state_assignment = {
                "charge": [],
                "support": [],
                "code": [],
                "assignment": {},
                "timestamp": datetime.now().strftime("%B %d, %Y - %I:%M:%S %p"),
                "shift-datetime": date_time_obj_formatted,
                "author": session['name'],
                "fixed": "",
                "flex": ""
            }

            # create area key with list
            for area in AREA_LIST:
                state_assignment['assignment'][area] = []

            # clean elements + dict storage
            for i in range(len(future_data)):
                # remove quotation marks
                future_data[i] = future_data[i][1:-1]

                # adv role = <advcode>-"assign"-<nurse id>
                future_data[i] = future_data[i].split('-')

                # adv role states
                if future_data[i][0] == "cn":
                    state_assignment["charge"].append(future_data[i][-1])
                if future_data[i][0] == "sn":
                    state_assignment["support"].append(future_data[i][-1])
                if future_data[i][0] == "code":
                    state_assignment["code"].append(future_data[i][-1])

                # fixed/flex
                if future_data[i][0] == "fixed":
                    state_assignment['fixed'] = future_data[i][-1]
                if future_data[i][0] == "flex":
                    state_assignment['flex'] = future_data[i][-1]

                # append nurse id to corresponding areas
                if future_data[i][0] in AREA_LIST:
                    state_assignment['assignment'][future_data[i][0]].append(
                        future_data[i][-1])

            # Overwrite if future shift json already exists
            if os.path.exists(f"{CURR_DIR}/cache/future_shift/{filename}.json"):
                os.remove(f"{CURR_DIR}/cache/future_shift/{filename}.json")

            with open(f"{CURR_DIR}/cache/future_shift/{filename}.json", "w") as jsonfile:
                json.dump(state_assignment, jsonfile)

            return redirect(url_for('future_CAASheet'))
        except Exception as error:
            return str(error)

    return redirect(url_for('login'))


@app.route("/currentPNSheet")
def current_PNSheet():
    """ Displays the current nurse-patient assignment sheet """
    # Variables
    curr_assignment = None

    if 'loggedin' in session:
        # Grab nurse and patient tables
        cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
        nurse_list = cursor.fetchall()
        cursor.execute("SELECT * FROM patients WHERE discharged_date='-'")
        patient_list = cursor.fetchall()
        cursor.execute("SELECT * FROM nurses")
        full_nurse_list = cursor.fetchall()

        if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
            with open("{0}/cache/current_shift/state.json".format(CURR_DIR), 'r') as jsonfile:
                state = json.load(jsonfile)
            if os.path.exists("{0}/cache/current_shift/flags.json".format(CURR_DIR)):
                with open("{0}/cache/current_shift/flags.json".format(CURR_DIR), 'r') as flagfile:
                    flags = json.load(flagfile)

            return render_template("./Assignment Sheets/cur_pnSheetState.html",
                                   loggedin=session['loggedin'],
                                   state=state[-1],
                                   flags=flags,
                                   nurseList=nurse_list,
                                   patientList=patient_list)
        elif os.path.exists('{0}/cache/current_shift/curr_assignment.json'.format(CURR_DIR)):
            with open('./cache/current_shift/curr_assignment.json', 'r') as jsonfile:
                curr_assignment = json.load(jsonfile)

            print(curr_assignment)

            for nurse_id in curr_assignment:
                print(nurse_id)
                # Advanced Role Assignment
                for nurse in full_nurse_list:
                    if nurse[0] == int(nurse_id):
                        if nurse[11] != "":
                            if nurse[11] == "Charge":
                                curr_assignment[nurse_id]['adv'] = "Charge"
                            if nurse[11] == "Support":
                                curr_assignment[nurse_id]['adv'] = "Support"
                            if nurse[11] == "Code":
                                curr_assignment[nurse_id]['adv'] = "Code"

                # Bed Assignments
                list_of_beds = []  # temp list of beds
                curr_assignment[nurse_id]['bed'] = ""  # init bed key

                cursor.execute(
                    "SELECT * FROM patients WHERE id in ({0})".format(
                        str(curr_assignment[nurse_id]['patients'])[1:-1]))
                list_of_patients = cursor.fetchall()

                for p in list_of_patients:
                    list_of_beds.append(p[2] + str(p[3]))

                curr_assignment[nurse_id]['bed'] = list_of_beds

            # Overwrite curr_assignment.json
            os.remove(
                "{0}/cache/current_shift/curr_assignment.json".format(CURR_DIR))
            with open("{0}/cache/current_shift/curr_assignment.json".format(CURR_DIR), 'w') as jsonfile:
                json.dump(curr_assignment, jsonfile)

            return render_template("./Assignment Sheets/cur_pnSheet.html",
                                   loggedin=session['loggedin'],
                                   curr_assignment=curr_assignment,
                                   nurseList=nurse_list,
                                   patientList=patient_list)
        else:
            return render_template("./Assignment Sheets/cur_pnSheet_blank.html",
                                   loggedin=session['loggedin'])
    return redirect(url_for('login'))


@ app.route("/pastPNSheet")
def past_PNSheet():
    if 'loggedin' in session:
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()

        try:
            past_json_list = sorted(os.listdir(
                f"{CURR_DIR}/cache/past_shift/"), reverse=True)
            past_json_states = []
            past_json_shifts = []
            past_json_versions = []
        except:
            return redirect(url_for('home'))

        for i, file in enumerate(past_json_list):
            with open(f'{CURR_DIR}/cache/past_shift/{file}', 'r') as jsonfile:
                temp_dict = json.load(jsonfile)
                past_json_versions.append([])
                past_json_states.append(temp_dict)
                past_json_shifts.append(temp_dict[0]['shift-datetime'])
                for version in temp_dict:
                    past_json_versions[i].append(version['timestamp'])

        print(past_json_shifts)
        print(past_json_versions)

        return render_template("./Assignment Sheets/past_pnSheet.html",
                               # Load most recent past assignment
                               nurseList=nurse_list,
                               patientList=patient_list,
                               latestState=past_json_states[0][-1],
                               state=past_json_states,
                               shifts=past_json_shifts,
                               versions=past_json_versions)
    return redirect(url_for('login'))


@ app.route("/pastPNSheetState", methods=["POST"])
def past_PNSheetState():
    if 'loggedin' in session:
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()

        try:
            # Selected version array position
            version_select = request.form["version-select"].split("-")

            past_json_list = sorted(os.listdir(
                f"{CURR_DIR}/cache/past_shift/"), reverse=True)
            past_json_states = []
            past_json_shifts = []
            past_json_versions = []

            for i, file in enumerate(past_json_list):
                with open(f'{CURR_DIR}/cache/past_shift/{file}', 'r') as jsonfile:
                    temp_dict = json.load(jsonfile)
                    past_json_versions.append([])
                    past_json_states.append(temp_dict)
                    past_json_shifts.append(temp_dict[0]['shift-datetime'])
                    for version in temp_dict:
                        past_json_versions[i].append(version['timestamp'])

            print(past_json_shifts)
            print(past_json_versions)

            print(version_select)

            return render_template("./Assignment Sheets/past_pnSheetState.html",
                                   # Load most recent past assignment
                                   nurseList=nurse_list,
                                   patientList=patient_list,
                                   latestState=past_json_states[int(
                                       version_select[0])][int(version_select[1])],
                                   state=past_json_states,
                                   shifts=past_json_shifts,
                                   versions=past_json_versions)
        except Exception as error:
            return str(error)

        return redirect(url_for('home'))

    return redirect(url_for('login'))


@ app.route("/saveState", methods=['POST'])
def save_current_state():
    """ Saves changes to the nurse-patient assignment sheet. Also flags. """
    # variable init
    bed_value = ""  # reset on new pair
    patient_nurse_pair = []

    try:
        # Runs only on first save
        date = request.form['shiftDate']
        time = request.form['shiftTime']

        date_time_obj = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M')
        date_time_obj = datetime.strftime(
            date_time_obj, "%B %d, %Y - %I:%M:%S %p")
    except:
        # Runs on subsequent saves
        date_time_obj = request.form['datetime']

    # Grab nurse and patient tables
    cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    nurse_list = cursor.fetchall()
    cursor.execute("SELECT * FROM patients WHERE discharged_date='-'")
    patient_list = cursor.fetchall()
    cursor.execute("SELECT DISTINCT group_num FROM nurses WHERE priority = 2;")
    fixed = cursor.fetchone()
    cursor.execute("SELECT DISTINCT group_num FROM nurses WHERE priority = 1;")
    flex = cursor.fetchone()
    cursor.execute("SELECT * FROM nurses")
    full_nurse_list = cursor.fetchall()

    # validate flex
    try:
        flex[0] = flex[0]
    except:
        flex = fixed

    if 'loggedin' in session:
        # Variables
        state_assignment_list = []  # Used for storing state history
        state_assignment = {
            "charge": [],
            "support": [],
            "code": [],
            "l_charge": [],
            "l_support": [],
            "l_code": [],
            "assignment": {},
            "timestamp": datetime.now().strftime("%B %d, %Y - %I:%M:%S %p"),
            "shift-datetime": date_time_obj,
            "author": session['name'],
            "fixed": fixed[0],
            "flex": flex[0],
            "id": 0
        }

        # Load state history if available
        if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
            with open("{0}/cache/current_shift/state.json".format(CURR_DIR), 'r') as jsonfile:
                state_assignment_list = json.load(jsonfile)
                state_assignment["id"] = len(state_assignment_list)

        # flag dict init
        flags = {}

        if os.path.exists("{0}/cache/current_shift/curr_assignment.json".format(CURR_DIR)):
            with open("{0}/cache/current_shift/curr_assignment.json".format(CURR_DIR), 'r') as jsonfile:
                assignments = json.load(jsonfile)

        for area in AREA_LIST:
            for i in range(MAX_BED):
                state_assignment["assignment"]["{0}{1}".format(
                    area, i + 1)] = []
                flags["{0}{1}".format(area, i + 1)] = []

        # Parse request
        state_data = request.form['saveStateData']
        state_data = state_data.strip('][').split(',')
        state_data = list(filter(('null').__ne__, state_data))

        # initiate bed areas
        for area in AREA_LIST:
            for i in range(MAX_BED):
                bed_value = f"{area}{i + 1}"
                # create p and n for storing
                state_assignment["assignment"]["{0}".format(bed_value)] = {
                    "p": [], "n": []}

        # clean elements + dict storage
        for i in range(len(state_data)):
            # remove quotation marks
            state_data[i] = state_data[i][1:-1]

            # adv role = <advcode>-"assign"-<nurse id>
            state_data[i] = state_data[i].split('-')

            # adv role states
            if state_data[i][0] == "cn":
                state_assignment["charge"].append(state_data[i][-1])
            if state_data[i][0] == "support":
                state_assignment["support"].append(state_data[i][-1])
            if state_data[i][0] == "code":
                state_assignment["code"].append(state_data[i][-1])
            if state_data[i][0] == "lcn":
                state_assignment["l_charge"].append(state_data[i][-1])
            if state_data[i][0] == "lsupport":
                state_assignment["l_support"].append(state_data[i][-1])
            if state_data[i][0] == "lcode":
                state_assignment["l_code"].append(state_data[i][-1])

            # Assign patient and nurses to beds
            if state_data[i][0] == "pod":
                bed_value = f"{state_data[i][1]}{state_data[i][3]}"  # eg. A3
                temp_p_name = ""
                temp_n_name = ""

                # Append ID and Name in []
                if state_data[i][-2] == "p":
                    for patient in patient_list:
                        if patient[0] == int(state_data[i][-1]):
                            temp_p_name = patient[1]
                            break
                    state_assignment["assignment"][bed_value]['p'] = [
                        state_data[i][-1], temp_p_name]

                if state_data[i][-2] == "n":
                    for nurse in full_nurse_list:
                        if nurse[0] == int(state_data[i][-1]):
                            temp_n_name = nurse[1]
                            break
                    state_assignment["assignment"][bed_value]['n'] = [
                        state_data[i][-1], temp_n_name]

        for area in AREA_LIST:
            for i in range(MAX_BED):

                flag_list = []
                curr_pair = state_assignment["assignment"]["{0}{1}".format(
                    area, i + 1)]

                if len(curr_pair['p']) == 0:
                    flag_list = ['0', '0', '0', '0', '0', '0',
                                 '0', '0', '0', '0', '0']
                else:
                    try:
                        cursor.execute(
                            f"SELECT * FROM patients WHERE id={curr_pair['p'][0]}")
                        patient = cursor.fetchone()
                    except:
                        patient = ""
                        continue

                    # Runs only if nurse is assigned to the patient in this pod
                    try:
                        try:
                            cursor.execute(
                                f"SELECT * FROM nurses WHERE id={curr_pair['n'][0]}")
                            nurse = cursor.fetchone()
                        except:
                            nurse = ""
                            continue

                        # Flag skill level
                        if nurse[7] < patient[4]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

                        # Flag A trained
                        if nurse[8] < patient[5]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

                        # Flag Transfer
                        if nurse[9] < patient[6]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

                        # Flag 1:1
                        # case 1: current patient is 1:1
                        if int(patient[8]):
                            if len(assignments[str(nurse[0])]['patients']) > 1:
                                flag_list.append('1')
                            else:
                                flag_list.append('0')
                        else:
                            # case 2: nurse being assigned is already assigned to another 1:1 patient
                            flag_list.append('0')
                            for p in assignments[str(nurse[0])]['patients']:
                                cursor.execute(
                                    'SELECT one_to_one FROM patients WHERE id={0}'.format(p))
                                fetched_p = cursor.fetchone()
                                if fetched_p[0]:
                                    flag_list[3] = '1'

                        # Flag previous patient
                        flag_list.append('0')
                        for n in patient[9].strip('][').split(', '):
                            if n in list(nurse_list):
                                if nurse[0] != n:
                                    flag_list[4] = '1'

                        # Flag priority
                        flag_list.append('0')
                        for n in patient[9].strip('][').split(', '):
                            if n in list(nurse_list):
                                if nurse[15] == 0:
                                    flags['priority'] = 1

                        # Flag twin
                        if patient[13]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

                        # Flag iv
                        if nurse[10] == patient[7]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

                        # Flag clinical area
                        if nurse[2] != patient[2]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

                        # Flag DTA
                        if nurse[13] != "":
                            flag_list.append(nurse[13])
                        else:
                            flag_list.append('0')

                        # Flag Comments
                        if nurse[14] != "":
                            flag_list.append(nurse[14])
                        else:
                            flag_list.append('0')

                    except:
                        flag_list = ['0', '0', '0', '0', '0',
                                     '0', '0', '0', '0', '0', '0']

                flags["{0}{1}".format(area, i + 1)] = flag_list

        # Write/Overwrite state.json
        if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
            os.remove(
                "{0}/cache/current_shift/state.json".format(CURR_DIR))
        with open("./cache/current_shift/state.json", 'w') as jsonfile:
            state_assignment_list.append(state_assignment)
            json.dump(state_assignment_list, jsonfile)

        # Write/Overwrite flags.json
        if os.path.exists("{0}/cache/current_shift/flags.json".format(CURR_DIR)):
            os.remove(
                "{0}/cache/current_shift/flags.json".format(CURR_DIR))
        with open("./cache/current_shift/flags.json", 'w') as flagjson:
            json.dump(flags, flagjson)

        return redirect(url_for('current_PNSheet'))
    return redirect(url_for('login'))


@ app.route('/endShift', methods=['POST'])
def end_shift():
    # Load current state
    with open("{0}/cache/current_shift/state.json".format(CURR_DIR), 'r') as jsonfile:
        state = json.load(jsonfile)

    date_time_obj = datetime.strptime(
        state[0]['shift-datetime'], "%B %d, %Y - %I:%M:%S %p")
    date_time_obj = datetime.strftime(
        date_time_obj, "%Y-%m-%d-%H-%M")

    # Create past_shift folder on first run
    try:
        os.makedirs("{0}/cache/past_shift".format(CURR_DIR))
    except:
        print("Required directories exist")

    # Copy state.json to past_shift folder
    shutil.copyfile(f"{CURR_DIR}/cache/current_shift/state.json",
                    f"{CURR_DIR}/cache/past_shift/{date_time_obj}.json")

    # Remove curr_shift folder
    shutil.rmtree("{0}/cache/current_shift".format(CURR_DIR))

    # Reset all nurses to unassigned
    cursor.execute("UPDATE nurses SET current_shift = 0")
    db.commit()

    return redirect(url_for('home'))

# Algorithm


@ app.route('/assign', methods=['GET'])
def assign_nurse_patient() -> dict:
    """ Assign nurses to patients"""
    assignments = main_assign(cursor)
    # twins = []
    #
    # # Grab Patients
    # patients = []
    # cursor.execute(
    #     'SELECT * FROM patients WHERE discharged_date="-" ORDER BY length(previous_nurses) DESC, one_to_one DESC, twin DESC, acuity DESC, a_trained DESC, transfer DESC, iv DESC;')
    # patient_list = cursor.fetchall()
    #
    # for row in patient_list:
    #     x = Patient(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
    #                 row[12], row[13])
    #     if row[13] == "1":
    #         twins.append(x)
    #     patients.append(x)
    #
    # # Grab Nurses
    # nurses = []
    # cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
    # nurse_list = cursor.fetchall()
    #
    # for row in nurse_list:
    #     x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
    #               row[12], row[13], row[14], row[15], row[16])
    #     nurses.append(x)
    #
    #     assignments[row[0]] = {'num_patients': 0, 'patients': [], 'prev_p': []}
    #
    # # Get all nurses that are eligible for each patient
    # for p in patients:
    #     if p.get_assigned() == 0:
    #         transfer = p.get_transfer()
    #         a_trained = p.get_a_trained()
    #         acuity = p.get_acuity()
    #         picc = p.get_picc()
    #         one_to_one = p.get_one_to_one()
    #         clinical_area = p.get_clinical_area()
    #         twin = p.get_twin()
    #
    #         # get nurses that match the hard constraints
    #         base = "SELECT * FROM nurses WHERE current_shift=1 AND skill_level>=%d" % acuity
    #
    #         if transfer:
    #             base += " AND transfer=1"
    #         if a_trained:
    #             base += " AND a_trained=1"
    #
    #         cursor.execute(base)
    #         eligible_nurses = cursor.fetchall()
    #         eligible_nurse_objects = []
    #
    #         i = 0
    #         while len(eligible_nurse_objects) < 1 and i < 3:
    #             for row in eligible_nurses:
    #                 # if nurse assigned
    #                 if row[0] in assignments:
    #                     # if nurse has i patients (we use this if our eligible nurses are all assigned. Then we
    #                     # resort to assigning nurses with more than 1 patient)
    #                     if assignments[row[0]]["num_patients"] == i:
    #                         x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
    #                                   row[10], row[11], row[12], row[13], row[14], row[15], row[16])
    #                         eligible_nurse_objects.append(x)
    #                 # if nurse is not assigned
    #                 elif row[0] not in assignments:
    #                     x = Nurse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
    #                               row[10], row[11], row[12], row[13], row[14], row[15], row[16])
    #                     eligible_nurse_objects.append(x)
    #             # for the next iteration, start considering nurses with i += 1 patients.
    #             if len(eligible_nurse_objects) < 1:
    #                 i += 1
    #
    #         # Calculate soft constraint weights
    #         nurse_weights = {}
    #         max_points = 0
    #
    #         for eno in eligible_nurse_objects:
    #             if eno.get_id() not in nurse_weights:
    #                 nurse_weights[eno.get_id()] = 0
    #
    #             # if nurse matches clinical area, give nurse 2 points
    #             if eno.get_clinical_area() == clinical_area:
    #                 nurse_weights[eno.get_id()] += 2
    #
    #             # if nurse matches picc, give nurse 2 points
    #             if eno.get_picc() == picc:
    #                 nurse_weights[eno.get_id()] += 2
    #
    #             # if nurse matches priority, give nurse 7 points
    #             if eno.get_priority() == 1:
    #                 nurse_weights[eno.get_id()] += 7
    #
    #             # if nurse has previous assignments, give nurse 10 points
    #             prev_p = eno.get_previous_patients().strip('][').split(', ')
    #             if prev_p != "[]":
    #                 if str(p.get_id()) in prev_p:
    #                     nurse_weights[eno.get_id()] += 10
    #
    #             # if secondary patient is in the same clinical area as the nurse's first assigned patient, give 7 points
    #             # This is so that the nurse can stay in the same area when he/she has more than 2 patients.
    #             if eno.get_id() in assignments:
    #                 if len(assignments[eno.get_id()]['patients']) > 0:
    #                     first_prev_patient_id = assignments[eno.get_id()]['patients'][0]
    #                     cursor.execute(f"SELECT clinical_area FROM patients WHERE id={first_prev_patient_id}")
    #                     first_prev_patient_pod = cursor.fetchone()
    #                     if p.get_clinical_area() == first_prev_patient_pod[0]:
    #                         nurse_weights[eno.get_id()] += 7
    #
    #             # calculate the highest weight a nurse achieved
    #             if nurse_weights[eno.get_id()] > max_points:
    #                 max_points = nurse_weights[eno.get_id()]
    #
    #         eligible_max_nurses = []
    #
    #         for eno in eligible_nurse_objects:
    #             if nurse_weights[eno.get_id()] == max_points:
    #                 eligible_max_nurses.append(eno.get_id())
    #
    #         # algorithm that matches nurse to patient starting from lowest skill level
    #         sorted_eligible_nurses = sorted(
    #             eligible_nurse_objects, key=lambda x: x.skill_level, reverse=False)
    #
    #         # assign
    #         for sen in sorted_eligible_nurses:
    #             if sen.get_id() in eligible_max_nurses:
    #                 if sen.get_id() not in assignments:
    #                     assignments[sen.get_id()]["num_patients"] = 0
    #                     assignments[sen.get_id()]["patients"] = []
    #
    #                 if twin == "1":
    #                     for twin_object in twins:
    #                         if p.get_name() == twin_object.get_name():
    #                             continue
    #                         elif p.get_last_name() == twin_object.get_last_name():
    #                             assignments[sen.get_id()]["num_patients"] += 1
    #                             assignments[sen.get_id()]["patients"].append(
    #                                 twin_object.get_id())
    #                             twin_object.set_assigned(1)
    #                             twins.remove(twin_object)
    #                             twins.remove(p)
    #                             break
    #
    #                 if one_to_one:
    #                     assignments[sen.get_id()]["num_patients"] = 98
    #                 assignments[sen.get_id()]["num_patients"] += 1
    #                 assignments[sen.get_id()]["patients"].append(p.get_id())
    #
    #                 # set patient to be assigned
    #                 p.set_assigned(1)
    #                 break
    #
    # # Check if a patient is not set as assigned
    # for p in patients:
    #     if p.get_assigned() != 1:
    #         print("Patient", p.get_id(), " is not assigned!")

    print(assignments)

    cursor.execute('SELECT * FROM patients')
    patient_list = cursor.fetchall()

    cursor.execute("SELECT * FROM nurses")
    nurse_list = cursor.fetchall()

    # Create cache/current_shift folders
    try:
        os.makedirs("{0}/cache/current_shift".format(CURR_DIR))
    except:
        print("Required directories exist")

    # If curr_assignment.json already exists, delete
    if os.path.exists("{0}/cache/current_shift/curr_assignment.json".format(CURR_DIR)):
        os.remove(
            "{0}/cache/current_shift/curr_assignment.json".format(CURR_DIR))
    if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
        os.remove(
            "{0}/cache/current_shift/state.json".format(CURR_DIR))

    # Create curr_assignment.json
    with open("./cache/current_shift/curr_assignment.json", 'w') as jsonfile:
        json.dump(assignments, jsonfile)

    # cursor.execute("SELECT * FROM nurses")
    # nurse_list = cursor.fetchall()

    # try:
    #     response = app.response_class(
    #         status=200, response=json.dumps(assignments))
    #     return render_template("./assign.html",
    #                            response=assignments,
    #                            nurseList=nurse_list,
    #                            patientList=patient_list)
    # except ValueError as error:
    #     response = app.response_class(status=400, response=str(error))

    try:
        return redirect(url_for('current_PNSheet'))
    except Exception as error:
        return str(error)

# @app.route('/flag', methods=['GET'])
# def assign_nurse_patient() -> dict:


if __name__ == "__main__":
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)
    app.run()
