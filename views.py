from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.shortcuts import render_to_response


from jot.models import Category


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render_to_response('blog/category_detail.html',
                              { 'object_list': category.live_entry_set(),
                               'category': category })

def category_list(request):
    return render_to_response('blog/category_list.html',
                              { 'object_list': Category.objects.all() })
