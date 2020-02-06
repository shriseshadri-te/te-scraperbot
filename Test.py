import requests
import csv
from requests.auth import HTTPBasicAuth
import json
import os
import shutil

def APIAuthCreate(username, password):
    # Create auth
    auth = (username, password)
    return auth

def APIGetTests(auth):
    # Define URL
    url = 'https://api.thousandeyes.com/v6/tests.json'

    # Obtain a list of tests
    response = requests.get(url, auth=auth)

    # Convert the response into a json python dictionary/list
    testsdict = response.json()

    # Obtain the metrics
    testslist = testsdict['test']

    return testslist


def APIGetTestData(auth,testId):
    url = 'https://api.thousandeyes.com/v6/tests/{}.json'.format(testId)
    response = requests.get(url, auth=auth)
    testdatatext = response.text
    return testdatatext


def APIMain():
    # Define username and password
    username = 'benton@thousandeyes.com'
    password = 'ubut1jqf8zcwpmlbtmynrnr45hb52zy0'


    #list  used to store test metadata
    testobjectlist = []


    # Define the test dictionary
    testdict = {}

    # Create the auth
    auth = APIAuthCreate(username, password)
    print('Extracting test data..')

    # Get the tests
    tests = APIGetTests(auth)

    # Loop through each test
    for test in tests:

        testData={}

        testFields=[
            'enabled',
            'createdBy',
            'createdDate',
            'testId',
            'testName',
            'type',
            'server',
            'interval',
            'httpInterval',
            'httpTimeLimit',
            'throughputDuration',
            'bgpMeasurements',
            'alertsEnabled',
            'domain',
            'liveShare',
            'timeLimit',
            'ftpTimeLimit',
            'pageLoadTimeLimit',
            'sipTimeLimit',
            'dnsServers__serverName'
        ]

        for field in testFields:
        	if field in test.keys():
        		testData[field]=test[field]
        	else:
        		testData[field]="NULL"

        testobjectlist.append(testData)


    # Count numbers of agents
    for testObject in testobjectlist:
    	curData=APIGetTestData(auth,testObject['testId'])

    	searchCloud="\"agentType\":\"Cloud\""
    	cloudAgents=curData.count(searchCloud)

    	searchEnt="\"agentType\":\"Enterprise\""
    	entAgents=curData.count(searchEnt)

    	#print("Cloud {}, Ent {}".format(cloudAgents,entAgents))
    	testObject['cloudAgents']=cloudAgents
    	testObject['entAgents']=entAgents

    # WRITE TO CSV
    toCSV = testobjectlist
    keys = toCSV[0].keys()
    with open('./reports/testlist.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)
    print('Test data written to file.')
    return
