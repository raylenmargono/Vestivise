from celery.schedules import crontab
from celery.task import periodic_task
from django.contrib.auth import get_user_model

from dashboard.models import UserTracking


@periodic_task(
    run_every=(crontab(minute=0, hour=0)),
    name="task_track_user",
    ignore_result=True
)
def task_track_user():
    UserTracking.objects.create(count=get_user_model().objects.all().count())
