from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
import data.algos
from django.http import Http404
from django.http import HttpResponseForbidden
from Vestivise import permission
from Vestivise.Vestivise import VestiviseException, QuovoWebhookException
from data.models import Holding
from dashboard.models import QuovoUser
from Vestivise import mailchimp

def holdingEditor(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    return render(request, "data/holdingEditorView.html")


def broker(request, module):
    """
    Gets the output of the requested module.
    :param request: The request to be forwarded to the module algorithm.
    :param module: The name of the desired module algorithm.
    :return: The response produced by the desired module algorithm.
    """
    if not request.user.is_authenticated() and not "Test" in module:
        raise Http404("Please Log In before using data API")
    module = module
    if hasattr(data.algos, module):
        method = getattr(data.algos, module)
        return method(request)
    else:
        raise Http404("Module not found")

class HoldingSerializer(generics.ListAPIView):
    serializer_class = Holding
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = Holding.objects.all()

        completed = self.request.query_params.get('completed', None)
        if completed is not None:
            queryset = Holding.objects.filter(cusip__isnull=True)

        return queryset

class HoldingDetailView(generics.UpdateAPIView):
    serializer_class = Holding
    permission_classes = (IsAdminUser,)
    queryset = Holding.objects.all()


# WEBHOOK FINISH SYNC
@api_view(['POST'])
@permission_classes((permission.QuovoWebHookPermission, ))
def finishSyncHandler(request):
    data = request.data
    if data.get("event") == "sync":
        user = data.get("user")
        user_id = user.get("id")
        try:
            handleNewQuovoSync(user_id)
        except VestiviseException as e:
            e.log_error()

def handleNewQuovoSync(quovo_id):
    try:
        vestivise_quovo_user = QuovoUser.objects.get(quovoID=quovo_id)
        # if the user has no current holdings it means that this is their first sync
        if not hasattr(vestivise_quovo_user, "userCurrentHoldings"):
            holdings = vestivise_quovo_user.getNewHoldings()
            vestivise_quovo_user.setCurrentHoldings(holdings)

            email = vestivise_quovo_user.userProfile.user.email

            if not vestivise_quovo_user.hasCompletedUserHoldings():
                # alert number monkeys
                for holding in holdings["positions"]:
                    secname = holding.get("ticker_name")
                    if not Holding.isIdentifiedHolding(secname):
                        mailchimp.alertIdentifyHoldings(secname)
            mailchimp.sendProcessingHoldingNotification(email)

    except QuovoUser.DoesNotExist:
        raise QuovoWebhookException("User {0} does not exist".format(quovo_id))
