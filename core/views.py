from typing import List
from django.db.models.query import QuerySet
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, resolve_url
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import activate
from django.views.generic import ListView
from core.forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from .models import Post, Comment
from taggit.models import Tag
from django.db.models import Count

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


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page,'posts': posts,'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                    status='publicado',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)

    comments = post.comments.filter(activate = True)
    new_comment = None

    if request.POST:
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit = False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat = True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]                                            
    return render(request,'blog/post/detail.html',{'post': post,
                                                    'comments': comments,
                                                    'new_comment': new_comment,
                                                    'comment_form': comment_form,
                                                    'similar_posts': similar_posts})
