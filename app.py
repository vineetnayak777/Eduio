from asyncio.windows_events import NULL
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd
import numpy as np

from algorithm.rvp import pvr
from algorithm.jee_algo import finalList

from algorithm.kcet_predict import kcet_prediction, kcet_prediction_yes_or_no, kcet_prediction_yes_or_no_both
from algorithm.kcet_predict import kcet_prediction_wrt_branch

from algorithm.admission_check import college_predict

app = Flask(__name__)
  
app.secret_key = 'eduio123'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '7019252847'
app.config['MYSQL_DB'] = 'eduiologin'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student_accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

  
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student_accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO student_accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student_accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/jee', methods=["GET","POST"])
def jee_render():
    if 'loggedin' in session:
        if(request.method == "POST"):
            req = request.form

            percentile = req["percentile"]
            rank = req["rank"]
            state = req["state"]
            pwd = req["pwd"]
            gender = req["gender"]
            category = req["category"]
            sortby = str(req["sortby"])

            if(percentile == "" and rank == ""):
                flash("Please enter either your Rank or your Percentile",'error')
                return redirect(request.url)

            if(rank == ""):
                ranks = pvr(float(percentile),pwd,category)
                ranks = int(ranks)

                if(ranks <= 0):
                    ranks = 2
                result = finalList(ranks,float(percentile),category,state,gender,pwd,sortby)

            if(rank):
                result = finalList(int(rank),percentile,category,state,gender,pwd,sortby)
                ranks = rank
            return render_template("result.html",ranks=ranks,category=category,tables=[result.to_html(classes='data')], titles=result.columns.values)

        return render_template('jee.html')
    return redirect(url_for('login'))

@app.route('/kcet', methods=["GET","POST"])
def kcet_render():
    if 'loggedin' in session:
        if(request.method =="POST"):
            req = request.form

            rank = int(req.get("Rank"))
            category = req.get("category")

            result_df = kcet_prediction(rank, category)
            if(result_df.empty == False):
                return render_template("kcet_result.html", tables=[result_df.to_html(classes='table table-stripped', index=False)],  titles=result_df.columns.values)
            
            msg = "OOPS! Seems like you are ineligible for Engineering"
            return render_template("failure.html", msg = msg)
        return render_template('kcet.html')
    return redirect(url_for('login'))

@app.route('/kcet_wrt_branch', methods=["GET","POST"])
def kcet_wrt_branch_render():
    if 'loggedin' in session:
        if(request.method =="POST"):
            req = request.form

            rank = int(req.get("Rank"))
            category = req.get("category")
            branch = req.get("branch")

            result_df = kcet_prediction_wrt_branch(rank, category, branch)
            if(result_df.empty == False):
                return render_template("kcet_result.html", msg = branch, tables=[result_df.to_html(classes='table table-stripped', index=False)],  titles=result_df.columns.values)
            
            msg = "OOPS! Seems like you are ineligible for Engineering"
            return render_template("failure.html", msg = msg)
        return render_template('kcet_wrt_branch.html')
    return redirect(url_for('login'))

@app.route('/kcet_wrt_college', methods=["GET","POST"])
def kcet_wrt_college_render():
    if 'loggedin' in session:
        if(request.method =="POST"):
            req = request.form

            rank = int(req.get("Rank"))
            category = req.get("category")
            college = req.get("college")

            result_df = kcet_prediction_yes_or_no(rank, category, college)
            if(result_df.empty == False):
                return render_template("kcet_result.html", msg = college, tables=[result_df.to_html(classes='table table-stripped', index=False)],  titles=result_df.columns.values)

            msg = "OOPS! Seems like you are ineligible for Engineering"
            return render_template("failure.html", msg = msg)
        return render_template('kcet_wrt_college.html')
    return redirect(url_for('login'))

@app.route('/kcet_yes_or_no', methods=["GET","POST"])
def kcet_yes_or_no_render():
    if 'loggedin' in session:
        if(request.method =="POST"):
            req = request.form

            rank = int(req.get("Rank"))
            category = req.get("category")
            college = req.get("college")
            branch = req.get("branch")

            result = kcet_prediction_yes_or_no_both(rank, category, college, branch)
            return render_template("yes_or_no_result.html", msg1 = result, msg = (college, branch))

        return render_template('kcet_yes_or_no.html')
    return redirect(url_for('login'))
@app.route('/admission_check', methods=["GET","POST"])
def admission_check_render():
    if 'loggedin' in session:
        if(request.method =="POST"):
            req = request.form

            gre = float(req.get("gre"))
            toefl = float(req.get("toefl"))
            ur = float(req.get("rating"))
            sop = float(req.get("sop"))
            lor = float(req.get("lor"))
            research = int(req.get("research"))
            cgpa = float(req.get("cgpa"))

            result, score = college_predict(gre, toefl, ur, sop, lor, cgpa, research)
            return render_template("admission_result.html", result = result, score = score)

        return render_template('admission_check.html')
    return redirect(url_for('login'))

@app.route('/news_entry', methods = ["GET", "POST"])
def add_event_data_render():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if(request.method =="POST"):
            req = request.form

            username = req.get("name")
            title = req.get("title")
            email = req.get("email")
            college = req.get("college")
            description = req.get("description")
            link = req.get("link")
            date_of_event = str(req.get("date"))
            cursor.execute('INSERT INTO news_module VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', (username, title, email, college, description, link, date_of_event,))
            mysql.connection.commit()
            return render_template("data_added_successfully.html")
        return render_template("news_module_add.html")
    return redirect(url_for('login'))

@app.route('/view_event', methods = ["GET", "POST"])
def view_college_event_render():
    if 'loggedin' in session:
        if(request.method == "POST"):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            req = request.form

            college = req.get("college")
            cursor.execute('select * from news_module where college = %s',(college,))
            results = cursor.fetchall()
            if(results):
                print(type(results[0]), flush = True)
                return render_template('college_events_result.html', results = results, college = college)
            msg = "No events from selected college found"
            return render_template('failure.html', msg = msg)
        return render_template('search_college_event.html')
    return redirect(url_for('login'))

@app.route('/about_us')
def about_us_render():
    if 'loggedin' in session:
        return render_template('about_us.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
