from flask import Flask, render_template, request, make_response, send_from_directory
from data import ReportList
from Test import APIMain
from AlertRules import APIAlertRules
import json
import time

app = Flask(__name__)

ReportList = ReportList()

# Home
@app.route('/')
def index():
    return render_template('home.html')

# Query
@app.route('/querypage')
def querypage():
    return render_template('query.html')


@app.route('/generate', methods=['POST'])
def result():
    if request.method == 'POST':
        username = request.form.get('user')
        token = request.form.get('auth')
        aid = request.form.get('aid')
        report =  request.form.get('report')
        fileName = ''.join(report + '_' + str(aid) + '_' + str(time.time()))
        selectReport(username, token, aid, report, fileName)
        # store this info in the database
        return send_from_directory('reports',
                                   fileName+ '.csv', as_attachment=True)
# Query
@app.route('/reportlist')
def reportlist():
    return render_template('reportlist.html', reportlist = ReportList )

def selectReport(username, token, aid, report, fileName):
    return {
        'Tests': APIMain(username, token, aid, fileName),
        'AlertRules' : APIAlertRules(username, token, aid, fileName)
        # 'AccountGroups' : APIAlertRules(username, token, aid, fileName),
        # 'AgentList' : APIAlertRules(username, token, aid, fileName)
    }[report]

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug='True')
