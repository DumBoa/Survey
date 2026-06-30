# apps/analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # === TRANG CHÍNH ===
    path('', views.dashboard_home, name='dashboard'),
    
    # === CÁC TRANG QUẢN LÝ (UI) ===
    path('surveys/', views.survey_list_view, name='survey_list'),
    path('target-groups/', views.target_groups_view, name='target_groups'),
    path('survey-forms/', views.survey_forms_view, name='survey_forms'),
    path('assignments/', views.assignments_view, name='assignments'),
    
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
    path('api/assignments/surveys/', views.assignment_surveys_api, name='api_assignment_surveys'),
    
    # === API SURVEY FORMS ===
    path('api/survey-forms/', views.survey_forms_list_api, name='api_survey_forms_list'),
    path('api/survey-forms/<int:survey_id>/', views.survey_form_detail_api, name='api_survey_form_detail'),
    path('api/survey-forms/create/', views.survey_form_create_api, name='api_survey_form_create'),
    path('api/survey-forms/<int:survey_id>/update/', views.survey_form_update_api, name='api_survey_form_update'),
    path('api/survey-forms/<int:survey_id>/delete/', views.survey_form_delete_api, name='api_survey_form_delete'),
    path('api/survey-forms/categories/', views.survey_form_categories_api, name='api_survey_form_categories'),
]