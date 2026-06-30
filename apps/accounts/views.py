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
from apps.survey.models import Survey as SurveyModel, Response as ResponseModel, SurveyParticipant


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
            return redirect('/analytics/')
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
                'redirect_url': '/analytics/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Sai tên đăng nhập hoặc mật khẩu!'
            }, status=401)

from apps.accounts.models import Organization

@login_required(login_url='/accounts/login/')
def get_organizations_api(request):
    """
    API lấy danh sách đơn vị để hiển thị trong dropdown
    """
    try:
        organizations = Organization.objects.filter(is_active=True).order_by('name')
        data = [{
            'id': org.id,
            'name': org.name,
            'code': org.code,
            'level': org.level,
            'level_display': org.get_level_display(),
        } for org in organizations]
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
from apps.analytics.models import TargetGroup

def get_target_groups_api(request):
    """
    API lấy danh sách nhóm đối tượng để hiển thị trong cổng khảo sát
    """
    try:
        groups = TargetGroup.objects.filter(is_active=True).order_by('code')
        data = [{
            'id': group.id,
            'code': group.code,
            'name': group.name,
            'description': group.description,
            'icon': group.icon,
            'forms': group.forms if group.forms else [],
        } for group in groups]
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
# ============================================
# CỔNG KHẢO SÁT CÔNG CHỨC - 3 BƯỚC
# ============================================

def congkhaosat_view(request):
    """
    Trang cổng khảo sát 3 bước
    """
    survey_id = request.GET.get('survey_id')
    
    if survey_id:
        survey = get_object_or_404(SurveyModel, id=survey_id)
    else:
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
        
        if not survey_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu survey_id'
            }, status=400)
        
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # Lấy session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # ============================================================
        # TÌM HOẶC TẠO SURVEY PARTICIPANT
        # ============================================================
        participant = None
        
        # Tìm participant theo session
        if session_key:
            participant = SurveyParticipant.objects.filter(
                survey=survey,
                session_key=session_key,
                status='draft'
            ).first()
        
        # Nếu chưa có, tìm theo email (trường hợp user quay lại sau khi mất session)
        if not participant:
            email = data.get('email', '')
            if email:
                participant = SurveyParticipant.objects.filter(
                    survey=survey,
                    email=email,
                    status='draft'
                ).first()
        
        if not participant:
            # Tạo mới participant
            participant = SurveyParticipant(
                survey=survey,
                session_key=session_key,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status='draft'
            )
        
        # Cập nhật thông tin từ form
        participant.agency = data.get('agency', '')
        participant.target_group_code = data.get('target_group_code', '')
        participant.target_group_name = data.get('target_group_name', '')
        participant.full_name = data.get('full_name', '')
        participant.position = data.get('position', '')
        participant.department = data.get('department', '')
        participant.phone = data.get('phone', '')
        participant.email = data.get('email', '')
        participant.notes = data.get('notes', '')
        participant.assigned_forms = data.get('assigned_forms', [])
        
        # ============================================================
        # SỬA: GÁN USER CHO PARTICIPANT - LẤY USER OBJECT THỰC TẾ
        # ============================================================
        if request.user.is_authenticated:
            # Lấy user object thực tế từ database
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                actual_user = User.objects.get(id=request.user.id)
                participant.user = actual_user
            except Exception as e:
                print(f"Error getting user: {e}")
                # Nếu không lấy được user, bỏ qua
        
        participant.save()
        
        # ============================================================
        # TÌM HOẶC TẠO RESPONSE
        # ============================================================
        response = None
        
        # Kiểm tra xem participant đã có response chưa
        if participant.response:
            response = participant.response
        else:
            # Tìm response theo session
            response_id = request.session.get(f'survey_response_{survey_id}')
            if response_id:
                try:
                    response = ResponseModel.objects.get(
                        id=response_id,
                        survey=survey,
                        status='draft'
                    )
                except ResponseModel.DoesNotExist:
                    response = None
        
        if not response:
            # Tạo mới response
            response = ResponseModel(
                survey=survey,
                status='draft',
                answers={},
                section_progress={},
                respondent_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # SỬA: GÁN USER CHO RESPONSE
            if request.user.is_authenticated:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    actual_user = User.objects.get(id=request.user.id)
                    response.user = actual_user
                    response.respondent_email = actual_user.email
                except Exception as e:
                    print(f"Error getting user for response: {e}")
            
            if participant.email:
                response.respondent_email = participant.email
            
            response.save()
            
            # Gán response vào participant
            participant.response = response
            participant.save()
        
        # Lưu thông tin cá nhân vào answers
        answers = response.answers or {}
        answers['_participant_info'] = {
            'agency': participant.agency,
            'target_group_code': participant.target_group_code,
            'target_group_name': participant.target_group_name,
            'full_name': participant.full_name,
            'position': participant.position,
            'department': participant.department,
            'phone': participant.phone,
            'email': participant.email,
            'notes': participant.notes,
            'assigned_forms': participant.assigned_forms,
        }
        response.answers = answers
        response.respondent_email = participant.email
        response.save()
        
        # Lưu vào session
        request.session[f'survey_response_{survey_id}'] = response.id
        request.session[f'survey_participant_{survey_id}'] = participant.id
        
        return JsonResponse({
            'success': True,
            'message': 'Đã lưu thông tin thành công!',
            'response_id': response.id,
            'participant_id': participant.id,
            'assigned_forms': participant.assigned_forms,
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
        import traceback
        print(f"Error in congkhaosat_submit: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)