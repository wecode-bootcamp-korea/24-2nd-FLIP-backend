import datetime

from django.db import models

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    is_deleted  = models.BooleanField(default=False)
    deleted_at  = models.DateTimeField(blank=True, null=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.save()

    def restore(self):
        self.is_delete = False
        self.save()

    class Meta:
        abstract = True

