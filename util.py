from requests.auth import HTTPBasicAuth
import csv
def APIAuthCreate(username, password):
    # Create auth
    auth = (username, password)
    return auth

def generateCSV(fileName, data):
    toCSV = data
    keys = toCSV[0].keys()
    with open('./reports/' + fileName + '.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)
    print('Test data written to file.')
    return
