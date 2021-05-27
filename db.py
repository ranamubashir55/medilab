a = [
"CREATE TABLE if not exists users (ID INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)",
# "INSERT INTO users (username, password) VALUES ('admin', 'admin')",
"CREATE TABLE if not exists patients (ID INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT, lastname TEXT, address TEXT, contact number,age TEXT, patient_category TEXT, gender TEXT, status Text, stool TEXT, sensitivity TEXT, taste TEXT, thirst TEXT, hands_feet_burn TEXT, hunger TEXT, sleep TEXT,constitution TEXT, attachment TEXT )"
]
import sqlite3
conn = sqlite3.connect('database.db')
# import pdb;pdb.set_trace()
for each in a:
    records = conn.execute(each)
conn.commit()