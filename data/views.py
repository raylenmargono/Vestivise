import os
import logging
import json
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from Vestivise import permission
from Vestivise import settings
from Vestivise.Vestivise import VestiviseException, network_response
from data.models import Holding, Account
from dashboard.models import QuovoUser, ProgressTracker
from tasks import task_instant_link
from sources import mailchimp
from data.algos import (risk_return_profile, fees, returns, holding_types, stock_types, bond_types,
                        contribution_withdraws, returns_comparison, risk_age_profile, compound_interest,
                        portfolio_holdings)


@api_view(["GET"])
def demo_broker(request, module):
    json_file = open(os.path.join(settings.BASE_DIR, 'data/fixtures/demo_data.json'))
    demo_data = json.loads(json_file.read())
    if not demo_data.get(module):
        raise Http404
    return network_response(demo_data.get(module))


@api_view(["GET"])
@permission_classes((IsAuthenticated, permission.QuovoAccountPermission))
def broker(request, module):
    """
    Gets the output of the requested module.
    :param request: The request to be forwarded to the module algorithm.
    :param module: The name of the desired module algorithm.
    :param filters: The account fitlers to be excluded from calculations.
    :return: The response produced by the desired module algorithm.
    """
    if not request.user.is_authenticated():
        raise Http404("Please Log In before using data API")
    algo = get_algo_with_module_name(module)

    if algo:
        filters = request.GET.getlist('filters')
        if filters:
            ProgressTracker.track_progress(request.user, {"track_id" : "total_filters"})
        quovo_ids_exclude = request.user.profile.quovo_user.user_accounts\
                                   .filter(active=True, id__in=filters).values_list("quovo_id", flat=True)
        r = algo(request, acct_ignore=quovo_ids_exclude)
        return r
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


logger = logging.getLogger('quovo_sync')


# WEBHOOK FINISH SYNC
@api_view(['POST'])
@permission_classes((permission.QuovoWebHookPermission, ))
def finish_sync_handler(request):
    request_data = request.data
    user = request_data.get("user")
    user_id = user.get("id")
    account = request_data.get("account")
    account_id = account.get("id")
    logger.info("begin quovo sync logging: " + json.dumps(request.data))
    if request_data.get("action") == "completed" and request_data.get('sync').get('status') == 'good':
        if request_data.get("event") == "sync":
            try:
                handle_new_quovo_sync(user_id, account_id)
            except VestiviseException as e:
                e.log_error()
                return e.generate_error_response()
    if request_data.get("action") == "deleted":
        try:
            handle_quovo_delete(account_id, user_id)
        except Account.DoesNotExist:
            pass
    return network_response("")


def handle_new_quovo_sync(quovo_id, account_id):
    vestivise_quovo_user = QuovoUser.objects.get(quovo_id=quovo_id)
    email = vestivise_quovo_user.user_profile.user.email
    mailchimp.send_processing_holding_notification(email)
    # if the user has no current holdings it means that this is their first sync
    if not Account.objects.filter(quovo_id=account_id):
        user = get_user_model().objects.get(profile__quovo_user__quovo_id=quovo_id)
        ProgressTracker.track_progress(user, {"track_id": "did_link"})
        task_instant_link.delay(quovo_id, account_id)


def handle_quovo_delete(account_id, quovo_id):
    a = Account.objects.get(quovo_id=account_id)
    a.delete()
    vestivise_quovo_user = QuovoUser.objects.get(quovo_id=quovo_id)
    if vestivise_quovo_user.user_accounts.exists():
        vestivise_quovo_user.get_user_returns()
        vestivise_quovo_user.get_user_sharpe()
        vestivise_quovo_user.get_user_bond_equity()


def get_algo_with_module_name(module):
    if module == "holdingTypes":
        return holding_types
    elif module == "stockTypes":
        return stock_types
    elif module == "bondTypes":
        return bond_types
    elif module == "returns":
        return returns
    elif module == "contributionWithdraws":
        return contribution_withdraws
    elif module == "returnsComparison":
        return returns_comparison
    elif module == "riskReturnProfile":
        return risk_return_profile
    elif module == "riskAgeProfile":
        return risk_age_profile
    elif module == "fees":
        return fees
    elif module == "compInterest":
        return compound_interest
    elif module == "portfolioHoldings":
        return portfolio_holdings
    return None
