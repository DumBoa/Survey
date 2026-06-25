# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'  # Thêm namespace

urlpatterns = [
    path('', views.accounts_main_render, name='home'),
    path('login/', views.login_view, name='login'),  # Thêm URL login
]