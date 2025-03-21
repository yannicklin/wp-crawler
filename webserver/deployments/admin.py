from django.contrib import admin

from .models import Environment, Deployment, Files, Job

# Register your models here.
admin.site.register(Environment)
admin.site.register(Deployment)
admin.site.register(Files)
admin.site.register(Job)
