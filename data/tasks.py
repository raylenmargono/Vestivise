from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger
import nightlyProcess
from Vestivise import Vestivise

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
