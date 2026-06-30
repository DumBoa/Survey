# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.accounts_main_render, name='home'),
    path('login/', views.login_view, name='login'),
    
    # Cổng khảo sát công chức
    path('congkhaosat/', views.congkhaosat_view, name='congkhaosat'),
    path('api/congkhaosat/init/', views.congkhaosat_init, name='congkhaosat_init'),
    path('api/congkhaosat/submit/', views.congkhaosat_submit, name='congkhaosat_submit'),
    path('api/organizations/', views.get_organizations_api, name='api_organizations'),
    path('api/target-groups/', views.get_target_groups_api, name='api_target_groups'),
]