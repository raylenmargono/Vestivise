import codecs
import csv
from rest_framework import mixins
from rest_framework import viewsets
from Vestivise.Vestivise import VestErrors, network_response
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
    except VestErrors.CSVException as e:
        return VestErrors.VestiviseException.generateErrorResponse(e)

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

    csv_dict = csv.DictReader(file)

    checkForHeaderError(csv_dict.fieldnames)

    datas = []
    for line in csv_dict:
        success, data = createSetUpUserData(line)
        if not success: raise VestErrors.CSVException("Detected some empty fields")
        random_string = generateRandomString()
        data["magic_link"] = random_string
        data["company"] = company
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
        raise VestErrors.CSVException(serializer.errors)


def generateRandomString(length=15):
    '''
    Generates random string for magic link
    '''
    return ''.join(random.choice(string.lowercase) for i in range(length))


def createSetUpUserData(csv_line):
    '''
    Returns a payload of data needed for SetUpProfileSerailizer
    '''
    for field, value in csv_line.iteritems():
        if not value:
            return (False, csv_line)
    return (True, csv_line)


def confirmDocumentUpload(post, file):
    form = DocumentForm(post, file)
    if form.is_valid():
        return True
    raise VestErrors.CSVException(form.errors)


def checkForHeaderError(header):
    '''
    Check for any keywords missing from first line of csv
    '''
    key_words = ['email', 'first_name', 'last_name']
    errors = []
    for word in key_words:
        if not word in header:
            errors.append(word)
    if errors:
        raise VestErrors.CSVException("Missing columns")