# apps/analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_main_render, name='home_analytics'),
    
    # === QUẢN LÝ BIỂU MẪU ===
    path('qly-bieumau/', views.survey_list_render, name='survey_list'),
    
    # === API ===
    path('api/surveys/list/', views.survey_list_api, name='api_survey_list'),
    path('api/surveys/<int:survey_id>/', views.survey_detail_api, name='api_survey_detail'),
    path('api/surveys/create/', views.survey_create_api, name='api_survey_create'),
    path('api/surveys/<int:survey_id>/update/', views.survey_update_api, name='api_survey_update'),
    path('api/surveys/<int:survey_id>/delete/', views.survey_delete_api, name='api_survey_delete'),
    path('api/surveys/bulk-action/', views.survey_bulk_action_api, name='api_survey_bulk'),
    path('api/categories/', views.survey_categories_api, name='api_categories'),
    path('api/stats/', views.survey_stats_api, name='api_stats'),
]