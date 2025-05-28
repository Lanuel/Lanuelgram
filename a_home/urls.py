from django.urls import path
from a_home.views import *

urlpatterns = [
    path('home/', home_view, name="home"),  
]
