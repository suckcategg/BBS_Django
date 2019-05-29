from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
def article_list(request):
    return HttpResponse("Hello_World!")