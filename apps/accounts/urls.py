# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==========================================
    # TRANG CHỦ
    # ==========================================
    path('', views.accounts_main_render, name='home'),
    
    # ==========================================
    # TRANG ĐĂNG NHẬP / ĐĂNG XUẤT
    # ==========================================
    path('login/', views.login_view, name='login'),              # Admin login
    path('user-login/', views.user_login_view, name='user_login'),  # User login
    path('logout/', views.logout_view, name='logout'),           # Logout
    
    # ==========================================
    # DASHBOARD USER
    # ==========================================
    path('survey-dashboard/', views.survey_dashboard, name='survey_dashboard'),
    path('survey-dashboard/continue/<int:progress_id>/', views.survey_dashboard_continue, name='survey_dashboard_continue'),
    
    # ==========================================
    # API CẬP NHẬT THÔNG TIN
    # ==========================================
    path('api/update-user-info/', views.update_user_info, name='update_user_info'),
    
    # ==========================================
    # API PUBLIC
    # ==========================================
    path('api/organizations/', views.get_organizations_api, name='api_organizations'),
    path('api/target-groups/', views.get_target_groups_api, name='api_target_groups'),
    path('api/survey-forms/', views.get_survey_forms_api, name='api_survey_forms'),
]