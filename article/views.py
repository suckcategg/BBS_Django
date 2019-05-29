# 引入redirect重定向模块
from django.shortcuts import render, redirect
import markdown
from .models import ArticlePost
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入HttpResponse
from django.http import HttpResponse
# 引入User模型
from django.contrib.auth.models import User



def article_list(request):
    #return HttpResponse("Hello_World!")
    article = ArticlePost.objects.all()
    context = {'articles':article}
    return render(request,'article/list.html',context)

def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)

    article.body = markdown.markdown(article.body,
        extensions = [
        'markdown.extensions.extra',

        'markdown.extensions.codehilite',
        ])
    context = {'article': article}
    return render(request, 'article/detail.html', context)

def article_create(request):
    # 判断用户是否提交空数据
    if request.method == "POST":
        # 将提交的数据复制到表单
        article_post_from = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型要求
        if article_post_from.is_valid():
            # 保存数据但不提交到数据库
            new_article = article_post_from.save(commit=False)
            # 指定数据库中 id 为1的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=1)
            # 将文章保存到数据库重
            new_article.save()
            # 返回文章列表
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写！")
    else:
        # 创建表单类实例
        article_post_from = ArticlePostForm()
        # 赋值上下文
        context = {'article_post_dorm': article_post_from}
        # 返回模板
        return render(request, 'article/create.html',context)




