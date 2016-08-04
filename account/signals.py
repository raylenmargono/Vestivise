from django.db.models.signals import post_save
from django.dispatch import receiver
from models import UserProfile, BasicAccount
from data.models import UserData


@receiver(post_save, sender=UserProfile)
def on_user_profile_create(sender, instance, created, **kwargs):
    if created:
        UserData.objects.create(userProfile=instance)
        BasicAccount.objects.create(userProfile=instance)

#TODO automatically assign basic modules
@receiver(post_save, sender=BasicAccount)
def on_basic_account_create(sender, instance, created, **kwargs):
    if created:
        pass
