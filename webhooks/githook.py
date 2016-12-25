from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
from rest_framework.decorators import permission_classes
from Vestivise import permission
from Vestivise.settings import BASE_DIR
import subprocess

@permission_classes((permission.GitHubWebHookPermission, ))
@csrf_exempt
def git_post_receive(request):
    # this is to run the script
    path = os.path.join(BASE_DIR, 'runScripts/')
    subprocess.call(["git", "pull"])
    os.system(path + 'vestivise_git_startup.sh')
    subprocess.call(["service", "gunicorn", "start"])
    return HttpResponse("Success")