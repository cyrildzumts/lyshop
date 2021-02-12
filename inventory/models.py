from django.db import models

# Create your models here.

class Visitor(models.Model):
    url = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    hits = models.PositiveIntegerField(default=0)


class UniqueIP(models.Model):
    ip_address = models.GenericIPAddressField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    hits = models.PositiveIntegerField(default=0)


class FacebookLinkHit(models.Model):
    fbclid = models.CharField(max_length=256)
    ip_address = models.GenericIPAddressField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    hits = models.PositiveIntegerField(default=0)

class GoogleAdsHit(models.Model):
    gclid = models.CharField(max_length=256)
    ip_address = models.GenericIPAddressField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    hits = models.PositiveIntegerField(default=0)

class SuspiciousRequest(models.Model):
    url = models.CharField(max_length=512)
    ip_address = models.GenericIPAddressField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    hits = models.PositiveIntegerField(default=0)


    

