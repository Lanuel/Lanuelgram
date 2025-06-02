from django.urls import path
from . import views


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("category/<slug:tags>/", views.HomePageView.as_view(), name="category"),
    path("post/create/", views.PostCreateView.as_view(), name="create_post"),
    path("post/edit/<str:pk>/", views.PostUpdateView.as_view(), name="edit_post"),
    path("post/delete/<str:pk>/", views.PostDeleteView.as_view(), name="delete_post"),
    path("post/details/<str:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("comment/delete/<str:pk>/", views.CommentDeleteView.as_view(), name="delete_comment"),
    path("reply/delete/<str:pk>/", views.ReplyDeleteView.as_view(), name="delete_reply"),
]

