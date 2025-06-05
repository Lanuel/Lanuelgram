from django.template import Library
from ..models import *
from django.db.models import Count

register = Library()

@register.inclusion_tag("includes/sidebar.html")
def sidebar_view(tag=None, user=None):
    categories = Tag.objects.all()
    top_posts = Post.objects.annotate(
            post_num_likes=Count("likes", distinct=True)
        ).filter(post_num_likes__gt=0).order_by("-post_num_likes")
    top_comments = Comment.objects.annotate(
            comment_num_likes=Count("likes", distinct=True)
        ).filter(comment_num_likes__gt=0).order_by("-comment_num_likes")
    
    context = {"categories": categories,
               "current_tag_slug":tag,
               "top_posts": top_posts,
               "top_comments": top_comments,
               "user":user,
               }
    return context