from django.db import models

# Create your models here.

class Visitor(models.Model):
    url = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    hits = models.PositiveIntegerField(default=0)


class UniqueIP(models.Model):
    id_adress = models.GenericIPAddressField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    hits = models.PositiveIntegerField(default=0)

