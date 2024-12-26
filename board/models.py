from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from tinymce.models import HTMLField


class Post(models.Model):
    CATEGORIES = [
        ('TA', 'Танки'),
        ('HI', 'Хилы'),
        ('DD', 'ДД'),
        ('TO', 'Торговцы'),
        ('GI', 'Гилдмастеры'),
        ('KV', 'Квестгиверы'),
        ('KU', 'Кузнецы'),
        ('KO', 'Кожевники'),
        ('ZE', 'Зельевары'),
        ('MA', 'Мастера заклинаний'),
    ]

    title = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=2, choices=CATEGORIES)
    replies = models.ManyToManyField('Reply', blank=True, related_name='replies')

    def __str__(self):  # настройка отображения на страницах
        return f'{self.title[:20]}'

    def get_absolute_url(self):
        return reverse('post_details', args=[str(self.id)])


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    accept = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.post.title[:20]}'

    def get_absolute_url(self):
        return reverse('post_details', args=[str(self.post.id)])

    def preview(self):
        return self.text[:124]+'...'


class PostReply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)


class News(models.Model):
    title = models.CharField(max_length=255, unique=True)
    text = models.TextField()

    # def get_absolute_url(self):
    #     return render(template_name=)