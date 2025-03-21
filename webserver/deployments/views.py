from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Deployment

@login_required(login_url="/admin/login/")
def index(request):
    deployments = Deployment.objects.order_by("-created")
    context = {
        "deployments": deployments,
        "is_nav_sidebar_enabled": True,
        "has_permission": True
    }
    return render(request, "index.html", context)
