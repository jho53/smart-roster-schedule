from nurse import Nurse
from patient import Patient
# from assignment import main_assign

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
import subprocess

UPLOAD_FOLDER = '.\\static\\images'
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
    if 'loggedin' in session:
        curr_nurse_ids = []
        supp_nurse_ids = []
        cn_nurse_ids = []
        code_nurse_ids = []
        group_num = []

        # Grab database information
        cursor.execute("SELECT * FROM nurses")
        nurse_list = cursor.fetchall()
        cursor.execute("SELECT * FROM patients")
        patient_list = cursor.fetchall()
        cursor.execute("SELECT DISTINCT group_num FROM nurses")
        for i in cursor.fetchall():
            if i[0] == 0:
                pass
            else:
                group_num.append(i[0])

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


@app.route("/modalSubmit", methods=["POST"])
def update_current_nurses():
    try:
        if "loggedin" in session:
            current_nurses_id = "({0})".format(
                request.form['current_nurses_list'])
            priority = request.form['priority']

            print(priority)

            if list(current_nurses_id)[1] == ",":
                current_nurses_id = current_nurses_id[:1] + \
                    current_nurses_id[2:]

            try:
                cursor.execute("UPDATE nurses SET current_shift = 0")
                cursor.execute("UPDATE nurses SET current_shift = 1 WHERE id in {0}".format(
                    current_nurses_id))
                cursor.execute("UPDATE nurses SET priority = 0")
                cursor.execute(
                    "UPDATE nurses SET priority = 1 WHERE group_num = {0}".format(priority))
                db.commit()
                return redirect(url_for('home'))
            except Exception as error:
                print(error)
    except:
        print(Exception)


@app.route("/modalSubmit2", methods=["POST"])
def update_cn_supp():
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
            session['name'] = "Administrator"
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
                session['name'] = account[3] + " " + account[4]
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
        print(error)
    return redirect(url_for('nurse_records'))


@app.route("/editNurseRecords", methods=["POST"])
def edit_nurse_records():
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
    print(nurse_fte)

    query = "UPDATE smartroster.nurses SET name = %s, clinical_area = %s, rotation = %s, group_num = %s, fte = %s, " \
            " skill_level = %s, a_trained = %s, transfer = %s, iv = %s, advanced_role = %s, dta = %s, comments = %s WHERE id = %s"

    arguments = (nurse_name, nurse_area, nurse_rotation, nurse_group,
                 str(nurse_fte), nurse_skill, nurse_a_trained, nurse_transfer, nurse_iv, nurse_adv_role,
                 nurse_DTA, nurse_comments, nurse_id)

    try:
        cursor.execute(query, arguments)
        db.commit()
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
        print(error)

    return redirect(url_for('patient_records'))


@app.route("/editPatientRecords", methods=["POST"])
def edit_patient_records():
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
    except Exception as error:
        print(error)
    return redirect(url_for('patient_records'))


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_image', methods=['POST'])
def upload_image():
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
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return redirect(url_for('profile'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/settings")
def settings():
    if 'loggedin' in session:
        return render_template("./Account/settings.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


# Assignment Sheets


@app.route("/currentCAASheet")
def current_CAASheet():
    area_nurse_list = []

    if 'loggedin' in session:
        # Grab nurse and patient tables
        cursor.execute("SELECT * FROM nurses WHERE current_shift=1")
        nurse_list = cursor.fetchall()
        cursor.execute(
            "SELECT DISTINCT group_num FROM nurses WHERE priority = 1")
        group_num = cursor.fetchone()

        if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
            with open("{0}/cache/current_shift/state.json".format(CURR_DIR), 'r') as jsonfile:
                state = json.load(jsonfile)

            for i, area in enumerate(AREA_LIST):
                area_nurse_list.append([])
                for j in range(MAX_BED):
                    try:
                        if state["assignment"][f"{area}{j + 1}"][1] not in area_nurse_list[i]:
                            area_nurse_list[i].append(
                                state["assignment"][f"{area}{j + 1}"][1])
                    except:
                        continue

            return render_template("./Assignment Sheets/cur_caaSheet.html",
                                   loggedin=session['loggedin'],
                                   nurseList=nurse_list,
                                   groupNum=group_num[0],
                                   areaNurseList=area_nurse_list,
                                   state=state)

        return render_template("./Assignment Sheets/cur_caaSheet_blank.html",
                               loggedin=session['loggedin'])

    return redirect(url_for('login'))


@app.route("/currentPNSheet")
def current_PNSheet():
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
                                   state=state,
                                   flags=flags,
                                   nurseList=nurse_list,
                                   patientList=patient_list)
        elif os.path.exists('{0}/cache/current_shift/curr_assignment.json'.format(CURR_DIR)):
            with open('./cache/current_shift/curr_assignment.json', 'r') as jsonfile:
                curr_assignment = json.load(jsonfile)

            for nurse_id in curr_assignment:
                # Advanced Role Assignment
                if full_nurse_list[int(nurse_id) - 1][11] != "":
                    if full_nurse_list[int(nurse_id) - 1][11] == "Charge":
                        curr_assignment[nurse_id]['adv'] = "Charge"
                    if full_nurse_list[int(nurse_id) - 1][11] == "Support":
                        curr_assignment[nurse_id]['adv'] = "Support"
                    if full_nurse_list[int(nurse_id) - 1][11] == "Code":
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


@ app.route("/pastCAASheet")
def past_CAASheet():
    if 'loggedin' in session:
        return render_template("./Assignment Sheets/past_caaSheet.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


@ app.route("/pastPNSheet")
def past_PNSheet():
    if 'loggedin' in session:
        past_json_list = os.listdir(f"{CURR_DIR}/cache/past_shift/")
        past_json_state = []
        past_json_dates = []

        for file in past_json_list:
            with open(f'{CURR_DIR}/cache/past_shift/{file}', 'r') as jsonfile:
                temp_dict = json.load(jsonfile)
                past_json_state.append(temp_dict)
                past_json_dates.append(file[:-5].split("-"))

        print(past_json_state)
        print(past_json_dates)

        return "working"
        # return render_template("./Assignment Sheets/past_pnSheet.html", loggedin=session['loggedin'])
    return redirect(url_for('login'))


@ app.route("/saveState", methods=['POST'])
def save_current_state():
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
    cursor.execute("SELECT DISTINCT group_num FROM nurses WHERE priority = 1;")
    priority = cursor.fetchone()

    if 'loggedin' in session:
        try:
            # dict init
            state_assignment = {
                "charge": [],
                "support": [],
                "code": [],
                "assignment": {},
                "timestamp": datetime.now().strftime("%B %d, %Y - %I:%M:%S %p"),
                "shift-datetime": date_time_obj,
                "author": session['name'],
                "priority": priority[0]
            }

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
            # clean elements + dict storage
            for i in range(len(state_data)):

                # remove quotation marks
                state_data[i] = state_data[i][1:-1]
                # adv role states
                if state_data[i][:2] == "cn":
                    state_assignment["charge"].append(state_data[i][10:])
                if state_data[i][:2] == "su":
                    state_assignment["support"].append(state_data[i][15:])
                if state_data[i][:2] == "co":
                    state_assignment["code"].append(state_data[i][12:])

                # assignment states
                if (i % 2) != 0 and i > 6:
                    # patient
                    bed_value = ""  # reset on new pair
                    patient_nurse_pair = []

                    pod = state_data[i][4]
                    bed_num = state_data[i][10:12]  # '5-' or '12'
                    try:
                        # bed number is two digits
                        int(bed_num)
                        bed_value = (pod + bed_num)
                        try:
                            patient_nurse_pair.append(
                                abs(int(state_data[i][-2:])))
                        except:
                            patient_nurse_pair.append(int(state_data[i][-1:]))
                    except:
                        # bed number is 1 digit
                        bed_value = (pod + bed_num[:-1])
                        try:
                            patient_nurse_pair.append(
                                abs(int(state_data[i][-2:])))
                        except:
                            patient_nurse_pair.append(int(state_data[i][-1:]))
                elif i > 6:
                    # nurse
                    try:
                        patient_nurse_pair.append(abs(int(state_data[i][-2:])))
                    except:
                        patient_nurse_pair.append(int(state_data[i][-1:]))
                    state_assignment["assignment"][bed_value] = patient_nurse_pair

            for area in AREA_LIST:
                for i in range(MAX_BED):
                    flag_list = []
                    curr_pair = state_assignment["assignment"]["{0}{1}".format(
                        area, i + 1)]

                    if len(curr_pair) == 0:
                        flag_list = ['0', '0', '0', '0',
                                     '0', '0', '0', '0', '0']
                    else:

                        cursor.execute(
                            f"SELECT * FROM patients WHERE id={curr_pair[0]}")
                        patient = cursor.fetchone()

                        cursor.execute(
                            f"SELECT * FROM nurses WHERE id={curr_pair[1]}")
                        nurse = cursor.fetchone()

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
                        if nurse[15]:
                            flag_list.append('1')
                        else:
                            flag_list.append('0')

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

                    flags["{0}{1}".format(area, i + 1)] = flag_list

            # Write/Overwrite state.json
            if os.path.exists("{0}/cache/current_shift/state.json".format(CURR_DIR)):
                os.remove(
                    "{0}/cache/current_shift/state.json".format(CURR_DIR))
            with open("./cache/current_shift/state.json", 'w') as jsonfile:
                json.dump(state_assignment, jsonfile)

            # Write/Overwrite flags.json
            if os.path.exists("{0}/cache/current_shift/flags.json".format(CURR_DIR)):
                os.remove(
                    "{0}/cache/current_shift/flags.json".format(CURR_DIR))
            with open("./cache/current_shift/flags.json", 'w') as flagjson:
                json.dump(flags, flagjson)

            return redirect(url_for('current_PNSheet'))

        except Exception as error:
            print(error)
            return redirect(url_for('current_PNSheet'))
    return redirect(url_for('login'))


@ app.route('/endShift', methods=['POST'])
def end_shift():
    # Load current state
    with open("{0}/cache/current_shift/state.json".format(CURR_DIR), 'r') as jsonfile:
        state = json.load(jsonfile)

    date_time_obj = datetime.strptime(
        state['shift-datetime'], "%B %d, %Y - %I:%M:%S %p")
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

    return redirect(url_for('home'))

# Algorithm


@ app.route('/assign', methods=['GET'])
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
        if row[13] == "1":
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
                                assignments[sen.get_id()]["patients"].append(
                                    twin_object.get_id())
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

    try:
        response = app.response_class(
            status=200, response=json.dumps(assignments))
        return render_template("./assign.html", response=assignments, nurseList=nurse_list, patientList=patient_list)
    except ValueError as error:
        response = app.response_class(status=400, response=str(error))

# @app.route('/flag', methods=['GET'])
# def assign_nurse_patient() -> dict:


if __name__ == "__main__":
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)
    app.run()
