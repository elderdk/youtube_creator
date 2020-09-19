from django.shortcuts import render
from django.http import HttpResponse
from .funcs import make_subs

# Create your views here.
def scrape(request):
    make_subs()
    return HttpResponse('scraped')
