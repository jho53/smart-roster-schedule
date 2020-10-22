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

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Username already taken.'
        elif password != password_conf:
            msg = 'Passwords do not match.'
        else:
            cursor.execute(
                'INSERT INTO users (username, password, first_name, last_name) '
                'VALUES (%s, md5(%s), %s, %s)', (username, password, first_name, last_name)
            )
            db.commit()
            msg = 'Account successfully created'
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
                'SELECT * FROM users WHERE username = %s AND password = md5(%s)', (
                    username, password, )
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
    return render_template(
        "./Records/nurseRecord.html", loggedin=session['loggedin'], nurseList=nurse_list
    )


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
    # Grabs all patients
    cursor.execute("SELECT * FROM patients")
    patient_list = cursor.fetchall()
    return render_template(
        "./Records/patientRecord.html", loggedin=session['loggedin'], patientList=patient_list
    )


@app.route("/patientRecordsSubmit", methods=['POST'])
def patient_records_submit():
    return


@app.route("/profile", methods=['GET'])
def profile():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE username = %s', (session['username'],))
        account = cursor.fetchone()
        return render_template('./Account/profile.html', account=account, loggedin=session['loggedin'])
    return redirect(url_for('login'))


if __name__ == "__main__":
    # Testing
    webbrowser.open("http://localhost:5000/", new=1, autoraise=True)
    app.run()
