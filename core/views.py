from typing import List
from django.db.models.query import QuerySet
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, resolve_url
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from core.forms import EmailPostForm
from django.core.mail import send_mail

from core.models import Post

# Create your views here.


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='publicado')
    sent = False
    if request.POST:
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
            post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                            f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                            f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'tassiotaylor@gmail.com',
            [cd['to']])
            sent = True
    else:
        form = EmailPostForm()        
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request):
    object_list = Post.objects.all()
    paginator = Paginator(object_list ,3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)        
    return render(request,'blog/post/list.html', {'posts': posts,'page': page})

    


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                    status='publicado',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)
    return render(request,'blog/post/detail.html',{'post': post})                                 