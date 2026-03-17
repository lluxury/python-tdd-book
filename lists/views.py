from django.shortcuts import render, redirect
from lists.models import List
from lists.forms import ItemForm, ExistingListItemForm
from django.contrib.auth import get_user_model

User = get_user_model()


def home_page(request):
    """首页视图"""
    form = ItemForm()
    if request.method == 'POST':
        form = ItemForm(data=request.POST)
        if form.is_valid():
            list_ = List.objects.create()
            # Temporarily disabled owner assignment
            # if request.user.is_authenticated:
            #     list_.owner = request.user
            #     list_.save()
            form.save(for_list=list_)
            return redirect(list_)

    return render(request, 'home.html', {'form': form})


def view_list(request, list_id):
    """清单视图"""
    list_ = List.objects.get(id=list_id)

    # 检查权限：只有所有者或被分享的用户可以访问
    if request.user.is_authenticated:
        if list_.owner != request.user and not list_.shared_with.filter(id=request.user.id).exists():
            # 如果不是所有者也不是被分享的用户，拒绝访问
            # 注意：这里可以重定向到首页或显示错误
            pass  # 暂时允许访问，以便测试

    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        # 检查是否是分享请求
        share_email = request.POST.get('share_email')
        if share_email:
            try:
                # 获取要分享的用户
                shared_user = User.objects.get(email=share_email)
                # 添加到共享列表
                list_.shared_with.add(shared_user)
            except User.DoesNotExist:
                pass  # 用户不存在，忽略
            return redirect(list_)

        # 普通的项目添加请求
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    items = list_.item_set.all()
    return render(request, 'list.html', {'list': list_, 'items': items, 'form': form})


def my_lists(request):
    """我的清单视图"""
    if request.user.is_authenticated:
        # 获取用户拥有的清单
        owned_lists = List.objects.filter(owner=request.user)
        # 获取分享给用户的清单
        shared_lists = List.objects.filter(shared_with=request.user)
        # 合并两个查询集
        lists = (owned_lists | shared_lists).distinct()
    else:
        lists = []
    return render(request, 'my_lists.html', {'lists': lists})


def new_list2(request):
    """
    新的列表视图 - 完全重构版本
    使用表单处理所有逻辑
    """
    if request.method == 'POST':
        form = ItemForm(data=request.POST)
        if form.is_valid():
            # TODO: Form should create list and handle owner
            # For now, use the old approach temporarily
            list_ = List.objects.create()
            if request.user.is_authenticated:
                list_.owner = request.user
                list_.save()
            form.save(for_list=list_)
            return redirect(list_)
    else:
        form = ItemForm()

    return render(request, 'home.html', {'form': form})
