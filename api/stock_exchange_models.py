from django.db import models


class Index(models.Model):
    index = models.CharField(max_length=10)
    is_active = models.BooleanField()

    def __str__(self):
        return self.index

    class Meta:
        verbose_name_plural = 'indexes'

