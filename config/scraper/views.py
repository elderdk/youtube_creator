from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def scrape(request):
    if request.method == 'POST':
        print(request.POST['action'])
        return HttpResponse("hello")
    else:
        return HttpResponse("hello")
