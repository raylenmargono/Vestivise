from django.shortcuts import render
import csv

from rest_framework import mixins
from rest_framework import viewsets

from Vestivise.Vestivise import VestErrors
import random, string
from serializers import SetUpUserSerializer
from models import SetUpUser
from dashboard.serializers import UserProfileWriteSerializer
import re
from rest_framework.views import APIView

#VIEWS

'''
Individual User API
'''
class EmployeeManagementViewSet(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    queryset = SetUpUser.objects.all()
    serializer_class = SetUpUserSerializer
    #TODO permission is user logged in is hr and belongs to same company
    #permission_classes = [IsAccountAdminOrReadOnly]

'''
Employee List
'''
class EmployeeListView(viewsets.ReadOnlyModelViewSet):
    queryset = SetUpUser.objects.all()
    serializer_class = SetUpUserSerializer
    #TODO permission is user logged in is hr and belongs to same company
    #permission_classes = [IsAccountAdminOrReadOnly]


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
    if has_error: raise VestErrors.VestiviseException("Header error: headers not found %s" % (",".join(headers),))

    header_order = {}
    for i in range(len(headers)):
        header_order[i] = headers[i]

    # TODO skip header?
    datas = []
    for line in headers:
        error, data = createSetUpUserData(header_order, line)
        if error: raise VestErrors.VestiviseException("Value is missing in one of the columns")
        random_string = generateRandomString()
        data["magic_link"] = random_string
        data["company"] = company
        datas.append(data)
    addEmployee(datas, True)

'''
Create employee
@param datas: datas could be list or single object
@param many: if multiple employees
'''
def addEmployee(datas, many):
    serializer = SetUpUserSerializer(data=datas, many=many)
    if serializer.is_valid():
        serializer.save()
    else:
        raise VestErrors.VestiviseException(serializer.errors)

'''
Generates random string for magic link
'''
def generateRandomString(length=15):
    return ''.join(random.choice(string.lowercase) for i in range(length))

'''
Returns a payload of data needed for SetUpProfileSerailizer
'''
def createSetUpUserData(header_order, next_line):
    data = {}
    for index, value in header_order.iteritems():
        field = next_line[index]
        if not field:
            return (True, data)
        data[value] = field
    return (False, data)

'''
Check for any keywords missing from first line of csv
'''
def checkForHeaderError(headers):
    key_words = ['email', 'first_name', 'last_name']
    errors = []
    for word in key_words:
        if not word in headers:
            errors.append(word)
    if not errors:
        return (False, errors)
    return (True, errors)
