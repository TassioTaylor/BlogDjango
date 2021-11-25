from django.db import models
from django.urls.base import reverse

from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import activate
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status = 'publicado')


class Post(models.Model):
    STATUS_CHOICES = (
        ('rascunho','Rascunho'),
        ('publicado','Publicado'),
    )
    title = models.CharField(max_length= 250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField()
    publish = models.DateTimeField(default= timezone.now)
    created = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete= models.CASCADE, related_name='blog_posts')

    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class META:
        order = ('-publish',)


    def __str__(self):
        return self.title    

    def get_absolute_url(self):
        return reverse('core:post_detail',
                        args = [self.publish.year,
                                self.publish.month,
                                self.publish.day,
                                self.slug
                                ])



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    activate = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)


    def __str__(self):
        return f'Comentado por {self.name} em {self.post}'
