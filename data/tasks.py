from celery.schedules import crontab
from celery.task import periodic_task, task
from celery.utils.log import get_task_logger
import nightly_process
from Vestivise import Vestivise
from dashboard.models import QuovoUser
from sources import mailchimp

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
    nightly_process.update_quovo_user_accounts()
    logger.info('Updating quovo user portfolios')
    nightly_process.update_quovo_user_portfolios()
    logger.info('Updating quovo user holdings')
    nightly_process.update_quovo_user_holdings()
    logger.info('Updating quovo user holding information')
    nightly_process.update_holding_information()
    logger.info('Updating user completeness')
    nightly_process.update_quovo_user_completeness()
    logger.info('Updating user returns')
    nightly_process.update_user_returns()
    logger.info('Updating user transactions')
    nightly_process.update_user_history()
    logger.info('Updating user fees')
    nightly_process.update_user_fees()
    logger.info('Nightly process ended')


@task(name="instant_link")
def task_instant_link(quovo_user_id, account_id):
    instant_link_logger = get_task_logger('instant_link')

    quovo_user = QuovoUser.objects.get(quovo_id=quovo_user_id)
    # update account
    instant_link_logger.info('updating user account: {}'.format(quovo_user_id))
    quovo_user.update_accounts()
    # update portfolio
    instant_link_logger.info('updating user portfolio: {}'.format(quovo_user_id))

    quovo_user.update_portfolios()
    # update holdings
    instant_link_logger.info('updating user holding: {}'.format(quovo_user_id))

    new_holdings = quovo_user.get_new_holdings()
    if not quovo_user.current_holdings_equal_holding_json(new_holdings):
        instant_link_logger.info('new holdings found for user: {}'.format(quovo_user_id))
        quovo_user.set_current_holdings(new_holdings)
    if not quovo_user.has_completed_user_holdings():
        instant_link_logger.info('user has some holdings that are not completed: {}'.format(quovo_user_id))
        quovo_user.is_completed = False

    quovo_user.save()
    # get holding information
    for current_holdings in quovo_user.get_current_holdings():
        instant_link_logger.info('updating holding {} for user: {}'.format(current_holdings, quovo_user_id))
        nightly_process.update_holding(current_holdings.holding)
    # update user display holdings
    instant_link_logger.info('updating display holding user: {}'.format(quovo_user_id))
    quovo_user.update_display_holdings()
    if quovo_user.has_completed_user_holdings():
        quovo_user.is_completed = True
        quovo_user.save()
    if quovo_user.user_accounts.exists():
        account = quovo_user.user_accounts.filter(quovo_id=account_id)
        if account.exists() and account.first():
            holdings = account.first().account_current_holdings.all()
            for dh in holdings:
                holding = dh.holding
                if holding.is_completed():
                    mailchimp.send_holding_processing_complete_notification(quovo_user.user_profile.user.email)
                    break
    # update user stats info
    instant_link_logger.info('updating user stats: {}'.format(quovo_user_id))
    for acct in quovo_user.user_accounts.all():
        acct.get_account_returns()
    quovo_user.get_user_sharpe()
    quovo_user.get_user_bond_equity()
    # update user transactions
    instant_link_logger.info('updating transactions user: {}'.format(quovo_user_id))
    quovo_user.update_transactions()
    instant_link_logger.info('updating fees user: {}'.format(quovo_user_id))
    quovo_user.update_fees()
    instant_link_logger.info('instant link completed for user: {}'.format(quovo_user_id))
