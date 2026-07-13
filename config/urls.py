# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from apps.accounts.views import is_admin_user
from django.conf import settings


# config/urls.py

def root_redirect(request):
    """
    Redirect dựa trên trạng thái đăng nhập và role
    """
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            return redirect('/analytics/')
        # User thường -> vào dashboard
        return redirect('/accounts/survey-dashboard/')
    # Chưa đăng nhập -> vào tổng quan khảo sát thay vì cổng đăng nhập
    return redirect('/analytics/public-dashboard/')


urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('survey/', include('apps.survey.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('analytics/', include('apps.analytics.urls')),
]