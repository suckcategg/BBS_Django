# 引入redirect重定向模块
from django.shortcuts import render, redirect
import markdown
from .models import ArticlePost
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入HttpResponse
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from userprofile.models import Profile
from django.core.paginator import Paginator
# 列表页  --翻页
def article_list(request):
    #return HttpResponse("Hello_World!")
    article_list = ArticlePost.objects.all()
    # 每页显示的文章数
    pagintor = Paginator(article_list,6)
    # 获取页码
    page = request.GET.get('page')
    # 页码内容反个 articles
    articles = pagintor.get_page(page)

    context = {'articles':articles}
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
@login_required(login_url='/userprofile/login/')
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
            new_article.author = User.objects.get(id=request.user.id)
            # 将文章保存到数据库重
            new_article.save()
            # 返回文章列表
            return redirect("article:article_list")
        else:
            messages.error(request, "表单内容有误，请重新填写！")
            return render(request, 'article/create.html')
            # article_post_form = ArticlePostForm()
            # context = {'article_post_form': article_post_form}
            # return HttpResponse("表单内容有误，请重新填写！")
    else:
        # 创建表单类实例
        article_post_from = ArticlePostForm()
        # 赋值上下文
        context = {'article_post_form': article_post_from}
        # 返回模板
        return render(request, 'article/create.html',context)

@login_required(login_url='/userprofile/login/')
def article_delete(request, id):

    # 记住来源的url，如果没有则设置为首页('/')
    # request.session['last_page'] = request.META.get('HTTP_REFERER', '/')
    user = request.session.get('_auth_user_id')
    # 根据id获取文章
    article = ArticlePost.objects.get(id=id)
    if str(article.author_id) != str(user):
        messages.error(request, "你没有权限删除此文章")
        # return render(request, 'article/delete.html', {'script': "alert", 'wrong': '你没有权限删除此文章',})
        # return redirect("article:article_list")
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/detail.html', context)
    else:
        # 调用.delete方法删除
        article.delete()
    return redirect("article:article_list")

@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    """
        更新文章的视图函数
        通过POST方法提交表单，更新titile、body字段
        GET方法进入初始表单页面
        id： 文章的 id
    """
    user = request.session.get('_auth_user_id')

    article = ArticlePost.objects.get(id=id)
    #print(user,article.author_id)
    if str(article.author_id) != str(user):
        messages.error(request, "你没有权限修改此文章")
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/detail.html', context)

    if request.method == "POST":
        # if str(article.author_id) != str(user):
        #     messages.error(request, "你没有权限修改此文章")
        #     article_post_form = ArticlePostForm()
        #     context = {'article': article, 'article_post_form': article_post_form}
        #     return render(request, 'article/detail.html', context)
        #     #return HttpResponse("你没有权限修改此文章")
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("article:article_detail",id=id)
        else:
            messages.error(request, "表单内容有误，请重新填写！")
            context = {'article': article, 'article_post_form': article_post_form}
            return render(request, 'article/update.html',context)


    else:
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/update.html', context)
# def return_to_list(request):
#     return redirect("article:article_list")
