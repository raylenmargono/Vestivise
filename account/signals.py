from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import *
from data.models import UserData


@receiver(post_save, sender=UserProfile)
def on_user_profile_create(sender, instance, created, **kwargs):
    if created:
        UserData.objects.create(userProfile=instance)
        BasicAccount.objects.create(userProfile=instance)


@receiver(post_save, sender=BasicAccount)
def on_basic_account_create(sender, instance, created, **kwargs):
    if created:
        modules = Module.objects.filter(account="BasicAccount")
        for module in modules:
            AccountModule.objects.create(module=module, account=instance)
