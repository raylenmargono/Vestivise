from django.shortcuts import render
from models import *
from serializers import *
from rest_framework import viewsets
from rest_framework import mixins
# Create your views here.

class EmailViewSet(mixins.CreateModelMixin,
                mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
        queryset = Email.objects.all()
        serializer_class = EmailSerializer

        def perform_create(self, serializer):
            instance = serializer.save()
            refrees = Referal.objects.filter(email=instance.email)
            for r in refrees:
                refree = r.refree
                refree.acceptedEmails += 1
                r.accepted = True
                refree.save()
                r.save()
                # send email to r.refree

class ReferalViewSet(mixins.CreateModelMixin,
                mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
        queryset = Referal.objects.all()
        serializer_class = ReferalSerializer
