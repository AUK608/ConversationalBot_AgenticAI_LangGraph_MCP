# create_sample_db.py
import sqlite3

#conn = sqlite3.connect("sample_data.db")
conn = sqlite3.connect("dummy_data.db")
cursor = conn.cursor()

'''cursor.execute("""
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY,
    name TEXT,
    queue TEXT,
    frequency TEXT,
    case_status TEXT,
    case_owner TEXT,
    duration TEXT,
    response TEXT,
    notify TEXT
)
""")'''

cursor.execute("""
CREATE TABLE IF NOT EXISTS Dummy_Cases (
    id INTEGER PRIMARY KEY,
    Case_Number TEXT,
    Description TEXT,
    Subject TEXT,
    Queue_CaseOwner TEXT,
    Status TEXT,
    Priority TEXT,
    Name TEXT,
    Email_ID TEXT
)
""")

'''sample_data = [
    ("Relief Provided Monitoring", "Queue1", "15 mins", "Completed", "ABC_Owner", "3 days", "yes", "xyz@mail.com"),
    ("Relief Provided Monitoring", "Queue2", "30 mins", "Completed", "XYZ_Owner", "2 days", "no", "abc@mail.com"),
    ("Relief Not Provided Monitoring", "Queue3", "1 hour", "Not Completed", "DEF_Owner", "5 days", "yes", "notify1@mail.com"),
    # Add more as needed
]'''

case_num = 1000
queue_l = ["AB.BC.CD", "DC.CB.BA", "ZA.BN.MN"]
stat_l = ["Completed", "In Progress", "Completed", "Unassigned", "In Progress", "Completed", "Completed", "Completed", "Unassigned"]
prior_l = ["Medium", "High", "Medium", "Medium", "High", "Low", "Medium", "High", "High"]
name_l = ["ABC_BCD", "BCD_ABC", "ZAB_NMN"]
email_l = ["abc@example.com", "bcd@example.com", "zab@example.com"]

dummy_data = []

for dd in range(9):
    desc = "Sample Description - " + str(case_num)
    subj = "Sample Subject - " + str(case_num)
    if dd < 3:
        qu = queue_l[0]
        na = name_l[0]
        em = email_l[0]
    elif dd > 2 and dd < 6:
        qu = queue_l[1]
        na = name_l[1]
        em = email_l[1]
    else:
        qu = queue_l[2]
        na = name_l[2]
        em = email_l[2]
    
    dd_tup = (case_num, desc, subj, qu, stat_l[dd], prior_l[dd], na, em)
    dummy_data.append(dd_tup)
    case_num += 1

'''cursor.executemany("""
INSERT INTO cases (name, queue, frequency, case_status, case_owner, duration, response, notify)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", sample_data)'''

cursor.executemany("""
INSERT INTO Dummy_Cases (Case_Number, Description, Subject, Queue_CaseOwner, Status, Priority, Name, Email_ID)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", dummy_data)

conn.commit()
conn.close()
