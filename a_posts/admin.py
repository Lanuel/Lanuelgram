from django.contrib import admin
from .models import Post, Tag, Comment, Reply
from django.contrib.admin import ModelAdmin


class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ["title", "body", "created"]


class TagAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'slug']


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment)
admin.site.register(Reply)
