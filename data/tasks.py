from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger
from datetime import timedelta
import tasks

logger = get_task_logger('nightly_process')


@periodic_task(
    run_every=(crontab(minute=0, hour=0)),
    name="task_nighly_process",
    ignore_result=True
)
def task_nighly_process():
    logger.info('Starting nightly process')
    logger.info('Updating quovo user holdings')
    tasks.updateQuovoUserHoldings()
    logger.info('Updating quovo user holding information')
    tasks.updateHoldingInformation()
    logger.info('Updating user completeness')
    tasks.updateQuovoUserCompleteness()
    logger.info('Updating user returns')
    tasks.updateUserReturns()
    logger.info('Nightly process ended')