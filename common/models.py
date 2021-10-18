import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

"""
Model in which other models inherit
"""

class BaseModel(models.Model):
    id = models.UUIDField(_('id'), primary_key = True, default = uuid.uuid4)
    date_created = models.DateTimeField(_('Date Created'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date Updated'), auto_now = True)

    class Meta:
        abstract = True