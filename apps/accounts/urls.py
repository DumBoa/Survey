# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==========================================
    # TRANG CHỦ - Cổng khảo sát (congkhaosat_main)
    # ==========================================
    path('', views.accounts_main_render, name='home'),
    
    # ==========================================
    # TRANG ĐĂNG NHẬP ADMIN
    # ==========================================
    path('login/', views.login_view, name='login'),              # Admin login
    
    # ==========================================
    # ĐĂNG XUẤT
    # ==========================================
    path('logout/', views.logout_view, name='logout'),           # Logout
    
    # ==========================================
    # DASHBOARD USER
    # ==========================================
    path('survey-dashboard/', views.survey_dashboard, name='survey_dashboard'),
    path('survey-dashboard/continue/<int:progress_id>/', views.survey_dashboard_continue, name='survey_dashboard_continue'),
    
    # ==========================================
    # API CỔNG KHẢO SÁT (congkhaosat_main)
    # ==========================================
    path('api/congkhaosat/login/', views.congkhaosat_login_api, name='congkhaosat_login_api'),
    path('api/congkhaosat/logout/', views.congkhaosat_logout_api, name='congkhaosat_logout_api'),
    path('api/congkhaosat/check-auth/', views.congkhaosat_check_auth, name='congkhaosat_check_auth'),
    path('api/congkhaosat/start-survey/', views.congkhaosat_start_survey, name='congkhaosat_start_survey'),
    
    # ==========================================
    # API XÁC MINH SỐ ĐIỆN THOẠI (MỚI)
    # ==========================================
    path('api/congkhaosat/verify-phone/', views.congkhaosat_verify_phone, name='congkhaosat_verify_phone'),
    
    # ==========================================
    # API LẤY KHẢO SÁT THEO NHÓM
    # ==========================================
    path('api/surveys-by-group/<int:group_id>/', views.get_surveys_by_group_api, name='get_surveys_by_group_api'),
    
    # ==========================================
    # API PUBLIC
    # ==========================================
    path('api/organizations/', views.get_organizations_api, name='api_organizations'),
    path('api/target-groups/', views.get_target_groups_api, name='api_target_groups'),
    path('api/survey-forms/', views.get_survey_forms_api, name='api_survey_forms'),
    
    # === EXPORT PDF ===
    path('export/<int:response_id>/pdf/', views.export_response_pdf, name='export_response_pdf'),

    path('api/congkhaosat/create-participant/', views.congkhaosat_create_participant, name='congkhaosat_create_participant'),

    path('api/switch-target-group/', views.switch_target_group_api, name='api_switch_target_group'),
    path('api/user-target-groups/', views.get_user_target_groups_api, name='api_user_target_groups'),
]