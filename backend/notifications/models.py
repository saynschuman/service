from backend.helpers import BaseModel
from django.db import models

class MessageNotification(BaseModel):
  text = models.CharField(max_length=250, blank=False)
  author = models.CharField(max_length=250, blank=False)
