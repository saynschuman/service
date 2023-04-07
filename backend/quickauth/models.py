from django.db import models
from solo.models import SingletonModel

class QuickLogin(SingletonModel):
  client_login = models.CharField(max_length=100, blank=True, null=True, default=None)
  curator_login = models.CharField(max_length=100, blank=True, null=True, default=None)
  moderator_login = models.CharField(max_length=100, blank=True, null=True, default=None)
  admin_login = models.CharField(max_length=100, blank=True, null=True, default=None)
  client_password = models.CharField(max_length=100, blank=True, null=True, default=None)
  curator_password = models.CharField(max_length=100, blank=True, null=True, default=None)
  moderator_password = models.CharField(max_length=100, blank=True, null=True, default=None)
  admin_password = models.CharField(max_length=100, blank=True, null=True, default=None)
