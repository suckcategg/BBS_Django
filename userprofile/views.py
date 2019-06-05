from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import ProfileFrom
from .models import Profile
from django.contrib import messages

# Create your views here.


def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect("article:article_list")
            else:
                messages.error(request, "表单内容有误，请重新填写！")
                # user_login_form = UserLoginForm()
                # context = {'userprofile': data, 'user_login_form': UserLoginForm}
                return redirect('userprofile:login')
                #return HttpResponse("账号或密码输入错误，请重新输入！")
        else:
            messages.error(request, "账号或密码输入不合法")
            return redirect('userprofile:login')
            # return HttpResponse("账号或密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'from': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        messages.error(request, "请使用GET或POST请求数据")
        return redirect('userprofile:login')
        # return HttpResponse("请使用GET或POST请求数据")
def user_logout(request):
    logout(request)
    return redirect("article:article_list")

def user_register(request):
    if request.method =='POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect("article:article_list")
        else:
            messages.error(request, "注册表单输入有误，请重新输入")
            user_register_form = UserRegisterForm(data=request.POST)
            context = {'form': user_register_form}
            return render(request, 'userprofile/register.html', context)
            # return HttpResponse("注册表单输入有误，请重新输入")
    elif request.method == "GET":
        user_register_form = UserRegisterForm
        context = {'data':data, 'form': user_register_form}
        return render(request, 'userprofile/register.html',context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


@login_required(login_url='/userprofile/login/')
def user_delete(request,id):
    user = User.objects.get(id=id)
    if request.user == user:
        logout(request)
        user.delete()
        return  redirect('article:article_list')
    else:
        return HttpResponse("你没有权限删除")


#编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    #user_id OneToOneField 是自动生成的字段
    profile = Profile.objects.get(user_id=id)

    if request.method == "POST":
        #验证修改数据者
        if request.user != user:

            return HttpResponse("你没有权限修改此用户信息")
        profile_form = ProfileFrom(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            return redirect("userprofile:edit",id=id)
        else:
            return HttpResponse("注册表单输入有误，请重新输入~")
    elif request.method == "GET":
        profile_form = ProfileFrom()
        context = {'profile_form': profile_form, 'profile':profile, 'user':user}
        return render(request,'userprofile/edit.html',context)
    else:
        return HttpResponse("请使用GET/POST请求数据")



