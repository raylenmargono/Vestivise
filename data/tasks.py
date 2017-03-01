from celery.schedules import crontab
from celery.task import periodic_task, task
from celery.utils.log import get_task_logger
import nightlyProcess
from Vestivise import Vestivise
from Vestivise.mailchimp import sendHoldingProcessingCompleteNotification
from dashboard.models import QuovoUser

logger = get_task_logger('nightly_process')


def nightly_process_proxy(request):
    task_nightly_process()
    return Vestivise.network_response("Nightly process is done.")

@periodic_task(
    run_every=(crontab(minute=0, hour=5)),
    name="task_nighly_process",
    ignore_result=True
)
def task_nightly_process():
    logger.info('Starting nightly process')
    logger.info('Updating quovo user accounts')
    nightlyProcess.updateQuovoUserAccounts()
    logger.info('Updating quovo user portfolios')
    nightlyProcess.updateQuovoUserPortfolios()
    logger.info('Updating quovo user holdings')
    nightlyProcess.updateQuovoUserHoldings()
    logger.info('Updating quovo user holding information')
    nightlyProcess.updateHoldingInformation()
    logger.info('Updating user completeness')
    nightlyProcess.updateQuovoUserCompleteness()
    logger.info('Updating user returns')
    nightlyProcess.updateUserReturns()
    logger.info('Updating user transactions')
    nightlyProcess.updateUserHistory()
    logger.info('Nightly process ended')

@task(name="instant_link")
def task_instant_link(quovo_user_id, account_id):
    instant_link_logger = get_task_logger('instant_link')

    quovo_user = QuovoUser.objects.get(quovoID=quovo_user_id)
    #update account
    instant_link_logger.info('updating user account: %s' % (quovo_user_id,))
    quovo_user.updateAccounts()
    #update portfolio
    instant_link_logger.info('updating user portfolio: %s' % (quovo_user_id,))

    quovo_user.updatePortfolios()
    #update holdings
    instant_link_logger.info('updating user holding: %s' % (quovo_user_id,))

    newHolds = quovo_user.getNewHoldings()
    if not quovo_user.currentHoldingsEqualHoldingJson(newHolds):
        instant_link_logger.info('new holdings found for user: %s' % (quovo_user_id,))
        quovo_user.setCurrentHoldings(newHolds)
    if not quovo_user.hasCompletedUserHoldings():
        instant_link_logger.info('user has some holdings that are not completed: %s' % (quovo_user_id,))
        quovo_user.isCompleted = False

    quovo_user.save()
    #get holding information
    for current_holdings in quovo_user.getCurrentHoldings():
        instant_link_logger.info('updating holding %s for user: %s' % (current_holdings, quovo_user_id,))
        nightlyProcess.update_holding(current_holdings.holding)
    #update user display holdings
    instant_link_logger.info('updating display holding user: %s' % (quovo_user_id,))
    quovo_user.updateDisplayHoldings()
    if quovo_user.hasCompletedUserHoldings():
        quovo_user.isCompleted = True
        quovo_user.save()
    if quovo_user.userAccounts.exists():
        account = quovo_user.userAccounts.filter(quovoID=account_id)
        if account.exists() and account.first():
            holdings = account.first().accountCurrentHoldings.all()
            for dh in holdings:
                holding = dh.holding
                if holding.isCompleted():
                    sendHoldingProcessingCompleteNotification(quovo_user.userProfile.user.email)
                    break
    #update user stats info
    instant_link_logger.info('updating user stats: %s' % (quovo_user_id,))
    for acct in quovo_user.userAccounts.all():
        if hasattr(acct, 'accountReturns'):
            acct.getAccountReturns()
    quovo_user.getUserSharpe()
    quovo_user.getUserBondEquity()
    #update user transactions
    instant_link_logger.info('updating transactions user: %s' % (quovo_user_id,))
    quovo_user.updateTransactions()
    instant_link_logger.info('instant link completed for user: %s' % (quovo_user_id,))
