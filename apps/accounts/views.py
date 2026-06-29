# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
import json
import re
import uuid

# Import models
from .models import User, Organization
from apps.survey.models import Survey as SurveyModel, Response as ResponseModel


def accounts_main_render(request):
    return render(request, 'accounts/accounts_main.html')


def get_user_role_from_db(user):
    return 'admin'


def get_role_display_name(role):
    return 'Quản trị viên'


@require_http_methods(["GET", "POST"])
@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/survey/survey-edit/')
        return render(request, 'accounts/login.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ!'
            }, status=400)
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng không để trống thông tin!'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if not remember:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            
            return JsonResponse({
                'success': True,
                'message': 'Đăng nhập thành công!',
                'redirect_url': '/survey/survey-edit/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Sai tên đăng nhập hoặc mật khẩu!'
            }, status=401)


# ============================================
# CỔNG KHẢO SÁT CÔNG CHỨC - 3 BƯỚC
# ============================================

def congkhaosat_view(request):
    """
    Trang cổng khảo sát 3 bước
    """
    # Lấy survey_id từ URL hoặc mặc định lấy survey đang active
    survey_id = request.GET.get('survey_id')
    
    if survey_id:
        survey = get_object_or_404(SurveyModel, id=survey_id)
    else:
        # Lấy survey active gần nhất
        survey = SurveyModel.objects.filter(status='active').order_by('-created_at').first()
    
    if not survey:
        return render(request, 'accounts/congkhaosat_no_survey.html', {
            'message': 'Hiện tại chưa có khảo sát nào đang hoạt động.'
        })
    
    context = {
        'survey_id': survey.id,
        'survey_title': survey.title,
        'survey_description': survey.description,
        'is_public': True,
    }
    return render(request, 'accounts/congkhaosat_main.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def congkhaosat_init(request):
    """
    API khởi tạo phiếu khảo sát - trả về danh sách câu hỏi
    """
    try:
        data = json.loads(request.body) if request.body else {}
        survey_id = data.get('survey_id')
        
        if not survey_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu survey_id'
            }, status=400)
        
        survey = get_object_or_404(SurveyModel, id=survey_id, status='active')
        
        # Kiểm tra thời gian khảo sát
        now = timezone.now()
        if survey.start_date and now < survey.start_date:
            return JsonResponse({
                'success': False,
                'message': 'Khảo sát chưa bắt đầu. Vui lòng quay lại sau.',
                'code': 'not_started'
            }, status=400)
        
        if survey.end_date and now > survey.end_date:
            if not survey.allow_after_deadline:
                return JsonResponse({
                    'success': False,
                    'message': 'Khảo sát đã kết thúc. Cảm ơn bạn đã quan tâm!',
                    'code': 'expired'
                }, status=400)
        
        # Lấy hoặc tạo response
        response_id = request.session.get(f'survey_response_{survey_id}')
        response = None
        
        if response_id:
            try:
                response = ResponseModel.objects.get(
                    id=response_id, 
                    survey=survey,
                    status='draft'
                )
            except ResponseModel.DoesNotExist:
                response = None
        
        # Nếu không có response draft, tạo mới
        if not response:
            response = ResponseModel.objects.create(
                survey=survey,
                status='draft',
                answers={},
                section_progress={},
                respondent_ip=request.META.get('REMOTE_ADDR'),
                respondent_device_id=request.META.get('HTTP_USER_AGENT', '')[:255],
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            request.session[f'survey_response_{survey_id}'] = response.id
        
        # Lấy sections và questions
        sections_data = []
        for section in survey.sections.all().order_by('order'):
            questions_data = []
            for question in section.questions.all().order_by('order'):
                questions_data.append({
                    'id': question.id,
                    'title': question.title,
                    'description': question.description,
                    'question_type_id': question.question_type_id,
                    'question_type_code': question.question_type.code if question.question_type else None,
                    'question_type_name': question.question_type.name if question.question_type else None,
                    'is_required': question.is_required,
                    'order': question.order,
                    'options': question.options,
                    'config': question.config,
                    'component_type': question.component_type,
                })
            
            # Tính tiến độ của section này
            progress = 0
            if response.section_progress and section.code in response.section_progress:
                progress = response.section_progress[section.code]
            elif questions_data:
                answered = 0
                for q in questions_data:
                    q_id = str(q['id'])
                    if q_id in response.answers and response.answers[q_id]:
                        answered += 1
                progress = round((answered / len(questions_data)) * 100) if questions_data else 0
            
            sections_data.append({
                'id': section.id,
                'code': section.code,
                'title': section.title,
                'description': section.description,
                'icon': section.icon,
                'order': section.order,
                'questions': questions_data,
                'progress': progress,
                'total_questions': len(questions_data)
            })
        
        # Tính tổng tiến độ
        total_progress = 0
        if sections_data:
            total_progress = sum(s['progress'] for s in sections_data) // len(sections_data)
        
        return JsonResponse({
            'success': True,
            'survey': {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'status': survey.status,
                'start_date': survey.start_date,
                'end_date': survey.end_date,
            },
            'response': {
                'id': response.id,
                'status': response.status,
                'answers': response.answers,
                'section_progress': response.section_progress,
                'total_progress': total_progress,
                'started_at': response.started_at,
            },
            'sections': sections_data,
        })
        
    except SurveyModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy khảo sát'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def congkhaosat_submit(request):
    """
    API lưu thông tin từ 3 bước và chuyển sang khảo sát
    """
    try:
        data = json.loads(request.body) if request.body else {}
        survey_id = data.get('survey_id')
        response_id = data.get('response_id')
        
        if not survey_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu survey_id'
            }, status=400)
        
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # Lấy hoặc tạo response
        response = None
        if response_id:
            try:
                response = ResponseModel.objects.get(id=response_id, survey=survey)
            except ResponseModel.DoesNotExist:
                pass
        
        if not response:
            response = ResponseModel.objects.create(
                survey=survey,
                status='draft',
                answers={},
                section_progress={}
            )
        
        # Lưu thông tin từ 3 bước vào answers
        personal_info = {
            'agency': data.get('agency', ''),
            'role': data.get('role', ''),
            'full_name': data.get('full_name', ''),
            'position': data.get('position', ''),
            'department': data.get('department', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'notes': data.get('notes', ''),
            'assigned_forms': data.get('assigned_forms', []),
        }
        
        answers = response.answers or {}
        answers['_personal_info'] = personal_info
        response.answers = answers
        response.respondent_email = data.get('email', '')
        response.save()
        
        request.session[f'survey_response_{survey_id}'] = response.id
        
        return JsonResponse({
            'success': True,
            'message': 'Đã lưu thông tin thành công!',
            'response_id': response.id,
            'redirect_url': f'/survey/public/{survey_id}/',
        })
        
    except SurveyModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy khảo sát'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)