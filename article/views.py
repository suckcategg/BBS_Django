from django.shortcuts import render

# Create your views here.
from .models import ArticlePost
from django.http import HttpResponse
def article_list(request):
    #return HttpResponse("Hello_World!")
    article = ArticlePost.objects.all()
    context = {'articles':article}
    return render(request,'article/list.html',context)

