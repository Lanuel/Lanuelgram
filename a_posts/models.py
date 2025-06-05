from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
import uuid
from uuid import uuid4

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
    likes = models.ManyToManyField(User, related_name="likedposts", through="LikedPost")
    image = models.URLField(max_length=500)
    url = models.URLField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)

    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ["-created"]
    

class LikedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} : {self.post.title}'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="comments")
    body = models.CharField(max_length=150)
    likes = models.ManyToManyField(User, related_name="likedcomments", through="LikedComment")
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="comments")
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : "{self.body[:30]}"'
        except:
            return f'no author : "{self.body[:30]}"'

    @staticmethod
    def top_comments_for_post(post):
        return post.comments.annotate(
            score=Count("likes", distinct=True)
        ).order_by("-score", "-created")
    
    class Meta:
        ordering = ["-created"]

        
class LikedComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} : {self.comment.body[:30]}'
    

class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="replies")
    body = models.CharField(max_length=150)
    likes = models.ManyToManyField(User, related_name="likedreplies", through="LikedReply")
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name="replies")
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : "{self.body[:30]}"'
        except:
            return f'no author : "{self.body[:30]}"'


class LikedReply(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} : {self.reply.body[:30]}'
    