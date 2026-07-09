# apps/survey/views.py
from rest_framework.views import APIView
from rest_framework.response import Response  # ✅ Đảm bảo import này
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
import json

# ✅ Import models với tên alias để tránh conflict
from .models import (
    Survey as SurveyModel,
    SurveyCategory as SurveyCategoryModel,
    Section as SectionModel,
    Question as QuestionModel,
    QuestionType as QuestionTypeModel,
    Response as ResponseModel,  # ✅ Đổi tên khi import
    Blocklist
)
from .serializers import (
    SurveySerializer, SectionSerializer, QuestionSerializer,
    SurveyCategorySerializer, QuestionTypeSerializer, ResponseSerializer,
    SurveyDetailSerializer, SurveyPublicSerializer,  # ✅ Thêm serializer mới
    SectionPublicSerializer, QuestionPublicSerializer,
    ResponseSubmitSerializer
)

# ============================================
# VIEWS CHO TRANG CHÍNH
# ============================================

@login_required(login_url='/accounts/login/')
def survey_edit_render(request):
    context = {
        'survey_id': request.GET.get('survey_id'),
        'category_id': request.GET.get('category_id'),
    }
    return render(request, 'survey/survey_main.html', context)


@login_required(login_url='/accounts/login/')
def duplicate_survey(request, survey_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        original = SurveyModel.objects.get(id=survey_id)
        from django.utils.text import slugify
        from django.utils import timezone
        import uuid
        
        new_survey = SurveyModel.objects.create(
            title=f"{original.title} (Bản sao)",
            slug=f"{original.slug}-copy-{uuid.uuid4().hex[:8]}",
            description=original.description,
            category=original.category,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            status='draft',
            target_groups=original.target_groups,
            settings=original.settings
        )
        
        for section in original.sections.all():
            new_section = SectionModel.objects.create(
                survey=new_survey,
                code=section.code,
                title=section.title,
                description=section.description,
                icon=section.icon,
                order=section.order
            )
            
            for question in section.questions.all():
                QuestionModel.objects.create(
                    section=new_section,
                    title=question.title,
                    description=question.description,
                    question_type=question.question_type,
                    is_required=question.is_required,
                    order=question.order,
                    options=question.options,
                    condition_logic=question.condition_logic,
                    config=question.config
                )
        
        return JsonResponse({
            'success': True,
            'survey_id': new_survey.id,
            'message': 'Đã tạo bản sao thành công'
        })
    except SurveyModel.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy khảo sát'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
def export_survey(request, survey_id):
    try:
        survey = SurveyModel.objects.get(id=survey_id)
        data = SurveyDetailSerializer(survey).data
        return JsonResponse(data, safe=False)
    except SurveyModel.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy khảo sát'}, status=404)


@login_required(login_url='/accounts/login/')
def publish_survey(request, survey_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        survey = SurveyModel.objects.get(id=survey_id)
        if survey.status != 'active':
            survey.status = 'active'
            survey.save()
            return JsonResponse({
                'success': True,
                'message': 'Đã phát hành khảo sát thành công',
                'status': survey.status
            })
        return JsonResponse({
            'success': False,
            'message': 'Khảo sát đã được phát hành trước đó',
            'status': survey.status
        })
    except SurveyModel.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy khảo sát'}, status=404)


# ============================================
# API VIEWS
# ============================================

class SurveyListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request):
        surveys = SurveyModel.objects.all().order_by('-created_at')
        
        category_id = request.query_params.get('category_id')
        category_code = request.query_params.get('category_code')
        
        if category_id:
            surveys = surveys.filter(category_id=category_id)
        elif category_code:
            surveys = surveys.filter(category__name__icontains=category_code)
            
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        try:
            data = request.data
            from django.utils.text import slugify
            base_slug = slugify(data.get('title', 'untitled'))
            slug = base_slug
            counter = 1
            while SurveyModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category_id = data.get('category') or data.get('category_id')
            category = None
            if category_id:
                try:
                    category = SurveyCategoryModel.objects.get(id=category_id)
                except SurveyCategoryModel.DoesNotExist:
                    pass
            
            survey = SurveyModel.objects.create(
                title=data['title'],
                slug=slug,
                description=data.get('description', ''),
                category=category,
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=30),
                status='draft',
                target_groups=data.get('target_groups', []),
                settings=data.get('settings', {})
            )
            
            return Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SurveyDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, pk):
        try:
            survey = SurveyModel.objects.get(id=pk)
            serializer = SurveyDetailSerializer(survey)
            return Response(serializer.data)
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            survey = SurveyModel.objects.get(id=pk)
            data = request.data
            
            for field in ['title', 'slug', 'description', 'status', 'target_groups', 'settings']:
                if field in data:
                    setattr(survey, field, data[field])
            
            survey.save()
            return Response(SurveyDetailSerializer(survey).data)
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            survey = SurveyModel.objects.get(id=pk)
            survey.delete()
            return Response({'message': 'Đã xóa khảo sát'}, status=status.HTTP_200_OK)
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=status.HTTP_404_NOT_FOUND)


class SectionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, survey_id):
        try:
            survey = SurveyModel.objects.get(id=survey_id)
            sections = survey.sections.all().order_by('order')
            serializer = SectionSerializer(sections, many=True)
            return Response(serializer.data)
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, survey_id):
        try:
            survey = SurveyModel.objects.get(id=survey_id)
            data = request.data
            
            max_order = survey.sections.aggregate(max_order=models.Max('order'))['max_order'] or -1
            section = SectionModel.objects.create(
                survey=survey,
                code=data.get('code', chr(65 + max_order + 1)),
                title=data.get('title', 'Phần mới'),
                description=data.get('description', ''),
                icon=data.get('icon', ''),
                order=max_order + 1
            )
            
            return Response(SectionSerializer(section).data, status=status.HTTP_201_CREATED)
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SectionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, pk):
        try:
            section = SectionModel.objects.get(id=pk)
            serializer = SectionSerializer(section)
            return Response(serializer.data)
        except SectionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy section'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            section = SectionModel.objects.get(id=pk)
            data = request.data
            
            for field in ['code', 'title', 'description', 'icon', 'order']:
                if field in data:
                    setattr(section, field, data[field])
            
            section.save()
            return Response(SectionSerializer(section).data)
        except SectionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy section'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            section = SectionModel.objects.get(id=pk)
            section.delete()
            return Response({'message': 'Đã xóa section'}, status=status.HTTP_200_OK)
        except SectionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy section'}, status=status.HTTP_404_NOT_FOUND)


class QuestionListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, section_id):
        try:
            section = SectionModel.objects.get(id=section_id)
            questions = section.questions.all().order_by('order')
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except SectionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy section'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, section_id):
        try:
            section = SectionModel.objects.get(id=section_id)
            data = request.data
            
            question_type = QuestionTypeModel.objects.get(id=data.get('question_type'))
            max_order = section.questions.aggregate(max_order=models.Max('order'))['max_order'] or -1
            
            question = QuestionModel.objects.create(
                section=section,
                title=data.get('title', 'Câu hỏi mới'),
                description=data.get('description', ''),
                question_type=question_type,
                is_required=data.get('is_required', True),
                order=max_order + 1,
                options=data.get('options', []),
                condition_logic=data.get('condition_logic', {}),
                config=data.get('config', {})
            )
            
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        except SectionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy section'}, status=status.HTTP_404_NOT_FOUND)
        except QuestionTypeModel.DoesNotExist:
            return Response({'error': 'Loại câu hỏi không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, pk):
        try:
            question = QuestionModel.objects.get(id=pk)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except QuestionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy câu hỏi'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            question = QuestionModel.objects.get(id=pk)
            data = request.data
            
            for field in ['title', 'description', 'is_required', 'order', 'options', 'condition_logic', 'config']:
                if field in data:
                    setattr(question, field, data[field])
            
            if 'question_type' in data:
                question_type = QuestionTypeModel.objects.get(id=data['question_type'])
                question.question_type = question_type
            
            question.save()
            return Response(QuestionSerializer(question).data)
        except QuestionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy câu hỏi'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            question = QuestionModel.objects.get(id=pk)
            question.delete()
            return Response({'message': 'Đã xóa câu hỏi'}, status=status.HTTP_200_OK)
        except QuestionModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy câu hỏi'}, status=status.HTTP_404_NOT_FOUND)


class ResponseCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def post(self, request):
        try:
            data = request.data
            survey_id = data.get('survey_id')
            
            if not survey_id:
                return Response({'error': 'Thiếu survey_id'}, status=status.HTTP_400_BAD_REQUEST)
            
            survey = get_object_or_404(SurveyModel, id=survey_id)
            
            response = None
            if 'response_id' in data:
                try:
                    response = ResponseModel.objects.get(id=data['response_id'], survey=survey)
                except ResponseModel.DoesNotExist:
                    pass
            
            if not response:
                response = ResponseModel(
                    survey=survey,
                    user=request.user,
                    respondent_email=request.user.email if request.user.is_authenticated else None,
                    status='draft'
                )
            
            if 'answers' in data:
                current_answers = response.answers or {}
                current_answers.update(data['answers'])
                response.answers = current_answers
            
            if 'section_progress' in data:
                current_progress = response.section_progress or {}
                current_progress.update(data['section_progress'])
                response.section_progress = current_progress
            
            if data.get('status') == 'submitted' and response.status != 'submitted':
                response.submitted_at = timezone.now()
                response.status = 'submitted'
            elif data.get('status') == 'draft':
                response.status = 'draft'
            
            if 'time_taken' in data:
                response.time_taken = data['time_taken']
            
            response.save()
            
            return Response(ResponseSerializer(response).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResponseDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, pk):
        try:
            response = ResponseModel.objects.get(id=pk)
            serializer = ResponseSerializer(response)
            return Response(serializer.data)
        except ResponseModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy response'}, status=status.HTTP_404_NOT_FOUND)


class SurveyStatsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request, survey_id):
        try:
            survey = SurveyModel.objects.get(id=survey_id)
            responses = survey.responses.all()
            
            total = responses.count()
            submitted = responses.filter(status='submitted').count()
            drafts = responses.filter(status='draft').count()
            
            section_stats = []
            for section in survey.sections.all():
                section_responses = []
                for response in responses.filter(status='submitted'):
                    if response.section_progress and section.code in response.section_progress:
                        section_responses.append(response.section_progress[section.code])
                
                avg_progress = sum(section_responses) / len(section_responses) if section_responses else 0
                section_stats.append({
                    'code': section.code,
                    'title': section.title,
                    'total_responses': len(section_responses),
                    'avg_progress': round(avg_progress, 2)
                })
            
            return Response({
                'survey_id': survey_id,
                'survey_title': survey.title,
                'total_responses': total,
                'submitted': submitted,
                'drafts': drafts,
                'completion_rate': round(submitted / total * 100, 2) if total > 0 else 0,
                'section_stats': section_stats
            })
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=status.HTTP_404_NOT_FOUND)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request):
        categories = SurveyCategoryModel.objects.all().order_by('name')
        serializer = SurveyCategorySerializer(categories, many=True)
        return Response(serializer.data)


class QuestionTypeListView(APIView):
    """Lấy danh sách loại câu hỏi"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get(self, request):
        try:
            question_types = QuestionTypeModel.objects.all().order_by('name')
            serializer = QuestionTypeSerializer(question_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        




# apps/survey/views.py (bổ sung thêm)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
import uuid

# apps/survey/views.py - Sửa các hàm public

# ============================================
# PUBLIC SURVEY VIEWS - Người dùng làm khảo sát
# ============================================

def survey_public_view(request, survey_id):
    """
    Trang public để người dùng làm khảo sát
    """
    survey = get_object_or_404(SurveyModel, id=survey_id, status='active')
    
    now = timezone.now()
    if survey.start_date and now < survey.start_date:
        return render(request, 'survey/survey_closed.html', {
            'survey': survey,
            'message': 'Khảo sát chưa bắt đầu. Vui lòng quay lại sau.'
        })
    
    if survey.end_date and now > survey.end_date:
        if not survey.allow_after_deadline:
            return render(request, 'survey/survey_closed.html', {
                'survey': survey,
                'message': 'Khảo sát đã kết thúc. Cảm ơn bạn đã quan tâm!'
            })
    
    context = {
        'survey': survey,
        'survey_id': survey.id,
        'is_public': True,
    }
    return render(request, 'survey/survey_public.html', context)


@login_required
def survey_public_response(request, survey_id):
    """
    API endpoint để lấy response hiện tại của user
    """
    survey = get_object_or_404(SurveyModel, id=survey_id)
    
    # SỬA: ResponseModel thay vì Response
    response, created = ResponseModel.objects.get_or_create(
        survey=survey,
        user=request.user,
        status='draft',
        defaults={
            'respondent_email': request.user.email,
            'answers': {},
            'section_progress': {}
        }
    )
    
    if not created and response.status == 'submitted':
        return JsonResponse({
            'error': 'Bạn đã nộp khảo sát này rồi.',
            'response_id': response.id,
            'status': 'submitted'
        }, status=400)
    
    serializer = ResponseSerializer(response)
    return JsonResponse(serializer.data)


# apps/survey/views.py - Hàm survey_submit_response

# apps/survey/views.py - Hàm survey_submit_response hoàn chỉnh

@csrf_exempt
def survey_submit_response(request):
    """
    API submit hoặc lưu nháp response
    Tự động cập nhật trạng thái đơn vị khi hoàn thành
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body) if request.body else {}
        
        # Validate dữ liệu
        serializer = ResponseSubmitSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({'error': serializer.errors}, status=400)
        
        validated = serializer.validated_data
        survey_id = validated['survey_id']
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # Lấy progress_id nếu có
        progress_id = validated.get('progress_id')
        progress = None
        if progress_id:
            try:
                from apps.survey.models import SurveyProgress
                progress = SurveyProgress.objects.get(id=progress_id)
            except SurveyProgress.DoesNotExist:
                progress = None
        
        # Lấy hoặc tạo response
        response_id = validated.get('response_id')
        if not response_id:
            response_id = request.session.get(f'survey_response_{survey_id}')

        response = None
        if response_id:
            try:
                response = ResponseModel.objects.get(id=response_id, survey=survey)
            except ResponseModel.DoesNotExist:
                response = None

        # Tạo mới response nếu chưa có
        if not response:
            response = ResponseModel(
                survey=survey,
                status='draft',
                answers={},
                section_progress={},
                respondent_ip=request.META.get('REMOTE_ADDR'),
                respondent_device_id=validated.get('device_id', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Gán user nếu đã đăng nhập
            if request.user.is_authenticated:
                response.user = request.user
                response.respondent_email = request.user.email
                
                # Tự động điền thông tin user vào answers lần đầu
                user = request.user
                user_info = {
                    'full_name': user.get_full_name() or user.username,
                    'email': user.email or '',
                    'phone': user.phone_number or '',
                    'position': user.position or '',
                    'department': user.organization.name if user.organization else '',
                    'agency': user.organization.name if user.organization else '',
                    'organization': user.organization.name if user.organization else '',
                }
                response.answers = user_info
        
        # Cập nhật answers
        if 'answers' in validated:
            current_answers = response.answers or {}
            for key, value in validated['answers'].items():
                # Nếu key là '_user_info' thì merge đặc biệt
                if key == '_user_info' and isinstance(value, dict):
                    for k, v in value.items():
                        if v:
                            current_answers[k] = v
                else:
                    current_answers[str(key)] = value
            response.answers = current_answers
        
        # Cập nhật section_progress
        if 'section_progress' in validated:
            current_progress = response.section_progress or {}
            for key, value in validated['section_progress'].items():
                current_progress[str(key)] = value
            response.section_progress = current_progress
        
        if 'time_taken' in validated:
            response.time_taken = validated['time_taken']
        
        # Xác định trạng thái mới
        new_status = validated.get('status', 'draft')
        was_submitted = response.status == 'submitted'
        
        if new_status == 'submitted' and not was_submitted:
            response.submitted_at = timezone.now()
            response.status = 'submitted'
        elif new_status == 'draft':
            response.status = 'draft'
        
        response.save()
        
        # ============================================================
        # CẬP NHẬT SURVEY PROGRESS
        # ============================================================
        if progress:
            # Tính tiến độ
            total_questions = 0
            answered = 0
            
            for section in survey.sections.all():
                for question in section.questions.all():
                    if question.question_type and question.question_type.code not in ['title', 'paragraph']:
                        total_questions += 1
                        if str(question.id) in response.answers:
                            answered += 1
            
            if total_questions > 0:
                progress.progress_percent = round((answered / total_questions) * 100)
            else:
                progress.progress_percent = 0
            
            # Cập nhật trạng thái progress
            if new_status == 'submitted':
                progress.status = 'completed'
                progress.completed_at = timezone.now()
            elif progress.progress_percent > 0 and progress.status == 'not_started':
                progress.status = 'in_progress'
                if not progress.started_at:
                    progress.started_at = timezone.now()
            
            if not progress.response:
                progress.response = response
            
            progress.save()
        
        # ============================================================
        # CẬP NHẬT SURVEY PARTICIPANT (nếu có)
        # ============================================================
        if request.user.is_authenticated:
            try:
                participant = SurveyParticipant.objects.filter(
                    user=request.user,
                    survey=survey,
                    status='draft'
                ).first()
                
                if participant:
                    # Cập nhật thông tin participant từ response
                    if not participant.full_name and response.answers.get('full_name'):
                        participant.full_name = response.answers.get('full_name')
                    if not participant.email and response.answers.get('email'):
                        participant.email = response.answers.get('email')
                    if not participant.phone and response.answers.get('phone'):
                        participant.phone = response.answers.get('phone')
                    if not participant.position and response.answers.get('position'):
                        participant.position = response.answers.get('position')
                    if not participant.department and response.answers.get('department'):
                        participant.department = response.answers.get('department')
                    if not participant.agency and response.answers.get('agency'):
                        participant.agency = response.answers.get('agency')
                    
                    if new_status == 'submitted':
                        participant.status = 'submitted'
                        participant.submitted_at = timezone.now()
                    
                    participant.response = response
                    participant.save()
            except Exception as e:
                print(f"Error updating participant: {e}")
        
        # ============================================================
        # CẬP NHẬT TRẠNG THÁI ĐƠN VỊ (QUAN TRỌNG)
        # ============================================================
        if new_status == 'submitted':
            try:
                from apps.survey.utils import update_survey_unit_status
                update_survey_unit_status(survey_id)
            except Exception as e:
                print(f"Error updating unit status: {e}")
                # Không fail response nếu lỗi update status
        
        # Lưu response ID vào session
        request.session[f'survey_response_{survey_id}'] = response.id
        
        # ============================================================
        # TRẢ VỀ KẾT QUẢ
        # ============================================================
        return JsonResponse({
            'success': True,
            'response_id': response.id,
            'status': response.status,
            'submitted_at': response.submitted_at.isoformat() if response.submitted_at else None,
            'progress_id': progress.id if progress else None,
            'progress_percent': progress.progress_percent if progress else 0,
            'message': 'Đã lưu thành công!' if new_status == 'draft' else 'Nộp khảo sát thành công!',
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        import traceback
        print(f"Error in survey_submit_response: {traceback.format_exc()}")
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


def survey_public_embed(request, survey_id):
    """
    Trả về survey dạng embed (iframe)
    """
    survey = get_object_or_404(SurveyModel, id=survey_id, status='active')
    context = {
        'survey': survey,
        'survey_id': survey.id,
        'is_embed': True,
    }
    return render(request, 'survey/survey_embed.html', context)


def survey_public_preview(request, survey_id):
    """
    Xem trước survey (không cần đăng nhập, chỉ dành cho survey active)
    """
    survey = get_object_or_404(SurveyModel, id=survey_id)
    
    if survey.status not in ['draft', 'active']:
        return render(request, 'survey/survey_closed.html', {
            'survey': survey,
            'message': 'Khảo sát này không có sẵn.'
        })
    
    context = {
        'survey': survey,
        'survey_id': survey.id,
        'is_preview': True,
    }
    return render(request, 'survey/survey_public.html', context)


def survey2_view(request, survey_id):
    """
    Render survey2.html với dữ liệu thực từ database
    """
    survey = get_object_or_404(SurveyModel, id=survey_id, status='active')
    
    # Lấy tất cả sections và questions
    sections = survey.sections.all().prefetch_related('questions__question_type').order_by('order')
    
    # Serialize data để truyền vào template
    from .serializers import SurveyPublicSerializer
    serializer = SurveyPublicSerializer(survey)
    
    context = {
        'survey': survey,
        'survey_data': serializer.data,
        'sections': sections,
        'survey_id': survey.id,
        'is_public': True,
    }
    return render(request, 'survey/survey2.html', context)


# ============================================
# PUBLIC API CLASS-BASED VIEWS
# ============================================

class SurveyPublicDetailView(APIView):
    """
    API public để lấy thông tin survey (không cần đăng nhập)
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, survey_id):
        try:
            survey = SurveyModel.objects.get(id=survey_id, status='active')
            serializer = SurveyPublicSerializer(survey)
            return Response(serializer.data)
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=404)


# apps/survey/views.py - Sửa hàm PublicResponseView (GET)

class PublicResponseView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, survey_id):
        try:
            survey = SurveyModel.objects.get(id=survey_id, status='active')
            
            # Lấy response_id từ session
            response_id = request.session.get(f'survey_response_{survey_id}')
            response = None
            
            if response_id:
                try:
                    response = ResponseModel.objects.get(id=response_id, survey=survey)
                    if response.status == 'submitted':
                        serializer = ResponseSerializer(response)
                        return Response(serializer.data)
                except ResponseModel.DoesNotExist:
                    pass
            
            # Nếu không tìm thấy theo session, thử tìm theo IP
            if not response:
                ip = request.META.get('REMOTE_ADDR')
                if ip:
                    try:
                        response = ResponseModel.objects.filter(
                            survey=survey,
                            respondent_ip=ip,
                            status='draft'
                        ).order_by('-started_at').first()
                    except Exception:
                        pass
            
            # Tạo mới nếu chưa có
            if not response:
                response = ResponseModel.objects.create(
                    survey=survey,
                    status='draft',
                    answers={},
                    section_progress={},
                    respondent_ip=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # ============================================================
                # TỰ ĐỘNG ĐIỀN THÔNG TIN USER VÀO ANSWERS
                # ============================================================
                if request.user.is_authenticated:
                    user = request.user
                    user_info = {
                        'full_name': user.get_full_name() or user.username,
                        'email': user.email or '',
                        'phone': user.phone_number or '',
                        'position': user.position or '',
                        'department': user.organization.name if user.organization else '',
                        'agency': user.organization.name if user.organization else '',
                        'organization': user.organization.name if user.organization else '',
                    }
                    response.answers = user_info
                    response.respondent_email = user.email
                    response.user = user
                    response.save()
                
                request.session[f'survey_response_{survey_id}'] = response.id
            
            serializer = ResponseSerializer(response)
            return Response(serializer.data)
            
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=404)
    
    def post(self, request, survey_id):
        """
        Cập nhật response
        """
        try:
            survey = SurveyModel.objects.get(id=survey_id)
            data = request.data
            
            response_id = data.get('response_id')
            if not response_id:
                response_id = request.session.get(f'survey_response_{survey_id}')
            
            if response_id:
                try:
                    response = ResponseModel.objects.get(id=response_id, survey=survey)
                except ResponseModel.DoesNotExist:
                    response = ResponseModel.objects.create(
                        survey=survey,
                        status='draft',
                        answers={},
                        section_progress={}
                    )
            else:
                response = ResponseModel.objects.create(
                    survey=survey,
                    status='draft',
                    answers={},
                    section_progress={}
                )
            
            request.session[f'survey_response_{survey_id}'] = response.id
            
            # ============================================================
            # TỰ ĐỘNG ĐIỀN THÔNG TIN USER KHI LƯU LẦN ĐẦU
            # ============================================================
            if request.user.is_authenticated and not response.answers:
                user = request.user
                user_info = {
                    'full_name': user.get_full_name() or user.username,
                    'email': user.email or '',
                    'phone': user.phone_number or '',
                    'position': user.position or '',
                    'department': user.organization.name if user.organization else '',
                    'agency': user.organization.name if user.organization else '',
                    'organization': user.organization.name if user.organization else '',
                }
                response.answers = user_info
                response.respondent_email = user.email
                response.user = user
            
            if 'answers' in data:
                current_answers = response.answers or {}
                for key, value in data['answers'].items():
                    if value is not None:
                        current_answers[str(key)] = value
                response.answers = current_answers
            
            if 'section_progress' in data:
                current_progress = response.section_progress or {}
                for key, value in data['section_progress'].items():
                    current_progress[str(key)] = value
                response.section_progress = current_progress
            
            if 'time_taken' in data:
                response.time_taken = data['time_taken']
            
            response.respondent_ip = request.META.get('REMOTE_ADDR')
            response.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            status_val = data.get('status', 'draft')
            if status_val == 'submitted' and response.status != 'submitted':
                response.submitted_at = timezone.now()
                response.status = 'submitted'
            elif status_val == 'draft':
                response.status = 'draft'
            
            response.save()
            
            return Response({
                'success': True,
                'response_id': response.id,
                'status': response.status,
                'answers': response.answers,
            })
            
        except SurveyModel.DoesNotExist:
            return Response({'error': 'Không tìm thấy khảo sát'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

from .models import SurveyAssignment, SurveyParticipant

def get_survey_mapping(request, survey_id):
    """
    Lấy danh sách mapping giữa nhóm đối tượng và biểu mẫu
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        assignments = SurveyAssignment.objects.filter(
            survey=survey,
            is_active=True
        ).order_by('order')
        
        data = []
        for assignment in assignments:
            data.append({
                'id': assignment.id,
                'form_code': assignment.form_code,
                'form_name': assignment.form_name,
                'form_description': assignment.form_description,
                'target_group_code': assignment.target_group_code,
                'target_group_name': assignment.target_group_name,
                'target_group_description': assignment.target_group_description,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def get_target_groups(request, survey_id):
    """
    Lấy danh sách nhóm đối tượng duy nhất từ mapping
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        assignments = SurveyAssignment.objects.filter(
            survey=survey,
            is_active=True
        ).values('target_group_code', 'target_group_name', 'target_group_description').distinct()
        
        data = list(assignments)
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)