from django.urls import path
from a_home.views import *

urlpatterns = [
    path('about/', AboutPageView.as_view(), name="about"),  
]
