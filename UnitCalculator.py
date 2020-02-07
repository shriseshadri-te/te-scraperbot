import requests
import json
import os
import shutil
from util import APIAuthCreate, generateCSV


# Function Definitions
def APIGetTests(auth, aid):
    # Define URL
    aid = "?aid="+aid
    url = 'https://api.thousandeyes.com/v6/tests.json{}'.format(aid)

    # Obtain a list of tests
    response = requests.get(url, auth=auth)

    # Convert the response into a json python dictionary/list
    testsdict = response.json()

    # Obtain the metrics
    testslist = testsdict['test']

    return testslist


def APIGetTestData(auth,testId, aid):
    aid = "?aid="+aid
    url = 'https://api.thousandeyes.com/v6/tests/{}.json{}'.format(testId,aid)
    response = requests.get(url, auth=auth)
    testdatatext = response.text
    return testdatatext


def testCost(testType,httpTimeout,otherTimeout,interval,cloudAgents,entAgents,dnsServers,duration,direction,targetType,plHttpInt):
    if testType in ['agent-to-server','agent-to-agent','dns-trace','dns-dnssec','dns-server']:
        unitsCloud=5
        unitsEnt=2.5
        perInterval = (unitsCloud * cloudAgents) + (unitsEnt * entAgents)

        if testType == "dns-server":
            perInterval *= dnsServers

        # why is the so complicated? :sob:
        elif testType == 'agent-to-agent':
            if direction == 'BIDIRECTIONAL':
                if targetType is "Ent":
                    testSrcEnt=cloudAgents+entAgents+entAgents
                    testSrcCld=cloudAgents
                elif targetType is "Cloud":
                    testSrcEnt=entAgents
                    testSrcCld=cloudAgents+cloudAgents+entAgents
            elif direction == "TO_TARGET":
                testSrcCld=cloudAgents
                testSrcEnt=entAgents
            elif direction == "FROM_TARGET":
                if targetType is "Ent":
                    testSrcEnt=cloudAgents+entAgents
                    testSrcCld=0
                elif targetType is "Cloud":
                    testSrcCld=cloudAgents+entAgents
                    testSrcEnt=0
            perInterval = (unitsCloud * testSrcCld) + (unitsEnt * testSrcEnt)

    elif testType in ['http-server','ftp-server','page-load','transactions','web-transactions','sip-server','voice','voice-call']:
        unitsCloud=1
        unitsEnt=.5
        baseUnits = (unitsCloud * cloudAgents + unitsEnt * entAgents)

        if testType == 'http-server':
            perInterval =  baseUnits * httpTimeout

        elif testType == 'voice-call':
            perInterval = baseUnits * (duration+otherTimeout)

        elif testType == 'voice':
            perInterval = baseUnits * duration


        elif testType == 'page-load':
            # plHttpInt is HTTP Interval
            # interval is Page Load Interval

            perIntervalPageLoad = baseUnits * otherTimeout
            unitCostHourly=perIntervalPageLoad*(3600/interval)
            unitCost31d_page=unitCostHourly * 24 * 31

            if(interval>plHttpInt):
                perIntervalHttp = baseUnits * httpTimeout
                unitCostHourly=perIntervalHttp*((3600/plHttpInt)-(3600/interval))
                unitCost31d_http=unitCostHourly * 24 * 31
                unitCost31d=unitCost31d_http+unitCost31d_page
            else:
                unitCost31d=unitCost31d_page
            return(unitCost31d)



        else:
            perInterval = baseUnits * otherTimeout

    # Easy ones
    elif testType == "dnsp-domain":
        perInterval = 217
    elif testType == "dnsp-server":
        perInterval = 868
    elif testType == "bgp":
        interval=15*60
        perInterval = 8


    unitCostHourly=perInterval*(3600/interval)
    unitCost31d=unitCostHourly * 24 * 31
    return unitCost31d

def APIGetAgents(auth, aid):
    aid = "?aid="+aid
    # Define URL
    url = 'https://api.thousandeyes.com/v6/agents.json{}'.format(aid)

    # Obtain a list of agents
    response = requests.get(url, auth=auth)

    # Convert the response into a json python dictionary/list
    agentsdict = response.json()

    # Obtain the metrics
    agentslist = agentsdict['agents']

    return agentslist


def agentType(agentId,agents):

    # CAN GAIN EFFICIENCY BY MOVING THESE VARIABLES TO GLOBAL
    # INSTEAD OF REPOPULATING FOR EVERY TEST WITHIN THIS FUNCTION
    # but it works right now and I don't want to break anything
    cloudList=[]
    entList=[]
    for agent in agents:
        if agent['agentType']=='Cloud':
            cloudList.append(agent['agentId'])
        elif agent['agentType']=='Enterprise':
            entList.append(agent['agentId'])

    if agentId in cloudList:
        return "Cloud"
    else:
        return "Ent"

# Main
def APIUnitCalculator(username, token, aid, fileName):

    # list used to store test metadata
    # (this is what gets output to CSV at the end)
    testobjectlist = []

    # Define the test dictionary
    testdict = {}

    auth = APIAuthCreate(username, token)

    # Pull agent list for later
    agentsList = APIGetAgents(auth, aid)

    # Something to look at on the console
    print('Extracting test data..')

    # Get the test list
    tests = APIGetTests(auth, aid)

    # Loop through each test
    for test in tests:

        testData={}

        # Columns will be output in this order later. Order only affects output.
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
            'throughputDuration',
            'bgpMeasurements',
            'alertsEnabled',
            'domain',
            'liveShare',
            'dnsServers__serverName',
            'httpTimeLimit',
            'timeLimit',
            'ftpTimeLimit',
            'pageLoadTimeLimit',
            'sipTimeLimit',
            'duration',
            'direction',
            'targetAgentId'
        ]

        # only one of these fields should apply to each test
        # whichever field is found first will be assigned to testData['otherTimeout']
        comboFields=[
            'timeLimit',
            'ftpTimeLimit',
            'pageLoadTimeLimit',
            'sipTimeLimit'
        ]

        for field in testFields:
            if field in test.keys():
                if field in comboFields:
                    testData['otherTimeout']=test[field]
                else:
                    testData[field]=test[field]
            elif field not in comboFields:
                testData[field]="NULL"

        if "otherTimeout" not in testData.keys():
            testData["otherTimeout"]="NULL"

        testobjectlist.append(testData)


    # Access data within individual tests, calculate consumption
    for testObject in testobjectlist:
        curData=APIGetTestData(auth,testObject['testId'], aid)

        # count cloud agents per test
        searchCloud="\"agentType\":\"Cloud\""
        cloudAgents=curData.count(searchCloud)
        testObject['cloudAgents']=cloudAgents

        # count enterprise agents per test
        searchEnt="\"agentType\":\"Enterprise\""
        entAgents=curData.count(searchEnt)
        testObject['entAgents']=entAgents

        # count dns servers per test
        dnsServers=curData.count("\"serverName\"")

        # determine if target is Cloud or Enterprise agent (for A2A unit calculation)
        if testObject['type'] == 'agent-to-agent':
            targetAgentType=agentType(testObject['targetAgentId'],agentsList)
        else:
            targetAgentType="NULL"

        # calculate unit consumption
        if testObject['enabled'] is 1:
            testObject['unitCost31d']=testCost(testObject['type'],testObject['httpTimeLimit'],testObject['otherTimeout'],testObject['interval'],cloudAgents,entAgents,dnsServers,testObject['duration'],testObject['direction'],targetAgentType,testObject['httpInterval'])
        else:
            testObject['unitCost31d']="NULL"
        # ALL OUTPUT CODE HERE

    # WRITE TO CSV
    generateCSV(fileName, testobjectlist)
    return
