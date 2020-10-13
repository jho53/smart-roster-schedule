from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector
import os


app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.urandom(12).hex()


@app.route("/")
def home():
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/loginUser', methods=['POST'])
def login_user():
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

    try:
        db = mysql.connector.connect(
            host="localhost",
            user=username,
            passwd=password,
            database="smartroster",
            auth_plugin="mysql_native_password"
        )
        session['username'] = db.user
        session['loggedin'] = True
        return render_template("index.html")

    except Exception:
        return render_template("login.html", msg="Invalid Login")


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()