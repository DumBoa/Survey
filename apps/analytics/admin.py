from django.contrib import admin
from .models import ScoringConfig, AggregatedResult, ComparisonReport

@admin.register(ScoringConfig)
class ScoringConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'survey', 'is_active', 'created_at')
    list_filter = ('is_active', 'survey')

@admin.register(AggregatedResult)
class AggregatedResultAdmin(admin.ModelAdmin):
    list_display = ('survey', 'level', 'entity_name', 'average_score', 'total_responses', 'year', 'quarter')
    list_filter = ('survey', 'level', 'year', 'quarter')
    search_fields = ('entity_name',)

@admin.register(ComparisonReport)
class ComparisonReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'survey', 'comparison_type', 'generated_at')