# apps/analytics/serializers.py
from rest_framework import serializers
from .models import TargetGroup
from apps.survey.models import Survey as SurveyModel

class TargetGroupSerializer(serializers.ModelSerializer):
    form_count = serializers.SerializerMethodField()
    survey_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TargetGroup
        fields = [
            'id', 'code', 'name', 'description', 'icon', 
            'is_active', 'forms', 'surveys',
            'form_count', 'survey_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_form_count(self, obj):
        return len(obj.forms) if obj.forms else 0
    
    def get_survey_count(self, obj):
        return obj.surveys.count()


# Serializer cho Assignment
class AssignmentSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    group_code = serializers.CharField()
    group_name = serializers.CharField()
    group_icon = serializers.CharField()
    forms = serializers.ListField(child=serializers.CharField())
    is_active = serializers.BooleanField()
    
    class Meta:
        fields = ['group_id', 'group_code', 'group_name', 'group_icon', 'forms', 'is_active']


# Serializer cho Survey (để lấy danh sách survey)
class SurveySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        from apps.survey.models import Survey as SurveyModel
        model = SurveyModel
        fields = ['id', 'title', 'status', 'start_date', 'end_date']


# Serializer cho Form (Survey form)
class FormSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    section = serializers.CharField(required=False, allow_blank=True)