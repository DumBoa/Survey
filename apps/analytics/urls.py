# apps/analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # === TRANG CHÍNH ===
    path('', views.dashboard_home, name='dashboard'),
    
    # === CÁC TRANG QUẢN LÝ (UI) ===
    path('target-groups/', views.target_groups_view, name='target_groups'),
    path('survey-forms/', views.survey_forms_view, name='survey_forms'),
    path('assignments/', views.assignments_view, name='assignments'),
    path('account-manage/', views.account_manage, name='account_manage'),
    
    # === BÁO CÁO TỔNG HỢP ĐƠN VỊ ===
    path('survey-dashboard/', views.tongquankhaosat_view, name='survey_dashboard'),
    path('api/survey-dashboard/<int:survey_id>/', views.survey_unit_dashboard_api, name='api_survey_unit_dashboard'),
    
    path('api/organizations/with-status/', views.organization_with_status_api, name='api_organizations_with_status'),
    # === API TARGET GROUPS ===
    path('api/target-groups/', views.target_group_list_api, name='api_target_group_list'),
    path('api/target-groups/<int:group_id>/', views.target_group_detail_api, name='api_target_group_detail'),
    path('api/target-groups/create/', views.target_group_create_api, name='api_target_group_create'),
    path('api/target-groups/<int:group_id>/update/', views.target_group_update_api, name='api_target_group_update'),
    path('api/target-groups/<int:group_id>/delete/', views.target_group_delete_api, name='api_target_group_delete'),
    path('api/target-groups/options/', views.target_group_options_api, name='api_target_group_options'),
    
    # === API ASSIGNMENTS ===
    path('api/assignments/', views.assignment_list_api, name='api_assignment_list'),
    path('api/assignments/<int:group_id>/', views.assignment_detail_api, name='api_assignment_detail'),
    path('api/assignments/create/', views.assignment_create_api, name='api_assignment_create'),
    path('api/assignments/<int:group_id>/update/', views.assignment_update_api, name='api_assignment_update'),
    path('api/assignments/<int:group_id>/delete/', views.assignment_delete_api, name='api_assignment_delete'),
    path('api/assignments/<int:group_id>/remove-form/', views.assignment_remove_form_api, name='api_assignment_remove_form'),
    
    # === API SURVEY FORMS ===
    path('api/survey-forms/', views.survey_forms_list_api, name='api_survey_forms_list'),
    path('api/survey-forms/<int:survey_id>/', views.survey_form_detail_api, name='api_survey_form_detail'),
    path('api/survey-forms/create/', views.survey_form_create_api, name='api_survey_form_create'),
    path('api/survey-forms/<int:survey_id>/update/', views.survey_form_update_api, name='api_survey_form_update'),
    path('api/survey-forms/<int:survey_id>/delete/', views.survey_form_delete_api, name='api_survey_form_delete'),
    path('api/survey-forms/categories/', views.survey_form_categories_api, name='api_survey_form_categories'),
    
    # === API QUẢN LÝ TÀI KHOẢN ===
    path('api/accounts/', views.account_list_api, name='api_account_list'),
    path('api/accounts/<int:user_id>/', views.account_detail_api, name='api_account_detail'),
    path('api/accounts/create/', views.account_create_api, name='api_account_create'),
    path('api/accounts/<int:user_id>/update/', views.account_update_api, name='api_account_update'),
    path('api/accounts/<int:user_id>/delete/', views.account_delete_api, name='api_account_delete'),
    path('api/accounts/organizations/', views.account_organizations_api, name='api_account_organizations'),
    path('api/accounts/bulk-action/', views.account_bulk_action_api, name='api_account_bulk_action'),
    # === QUẢN LÝ ĐƠN VỊ (ORGANIZATION) ===
    path('organizations/', views.organization_manage_view, name='organization_manage'),
    path('api/organizations/', views.organization_list_api, name='api_organization_list'),
    path('api/organizations/<int:org_id>/', views.organization_detail_api, name='api_organization_detail'),
    path('api/organizations/create/', views.organization_create_api, name='api_organization_create'),
    path('api/organizations/<int:org_id>/update/', views.organization_update_api, name='api_organization_update'),
    path('api/organizations/<int:org_id>/delete/', views.organization_delete_api, name='api_organization_delete'),
    path('api/organizations/options/', views.organization_options_api, name='api_organization_options'),
]