from requests.auth import HTTPBasicAuth
import csv, io
from flask import make_response

def APIAuthCreate(username, password):
    # Create auth
    auth = (username, password)
    return auth

def generateCSV(fileName, data):
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+fileName+".csv"
    output.headers["Content-type"] = "text/csv"
    return output
