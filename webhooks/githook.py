from django.views.decorators.csrf import csrf_exempt
import os
from rest_framework.decorators import permission_classes
from Vestivise import permission
from Vestivise.settings import BASE_DIR


@permission_classes((permission.GitHubWebHookPermission, ))
@csrf_exempt
def git_post_receive(request):
    path = os.path.join(BASE_DIR, 'runScripts/')
    os.system("git pull")
    os.system(path + 'vestivise_startup.sh')