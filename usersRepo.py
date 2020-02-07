import sqlite3 as sql

def save(username, report, date, fileName):
    with sql.connect("users.db") as con:
        cur = con.cursor()
        data = (username,report,date.today(),fileName)
        cur.execute("INSERT INTO users (created_by,report_name,query_date,csv_file_name) VALUES (?, ?, ?, ?)", data)
        con.commit()
def getAll():
    con = sql.connect("users.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from users")
    users = cur.fetchall()
    return users

