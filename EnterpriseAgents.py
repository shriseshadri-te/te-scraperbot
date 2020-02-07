import requests
import json
import os
import shutil
from util import APIAuthCreate, generateCSV

def APIGetAgents(auth,aid):
    # Define URL
    url = 'https://api.thousandeyes.com/v6/agents.json?agentTypes=ENTERPRISE&&aid={}'.format(aid)

    # Obtain a list of tests
    response = requests.get(url, auth=auth)

    # Convert the response into a json python dictionary/list
    agentsdict = response.json()

    # Obtain the metrics
    agentslist = agentsdict['agents']

    return agentslist

def APIEnterpriseAgents(username, token, aid, fileName):
    #list  used to store test metadata
    agentobjectlist = []

    # Define the test dictionary
    agentdict = {}

    # Create the auth
    auth = APIAuthCreate(username, token)
    print('Extracting test data..')

    # Get the tests
    agentlist = APIGetAgents(auth, aid)

    # Loop through each test
    for agents in agentlist:
        agentData={}
        agentFields=[
            'agentId',
            'agentName',
            'location',
            'countryId',
            'ipAddresses',
            'utilization',
            'targetForTests',
            'enabled',
            'agentType'
        ]

        for field in agentFields:
            if field in agents.keys():
                agentData[field]=agents[field]
            else:
                agentData[field]="NULL"
        agentobjectlist.append(agentData)
    # WRITE TO CSV
    generateCSV(fileName, agentobjectlist)
    return
