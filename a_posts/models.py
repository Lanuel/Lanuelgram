from django.db import models
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
    tags = models.ManyToManyField(Tag)
    image = models.URLField(max_length=500)
    url = models.URLField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ["-created"]
    

