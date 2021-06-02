import datetime
from flask import Flask, session, redirect, url_for, escape, request, render_template, jsonify, send_from_directory
import sqlite3, os
from datetime import datetime as d
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "any random string"

app.config['UPLOAD_FOLDER'] = 'uploads'
if not 'uploads' in os.listdir():
    os.mkdir('uploads')

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)

@app.route('/', methods=['GET'])
def index():
    print("hello index")
    
    return render_template("index.html")

@app.route('/admin')
def admin():
    print("hello index")
    if 'id' not in session:
        return render_template("login.html")
    id = session['id']
    print(id)
    return render_template("dashboard.html")

@app.route('/add_patient', methods=['POST','GET'])
def add_patient():
    if 'id' not in session:
        return render_template("login.html")
    id = session['id']
    if request.method== 'GET':
        return render_template("add_patient.html")
    if request.method=="POST":
        f = request.files['docs']
        filename=''
        if f:
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
        conn = sqlite3.connect('database.db')
        query = "INSERT into patients(firstname , lastname , address , contact ,age ,  gender , status ,patient_category , stool , sensitivity , taste , thirst , hands_feet_burn , hunger , sleep ,constitution, attachment)"
        query =query+f"VALUES ('{request.form['inputFirstName']}', '{request.form['inputLastName']}', '{request.form['address']}', '{request.form['contact']}', '{request.form['age']}', '{request.form['gender']}', '{request.form['status']}', '{request.form['p_category']}', '{request.form['stool']}', '{request.form['sensitivity']}', '{request.form['taste']}', '{request.form['thirst']}', '{request.form['burn_feel']}', '{request.form['hunger']}', '{request.form['sleep']}', '{request.form['Constitution']}', '{filename}')"
        conn.execute(query)
        conn.commit()
        return render_template('add_patient.html', data={"msg":"Patient data added successfully.."})

@app.route("/send_file", methods=['POST'])
def get_file():
    """Download a file."""
    if request.method=="POST":
        file_name = request.form['file_name']
        directory = "uploads/"
        print(file_name.strip())
        return send_from_directory(directory, file_name.strip(), as_attachment=True)

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if 'id' not in session:
        return render_template("login.html")
    id = session['id']
    if request.method=='GET':
        return render_template("change_pass.html")
    if request.method == 'POST':
        n_pass = request.form['new_pass']
        c_pass = request.form['confirm_pass']
        o_pass = request.form['old_pass']
        conn = sqlite3.connect('database.db')
        records = conn.execute("Select * from users where username = '"+session['id']+"' and password = '"+o_pass+"'")
        user = records.fetchall()
        if user:
            query = "Update users set password='"+n_pass+"' where username= '"+ session['id']+"'"
            conn.execute(query)
            conn.commit()
            return render_template("change_pass.html", data={"msg":"Succss! Password updated successfully.. ","class":"alert-success"})
        else:
            return render_template("change_pass.html", data={"msg":"Error! Check your old password.. ", "class":"alert-danger"})

@app.route('/view_patient' , methods=['GET'])
def view_patient():
    
    if 'id' not in session:
        return render_template("login.html")
    id = session['id']
    if request.method=="GET":
        conn = sqlite3.connect('database.db')
        records = conn.execute("Select * from patients")
        data = records.fetchall()
        print(data)
        return render_template("view_patient.html", data=data)

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        records = conn.execute("Select * from users where username = '"+name+"' and password = '"+password+"'")
        user = records.fetchall()
        if user:
            session['id'] = user[0][1]
            return redirect(url_for('admin'))
        else:
            return render_template("login.html", data={"msg":"Error! Check your username or password...","class":"alert-danger"})
    if request.method == 'GET' and session.get('id'):
        return redirect(url_for('admin'))
    return render_template("login.html")


if __name__ =="__main__":
    # app.run(host= "0.0.0.0", debug=True ,port=80, threaded=True)
    app.run(host= "0.0.0.0",port=5000,debug=True, threaded=True)