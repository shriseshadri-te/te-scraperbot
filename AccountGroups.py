import requests
import csv
from requests.auth import HTTPBasicAuth
import json
import os
import shutil
from util import APIAuthCreate, generateCSV

def APIGetaid(auth):
    # Define URL
    url = 'https://api.thousandeyes.com/v7/account-groups.json'

    # Obtain a list of tests
    response = requests.get(url, auth=auth)

    # Convert the response into a json python dictionary/list
    agdict = response.json()

    # Obtain the metrics
    aglist = agdict['accountGroups']

    return aglist

def APIAccountGroups(username, token, fileName):
    #list  used to store test metadata
    agobjectlist = []


    # Define the test dictionary
    aiddict = {}

    # Create the auth
    auth = APIAuthCreate(username, token)
    print('Extracting test data..')

    # Get the tests
    ags = APIGetaid(auth)

    # Loop through each test
    for accountGroups in ags:

        agData={}

        agFields=[
            'accountGroupName',
            'aid',
            'organizationName',
            'default'

        ]

        for field in agFields:
            if field in accountGroups.keys():
                agData[field]=accountGroups[field]
            else:
                agData[field]="NULL"

        agobjectlist.append(agData)

    # WRITE TO CSV
    return generateCSV(fileName, agobjectlist)

