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
    conn = sqlite3.connect("database.db")
    query = "Select (select count(*) from patients) as count1, (select count(*) from combination) as count2, (select count(*) from patient_visit) as count3, (select count(*) from appointments) as count4"
    records = conn.execute(query)
    data = records.fetchone()
    return render_template("dashboard.html", data = {"patients":data[0], "combination":data[1], "visits":data[2],"appoint":data[3]}, session_id = id)

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
        query = "INSERT into patients(firstname , lastname , address , contact ,age ,  gender , status ,patient_category , stool , sensitivity , taste , thirst , hands_feet_burn , hunger , sleep ,constitution, attachment, symptoms)"
        query =query+f"VALUES ('{request.form['inputFirstName']}', '{request.form['inputLastName']}', '{request.form['address']}', '{request.form['contact']}', '{request.form['age']}', '{request.form['gender']}', '{request.form['status']}', '{request.form['p_category']}', '{request.form['stool']}', '{request.form['sensitivity']}', '{request.form['taste']}', '{request.form['thirst']}', '{request.form['burn_feel']}', '{request.form['hunger']}', '{request.form['sleep']}', '{request.form['Constitution']}', '{filename}', '{request.form['symptoms']}')"
        conn.execute(query)
        conn.commit()
        return render_template('add_patient.html', data={"msg":"Patient data added successfully.."})

@app.route("/book_appointment", methods=["GET", "POST"])
def add_appointment():
    if 'id' not in session:
        return render_template("login.html")
    if request.method== 'GET':
        conn = sqlite3.connect('database.db')
        record = conn.execute(f"select * from appointments")
        data = record.fetchall()
        return render_template("view_appointments.html", data = data)

    if request.method=="POST":
        conn = sqlite3.connect('database.db')
        conn.execute(f"Insert into appointments (name, email, date, phone, department, doctor, message) Values ('{request.form['name']}', '{request.form['email']}', '{request.form['date']}','{request.form['phone']}','{request.form['department']}','{request.form['doctor']}','{request.form['message']}' )")
        conn.commit()
        return jsonify({"msg":"success"}), 200

@app.route("/add_visit", methods=['GET','POST'])
def add_visit():
    if 'id' not in session:
        return render_template("login.html")
    if request.method== 'GET':
        v_id = request.args.get("v_id")
        p_id = request.args.get("id")
        if v_id:
            conn = sqlite3.connect('database.db')
            record = conn.execute(f"select * from patient_visit where id= {str(v_id)}")
            data = record.fetchone()
            return render_template("add_visit.html", v_data = data, vid= v_id)
        if p_id:
            return render_template("add_visit.html", p_id = p_id)

    if request.method=="POST":
        now = d.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        p_id = request.args.get("id")
        v_id = request.args.get("v_id")
        pid = request.args.get("p_id")
        symp = request.form['symptoms']
        diagnosis = request.form['diagnosis']
        med = request.form['medicine']
        feedback = request.form['feedback']
        fee = request.form['fee']
        is_repeat = request.form['repeat']
        p_id = is_repeat if is_repeat else p_id
        conn = sqlite3.connect('database.db')
        if p_id or is_repeat:
            query = f"Insert into patient_visit(patient_id, symptoms, diagnosis, medicine, fee, date, feedback) Values ({p_id}, '{symp}','{diagnosis}', '{med}', '{fee}','{date_time}', '{feedback}')"
            message = "Succss! Patient visit added successfully.. "
            conn.execute(query)
            conn.commit()
            return redirect(url_for('patient_detail', id=int(p_id)))
        if v_id and not is_repeat and pid:
            query = f"Update patient_visit set symptoms='{symp}',diagnosis='{diagnosis}', medicine='{med}', fee='{fee}', date='{date_time}', feedback='{feedback}'  where id = {int(v_id)}"
            message = "Patient visit info has been updated successfully.. "
            conn.execute(query)
            conn.commit()
            return redirect(url_for("patient_detail", id=int(pid)))
    
        
        

@app.route("/patient_detail", methods= ['GET','POST'])
def patient_detail():
    if 'id' not in session:
        return render_template("login.html")
    if request.method=="GET":
        conn = sqlite3.connect('database.db')
        patient_id = request.args.get('id')
        p_records = conn.execute(f"Select * from patients where id = {patient_id}")
        p_details = p_records.fetchone()
        records = conn.execute(f"Select * from patient_visit where patient_id = {patient_id}")
        data = records.fetchall()
        print(data)
        return render_template("view_patient_detail.html", data=data, p_id = patient_id, patient_detail = p_details)
    if request.method=="POST":
        conn = sqlite3.connect('database.db')
        patient_id = int(request.args.get('id'))
        f = request.files['docs']
        filename=''
        if f:
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
        attach = f",attachment='{filename}'" if filename else ''
        query = f"Update patients set age ='{request.form['age']}', contact='{request.form['contact']}', status='{request.form['marritial']}', sensitivity='{request.form['sensitive']}', taste='{request.form['taste']}', thirst='{request.form['thirst']}', hands_feet_burn='{request.form['burning']}',hunger='{request.form['hunnger']}', sleep='{request.form['sleep']}',patient_category='{request.form['p_category']}',stool='{request.form['stool']}',constitution='{request.form['constitution']}',address='{request.form['address']}'"+attach+f" where id={patient_id}"
        conn.execute(query)
        conn.commit()
        return redirect( url_for('view_patient'))

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

@app.route('/add_combination', methods=['POST', 'GET'])
def add_combination():
    if 'id' not in session:
        return render_template("login.html")
    id = session['id']
    if request.method=='GET':
        if request.args.get('id'):
            conn = sqlite3.connect('database.db')
            query=f"Select * from combination where id= {request.args['id']}"
            records = conn.execute(query)
            data = records.fetchone()
            print(data)
            return render_template('add_combination.html', data = data )
        else:
            return render_template("add_combination.html")
    if request.method == 'POST':
        disease = request.form['disease']
        medicine = request.form['medicine']
        record_id = request.args.get('id')
        conn = sqlite3.connect('database.db')
        if record_id:
            query = f"Update combination set disease='{disease}', medicine='{medicine}' where id= {record_id} "
            message = "Combination updated successfully.."
        if not record_id:
            query = f"Insert into combination (disease, medicine) Values ('{disease}', '{medicine}')"
            message = "New combination added successfully.."
        try:
            conn.execute(query)
            conn.commit()
            return render_template('add_combination.html', msg={"msg":message, "class":"alert-success"})
        except Exception:
            return render_template('add_combination.html', msg={"msg":"Warning! Combiation already exists..", "class":"alert-danger"})

@app.route('/del_combination', methods=['GET'])
def del_combination():
    if 'id' not in session:
        return render_template("login.html")
    if request.method=="GET":
        conn = sqlite3.connect('database.db')
        conn.execute(f"delete from combination where id= {request.args.get('id')}")
        conn.commit()
        return redirect(url_for('view_combination'))

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

@app.route('/view_combination' , methods=['GET'])
def view_combination():
    if 'id' not in session:
        return render_template("login.html")
    id = session['id']
    if request.method=="GET":
        conn = sqlite3.connect('database.db')
        records = conn.execute("Select * from combination")
        data = records.fetchall()
        print(data)
        return render_template("view_combination.html", data=data)


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