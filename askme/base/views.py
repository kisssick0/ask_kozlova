from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    return render(request, 'base/index.html')


def tag(request):
    return render(request, 'base/tag.html')


def question(request):
    return render(request, 'base/question.html')


def login(request):
    return render(request, 'base/login.html')


def register(request):
    return render(request, 'base/signup.html')


def ask(request):
    return render(request, 'base/ask.html')


def settings(request):
    return render(request, 'base/settings.html')
