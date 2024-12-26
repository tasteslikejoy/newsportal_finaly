from django.contrib import admin
from django.db import models
from .models import Post, Reply
from tinymce.widgets import TinyMCE


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created', 'title', 'category')
    list_filter = ('category', 'author')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}}


class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', '')


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Reply)