from django.contrib import admin
from .models import Survey, SurveyCategory, Section, Question, QuestionType, Response

@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon', 'created_at')
    search_fields = ('name',)

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'get_original_code', 'category', 'status', 'start_date', 'end_date')
    list_filter = ('category', 'status')
    search_fields = ('title', 'code')
    readonly_fields = ('code',)
    
    def get_original_code(self, obj):
        return obj.original_code
    get_original_code.short_description = 'Mã gốc (Original Code)'

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'survey', 'order')
    list_filter = ('survey',)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.survey.responses.exists():
            return False
        return super().has_delete_permission(request, obj)

@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'has_options', 'has_validation')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question_type', 'section', 'order', 'is_required')
    list_filter = ('section__survey', 'question_type')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.section.survey.responses.exists():
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'respondent_email', 'status', 'submitted_at')
    list_filter = ('status', 'survey')
