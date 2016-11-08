import codecs
import csv
from rest_framework import mixins
from rest_framework import viewsets
from Vestivise.Vestivise import *
import random, string
from dashboard.models import UserProfile
from humanResources.permissions import HumanResourceWritePermission, HumanResourcePermission
from serializers import SetUpUserSerializer
from models import SetUpUser
from dashboard.serializers import UserProfileReadSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django import forms

class DocumentForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
#VIEWS

@api_view(['POST'])
def add_employees_using_csv(request):
    try:
        confirmDocumentUpload(request.POST, request.FILES)
        csvfile = request.FILES.get('csv_file')
        user = request.user.humanResourceProfile
        generateSetUpUsers(csvfile, user.company)
        return network_response("Upload complete!")
    except CSVException as e:
        e.log_error()
        return e.generateErrorResponse()

class EmployeeManagementViewSet(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    '''
    Individual User API
    '''
    queryset = SetUpUser.objects.all()
    serializer_class = SetUpUserSerializer
    permission_classes = [HumanResourceWritePermission]

class EmployeeListView(viewsets.ReadOnlyModelViewSet):
    '''
    Employee List
    '''
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileReadSerializer
    permission_classes = [HumanResourcePermission]

    def list(self, request):
        queryset = UserProfile.objects.filter(company=request.user.humanResourceProfile.company)
        serializer = UserProfileReadSerializer(queryset, many=True)
        return Response(serializer.data)

#AUXILARY FUNCTIONS


def generateSetUpUsers(file, company):
    '''
    Accepts csv file and creates new users
    @param file: csv file with field parameters
    @param company: name of the company
    '''

    csv_reader = csv.reader(file)

    datas = []
    for line in csv_reader:
        if len(line) < 1:
            #todo handle empty row
            pass
        data = {}
        random_string = generateRandomString()
        data["magic_link"] = random_string
        data["company"] = company
        data["email"] = line[0]
        datas.append(data)
    addEmployee(datas, True)


def addEmployee(datas, many):
    '''
    Create employee
    @param datas: datas could be list or single object
    @param many: if multiple employees
    '''
    serializer = SetUpUserSerializer(data=datas, many=many)
    if serializer.is_valid():
        serializer.save()
    else:
        raise CSVException(serializer.errors)


def generateRandomString(stop=0, length=15):
    '''
    Generates random string for magic link
    '''
    result = ''.join(random.choice(string.lowercase) for i in range(length))
    if SetUpUser.objects.filter(magic_link=result).exists() and stop != 5:
        result = generateRandomString(stop=stop+1)
    return result


def confirmDocumentUpload(post, file):
    form = DocumentForm(post, file)
    if form.is_valid():
        return True
    raise CSVException(form.errors)
