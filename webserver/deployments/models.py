from django.db import models

DEPLOYMENT_STATUS = {
    "P": "Pending",
    "R": "Running",
    "C": "Completed",
    "F": "Failed"
}

# Create your models here.
class Environment(models.Model):
    uuid = models.UUIDField()
    name = models.CharField(max_length=200)
    created = models.DateTimeField("date published")
    deleted = models.DateTimeField(default=None, blank=True, null=True)


class Deployment(models.Model):
    uuid = models.UUIDField()
    created = models.DateTimeField("date published")
    name = models.CharField(max_length=200)
    endpoint = models.CharField(max_length=1024)
    status = models.CharField(max_length=10, choices=DEPLOYMENT_STATUS)
    meta = models.CharField(max_length=1024)
    s3_bucket = models.CharField(max_length=254)
    deleted = models.DateTimeField(default=None, blank=True, null=True)
    environment = models.ForeignKey("deployments.Environment", on_delete=models.CASCADE)


class Files(models.Model):
    filename = models.CharField(max_length=1024)
    uuid = models.UUIDField()
    created = models.DateTimeField("date published")
    shasum = models.CharField(max_length=200)
    s3_key = models.CharField(max_length=1024)
    s3_version = models.CharField(max_length=254)
    deleted = models.DateTimeField(default=None, blank=True, null=True)
    deployment = models.ForeignKey("deployments.Deployment", on_delete=models.CASCADE)


class Job(models.Model):
    uuid = models.UUIDField()
    created = models.DateTimeField("date published")
    job = models.CharField(max_length=200)
    status = models.CharField(max_length=1024)
    deleted = models.DateTimeField(default=None, blank=True, null=True)
    environment = models.ForeignKey("deployments.Environment", on_delete=models.CASCADE)
    deployment = models.ForeignKey("deployments.Deployment", on_delete=models.CASCADE)
