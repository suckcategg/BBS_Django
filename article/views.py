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
from django.db.models import Q
from comment.models import Comment
from .models import ArticleColumn
# 列表页  --翻页
def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)

def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    article.total_views+=1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)

    # 新增了md.toc对象
    context = {'article': article, 'toc': md.toc, 'comments':comments}

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
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            # 保存 tags的多读多关系
            article_post_from._save_m2m()
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
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_from,'columns':columns}
        # 返回模板
        return render(request, 'article/create.html',context)

@login_required(login_url='/userprofile/login/')
def article_delete(request, id):

    # 记住来源的url，如果没有则设置为首页('/')
    # request.session['last_page'] = request.META.get('HTTP_REFERER', '/')
    user = request.session.get('_auth_user_id')
    # 根据id获取文章
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        messages.error(request, "你没有权限删除此文章")
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
    if request.user != article.author:
    # if str(article.author_id) != str(user):
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

            # 新增的代码
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            return redirect("article:article_detail",id=id)
        else:
            messages.error(request, "表单内容有误，请重新填写！")
            context = {'article': article, 'article_post_form': article_post_form}
            return render(request, 'article/update.html',context)


    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
        }
        return render(request, 'article/update.html', context)
# def return_to_list(request):
#     return redirect("article:article_list")
