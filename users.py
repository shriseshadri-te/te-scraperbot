import sqlite3

conn = sqlite3.connect('users.db')

conn.execute('CREATE TABLE users(report_id INTEGER PRIMARY KEY, created_by TEXT, report_name TEXT, query_date TEXT, csv_file_name TEXT)')
conn.close()