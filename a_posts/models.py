from django.db import models
from django.contrib.auth.models import User
import uuid


class Tag(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20, unique=True)
    image = models.FileField(upload_to='icons/', null=True, blank=True)
    order = models.IntegerField()

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']


class Post(models.Model):
    artist = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag)
    image = models.URLField(max_length=500)
    url = models.URLField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ["-created"]
    

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comments")
    body = models.CharField(max_length=150)
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="comments")
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : "{self.body[:30]}"'
        except:
            return f'no author : "{self.body[:30]}"'
    
    class Meta:
        ordering = ["created"]


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="replies")
    body = models.CharField(max_length=150)
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name="replies")
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : "{self.body[:30]}"'
        except:
            return f'no author : "{self.body[:30]}"'
    
    class Meta:
        ordering = ["created"]