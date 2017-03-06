from celery.schedules import crontab
from celery.task import periodic_task
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import datetime

from Vestivise.mailchimp import inactivity_reminder, not_linked_account
from dashboard.models import ProgressTracker


def send_inactive_user_email():
    last_month = datetime.today() - timedelta(days=30)
    for progress in ProgressTracker.objects.filter(last_dashboard_view__lte=last_month):
        user = progress.profile.user
        email = user.email
        inactivity_reminder(email)



def send_unlink_email():
    three_days_ago = datetime.today() - timedelta(days=3)
    for user in get_user_model()\
            .objects.annotate(num_accounts=Count('profile__quovoUser__userAccounts'))\
            .filter(profile__createdAt=three_days_ago, num_accounts=0):
        email = user.email
        not_linked_account(email)


@periodic_task(
    run_every=(crontab(minute=0, hour=13)),
    name="task_nighly_process",
    ignore_result=True
)
def task_send_activity_emails():
    send_inactive_user_email()
    send_unlink_email()
