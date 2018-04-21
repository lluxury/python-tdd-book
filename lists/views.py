from django.shortcuts import redirect, render
from lists.models import Item

def home_page(request):
    return render(request, 'home.html')

def view_list(request):
    # pass
    items = Item.objects.all()
    return render(request, 'list.html', {'items': items})

def new_list(request):
    # pass
    Item.objects.create(text=request.POST['item_text'])
    return redirect('/lists/the-only-list-in-the-world/')
    # return redirect('lists/the-only-list-in-the-world/')
