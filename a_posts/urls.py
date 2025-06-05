from django.urls import path
from . import views


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("category/<slug:tags>/", views.HomePageView.as_view(), name="category"),
    path("post/create/", views.PostCreateView.as_view(), name="create_post"),
    path("post/like/<uuid:pk>/", views.like_post, name="like_post"),
    path("post/edit/<uuid:pk>/", views.PostUpdateView.as_view(), name="edit_post"),
    path("post/delete/<uuid:pk>/", views.PostDeleteView.as_view(), name="delete_post"),
    path("post/details/<uuid:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("comment/like/<uuid:pk>/", views.like_comment, name="like_comment"),
    path("comment/delete/<uuid:pk>/", views.CommentDeleteView.as_view(), name="delete_comment"),
    path("reply/delete/<uuid:pk>/", views.ReplyDeleteView.as_view(), name="delete_reply"),
    path("reply/like/<uuid:pk>/", views.like_reply, name="like_reply"),
]

