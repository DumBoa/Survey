from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_main_render, name='home_analytics'),
]