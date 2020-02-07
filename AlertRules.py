import requests
from util import APIAuthCreate, generateCSV
import json
import os
import shutil

def APIGetRules(auth, aid):
    # Define URL
    url = 'https://api.thousandeyes.com/v6/alert-rules.json?aid=' + str(aid)

    # Obtain a list of tests
    response = requests.get(url, auth=auth)

    # Convert the response into a json python dictionary/list
    rulesdict = response.json()

    # Obtain the metrics
    ruleslist = rulesdict['alertRules']

    return ruleslist


def APIAlertRules(username, token, aid, fileName):

    # Define username and password
    # username = 'benton@thousandeyes.com'
    # password = 'ubut1jqf8zcwpmlbtmynrnr45hb52zy0'

    #list  used to store test metadata
    rulesobjectlist = []


    # Define the test dictionary
    rulesdict = {}

    # Create the auth
    auth = APIAuthCreate(username, token)
    print('Extracting alert rules data..')

    # Get the tests
    rules = APIGetRules(auth, aid)

    # Loop through each test
    for rule in rules:

        rulesData={}

        ruleFields=[
            'ruleId',
            'ruleName',
            'expression',
            'direction',
            'notifyOnClear',
            'default',
            'alertType',
            'minimumSources',
            'minimumSourcesPct',
            'roundsViolatingOutOf',
            'throughputDuration',
            'roundsViolatingRequired'
        ]

        for field in ruleFields:
        	if field in rule.keys():rulesData[field]=rule[field]
        	else:rulesData[field]=""

        rulesobjectlist.append(rulesData)

    # WRITE TO CSV
    generateCSV(fileName, rulesobjectlist)
    return
