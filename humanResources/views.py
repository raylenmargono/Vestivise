from django.shortcuts import render
import csv
from Vestivise.Vestivise import VestErrors
# Create your views here.



#AUXILARY FUNCTIONS

'''
Accepts csv file and creates new users
@param file: csv file with field parameters
@param company: name of the company
'''
def generateSetUpUsers(file, company):
    reader = csv.reader(file)
    headers = reader.next()

    has_error, errors = checkForHeaderError(headers)
    if has_error:
        raise VestErrors.VestiviseException("Header error: headers not found %s" % (",".join(headers),))

    header_order = {}

    for i in range(len(headers)):
        header_order[i] = headers[i]

    

def checkForHeaderError(headers):
    key_words = ['email', 'first_name', 'last_name']
    errors = []
    for word in key_words:
        if not word in headers:
            errors.append(word)
    if not errors:
        return (False, errors)
    return (True, errors)
