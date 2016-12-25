from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
from rest_framework.decorators import permission_classes
from Vestivise import permission
from Vestivise.settings import BASE_DIR
import git


@permission_classes((permission.GitHubWebHookPermission, ))
@csrf_exempt
def git_post_receive(request):
    path = os.path.join(BASE_DIR, 'runScripts/')
    g = git.cmd.Git(BASE_DIR)
    g.pull()
    os.system(path + 'vestivise_startup.sh')
    return HttpResponse("Success")