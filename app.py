from flask import Flask, render_template, request, make_response, send_from_directory
from data import ReportList
from Test import APIMain
import json
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
        APIMain()
        return send_from_directory('reports',
                                   'testlist.csv', as_attachment=True)

# Query
@app.route('/reportlist')
def reportlist():
    return render_template('reportlist.html', reportlist = ReportList )

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug='True')
