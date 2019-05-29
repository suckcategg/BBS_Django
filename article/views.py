from django.shortcuts import render

# Create your views here.
from .models import ArticlePost
from django.http import HttpResponse
def article_list(request):
    #return HttpResponse("Hello_World!")
    article = ArticlePost.objects.all()
    context = {'articles':article}
    return render(request,'article/list.html',context)

def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)
    context = {'article': article}
    return  render(request, 'article/detail.html', context)