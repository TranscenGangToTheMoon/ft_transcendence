from django.shortcuts import render

def landing(request):
    return render(request, 'index.html', {})

def test(request):
    return render(request, 'test.html', {})

def login(request, extraArgs=None):
    return render(request, 'popuptest.html', {})