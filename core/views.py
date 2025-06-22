from django.shortcuts import render

from .action import run_quake_safety

# Create your views here.
def index(request):
    context = run_quake_safety()
    return render(request, "core/index.html", context)