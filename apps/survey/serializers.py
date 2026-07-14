# apps/survey/serializers.py
from rest_framework import serializers
from .models import Survey, SurveyCategory, Section, Question, QuestionType, Response


class SurveyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCategory
        fields = ['id', 'name', 'description', 'icon']


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ['id', 'name', 'code', 'icon', 'has_options', 'has_validation']


# apps/survey/serializers.py

class QuestionSerializer(serializers.ModelSerializer):
    question_type_name = serializers.CharField(source='question_type.name', read_only=True)
    question_type_code = serializers.CharField(source='question_type.code', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'description', 'question_type', 'question_type_name', 
            'question_type_code', 'is_required', 'order', 'options', 
            'condition_logic', 'config', 'component_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class SectionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = [
            'id', 'survey', 'code', 'title', 'description', 
            'icon', 'order', 'questions', 'total_questions',
            'created_at', 'updated_at'
        ]
    
    def get_questions(self, obj):
        questions = obj.questions.filter(is_active=True).order_by('order')
        return QuestionSerializer(questions, many=True).data
    
    def get_total_questions(self, obj):
        return obj.questions.filter(is_active=True).count()


class SurveySerializer(serializers.ModelSerializer):
    category_detail = SurveyCategorySerializer(source='category', read_only=True)
    sections = serializers.SerializerMethodField()
    total_sections = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    original_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Survey
        fields = [
            'id', 'code', 'original_code', 'title', 'slug', 'description', 'category', 'category_detail',
            'start_date', 'end_date', 'allow_after_deadline', 'status',
            'target_groups', 'settings', 'sections', 'total_sections',
            'total_questions', 'created_at', 'updated_at'
        ]
    
    def get_sections(self, obj):
        sections = obj.sections.filter(is_active=True).order_by('order')
        return SectionSerializer(sections, many=True).data
    
    def get_total_sections(self, obj):
        return obj.sections.filter(is_active=True).count()
    
    def get_total_questions(self, obj):
        total = 0
        for section in obj.sections.filter(is_active=True):
            total += section.questions.filter(is_active=True).count()
        return total


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết bao gồm tất cả sections và questions"""
    category_detail = SurveyCategorySerializer(source='category', read_only=True)
    sections = serializers.SerializerMethodField()
    original_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Survey
        fields = [
            'id', 'code', 'original_code', 'title', 'slug', 'description', 'category', 'category_detail',
            'start_date', 'end_date', 'allow_after_deadline', 'status',
            'target_groups', 'settings', 'sections', 'created_at', 'updated_at'
        ]

    def get_sections(self, obj):
        sections = obj.sections.filter(is_active=True).order_by('order')
        return SectionSerializer(sections, many=True).data


class ResponseSerializer(serializers.ModelSerializer):
    survey_title = serializers.CharField(source='survey.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Response
        fields = [
            'id', 'survey', 'survey_title', 'user', 'user_email',
            'respondent_ip', 'respondent_device_id', 'respondent_email',
            'user_agent', 'started_at', 'submitted_at', 'time_taken',
            'status', 'answers', 'section_progress', 'is_verified',
            'verification_token', 'is_cleaned', 'is_duplicate',
            'created_at'
        ]
        read_only_fields = ['started_at', 'created_at']






class SurveyPublicSerializer(serializers.ModelSerializer):
    """Serializer cho public survey - chỉ hiển thị thông tin cần thiết"""
    sections = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'status', 'sections', 'settings']
    
    def get_sections(self, obj):
        sections = obj.sections.all().order_by('order')
        return SectionPublicSerializer(sections, many=True).data


class SectionPublicSerializer(serializers.ModelSerializer):
    """Serializer cho public section"""
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'code', 'title', 'description', 'order', 'questions']
    
    def get_questions(self, obj):
        questions = obj.questions.all().order_by('order')
        return QuestionPublicSerializer(questions, many=True).data


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Serializer cho public question"""
    question_type = serializers.StringRelatedField()
    question_type_code = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'description', 'question_type', 
            'question_type_code', 'is_required', 'order', 
            'options', 'config', 'condition_logic'
        ]
    
    def get_question_type_code(self, obj):
        return obj.question_type.code if obj.question_type else None


class ResponseSubmitSerializer(serializers.Serializer):
    """Serializer cho submit response"""
    survey_id = serializers.IntegerField()
    response_id = serializers.IntegerField(required=False)
    progress_id = serializers.IntegerField(required=False)
    answers = serializers.DictField(required=False, default=dict)
    section_progress = serializers.DictField(required=False, default=dict)
    status = serializers.ChoiceField(choices=['draft', 'submitted'])
    time_taken = serializers.IntegerField(required=False, default=0)
    device_id = serializers.CharField(required=False, default='')
    user_agent = serializers.CharField(required=False, default='')