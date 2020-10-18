from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector
import os


app = Flask(__name__, instance_relative_config=True)
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
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route("/register", methods=['GET'])
def register():
    if 'loggedin' in session:
        return render_template('register.html')
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
                'VALUES (%s, md5(%s), %s, %s)', (username, password, first_name, last_name)
            )
            db.commit()
            return render_template('index.html')
        else:
            return render_template('register.html', msg="Passwords do not match")


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/loginUser', methods=['POST'])
def login_user():
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            'SELECT * FROM users WHERE username = %s AND password = md5(%s)', (username, password,)
        )
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = username
            return render_template("index.html", loggedin=session['loggedin'])
        else:
            return render_template("login.html", msg="Invalid Login")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
