import os
import subprocess

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from Vestivise import permission
from Vestivise.settings import BASE_DIR


@permission_classes((permission.GitHubWebHookPermission, ))
@csrf_exempt
def git_post_receive(request):
    # this is to run the script
    path = os.path.join(BASE_DIR, 'run_scripts/')
    subprocess.call(["git", "pull"])
    os.system(path + 'vestivise_startup.sh')
    return HttpResponse("Success")