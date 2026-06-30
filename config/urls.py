# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('analytics:dashboard')
    return redirect('/accounts/login/') 

urlpatterns = [
    path('', root_redirect),  
    path('admin/', admin.site.urls),
    path('survey/', include('apps.survey.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('analytics/', include('apps.analytics.urls'))
]