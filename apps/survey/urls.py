# apps/survey/urls.py
from django.urls import path
from . import views

app_name = 'survey'

urlpatterns = [
    # Trang chính
    path('survey-edit/', views.survey_edit_render, name='survey_edit_render'),
    
    # ============================================
    # API ENDPOINTS
    # ============================================
    path('api/surveys/', views.SurveyListCreateView.as_view(), name='api_survey_list'),
    path('api/surveys/<int:pk>/', views.SurveyDetailView.as_view(), name='api_survey_detail'),
    path('api/surveys/<int:survey_id>/sections/', views.SectionListCreateView.as_view(), name='api_section_list'),
    path('api/sections/<int:pk>/', views.SectionDetailView.as_view(), name='api_section_detail'),
    path('api/sections/<int:section_id>/questions/', views.QuestionListCreateView.as_view(), name='api_question_list'),
    path('api/questions/<int:pk>/', views.QuestionDetailView.as_view(), name='api_question_detail'),
    path('api/surveys/<int:survey_id>/duplicate/', views.duplicate_survey, name='api_duplicate_survey'),
    path('api/surveys/<int:survey_id>/export/', views.export_survey, name='api_export_survey'),
    path('api/surveys/<int:survey_id>/publish/', views.publish_survey, name='api_publish_survey'),
    path('api/responses/', views.ResponseCreateView.as_view(), name='api_response_create'),
    path('api/responses/<int:pk>/', views.ResponseDetailView.as_view(), name='api_response_detail'),
    path('api/responses/<int:survey_id>/stats/', views.SurveyStatsView.as_view(), name='api_survey_stats'),
    path('api/categories/', views.CategoryListView.as_view(), name='api_category_list'),
    path('api/question-types/', views.QuestionTypeListView.as_view(), name='api_question_type_list'),


    # ============================================
    # PUBLIC SURVEY URLs
    # ============================================
    path('public/<int:survey_id>/', views.survey_public_view, name='survey_public'),
    path('public/<int:survey_id>/embed/', views.survey_public_embed, name='survey_public_embed'),
    path('public/<int:survey_id>/preview/', views.survey_public_preview, name='survey_public_preview'),
    
    # ============================================
    # PUBLIC API - Cho người dùng làm khảo sát
    # ============================================
    path('api/public/surveys/<int:survey_id>/', views.SurveyPublicDetailView.as_view(), name='api_public_survey_detail'),
    path('api/public/surveys/<int:survey_id>/response/', views.PublicResponseView.as_view(), name='api_public_response'),
    path('api/public/responses/submit/', views.survey_submit_response, name='api_public_submit'),

]