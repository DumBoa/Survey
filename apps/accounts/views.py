# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import transaction
import json
import logging

import re
from .models import User, Organization
from apps.analytics.models import TargetGroup
from apps.survey.models import Survey, SurveyParticipant, SurveyProgress, Response
logger = logging.getLogger(__name__)


# ============================================
# TRANG CHỦ - REDIRECT THEO LUỒNG MỚI
# ============================================

def accounts_main_render(request):
    """
    Trang chủ của accounts - hiển thị congkhaosat_main.html
    Nếu đã đăng nhập và là admin thì redirect sang analytics
    """
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            return redirect('/analytics/')
        
        # Nếu có tham số choose_group=true, hiển thị trang chọn nhóm (bỏ qua bước login)
        if request.GET.get('choose_group') == 'true':
            return render(request, 'accounts/congkhaosat_main.html', {
                'skip_login': True,
                'force_choose_group': True
            })
        
        # Nếu user đã có SĐT và không có tham số đặc biệt, redirect đến dashboard
        if request.user.phone_number:
            return redirect('/accounts/survey-dashboard/')
        
        # User chưa có SĐT, hiển thị trang chọn nhóm (bỏ qua bước login)
        return render(request, 'accounts/congkhaosat_main.html', {
            'skip_login': True
        })
    
    # Chưa đăng nhập -> vào congkhaosat_main (có bước login)
    return render(request, 'accounts/congkhaosat_main.html')

# ============================================
# HÀM TIỆN ÍCH
# ============================================

def is_admin_user(user):
    """Kiểm tra user có phải là Admin/Staff không"""
    return user.is_superuser or user.is_staff


def get_redirect_url_based_on_role(user):
    """Xác định URL redirect dựa trên role"""
    if is_admin_user(user):
        return '/analytics/'
    return '/accounts/survey-dashboard/'


# ============================================
# LOGOUT
# ============================================

@login_required
def logout_view(request):
    """Đăng xuất và quay về trang chủ accounts"""
    logout(request)
    return redirect('/accounts/')  # Về congkhaosat_main


# ============================================
# LOGIN ADMIN - Dành cho Quản trị viên
# ============================================

@require_http_methods(["GET", "POST"])
@csrf_exempt
def login_view(request):
    """
    Trang đăng nhập dành cho Admin/Staff
    """
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(get_redirect_url_based_on_role(request.user))
        return render(request, 'accounts/login.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')
            remember = data.get('remember', False)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ!'
            }, status=400)
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not is_admin_user(user):
                return JsonResponse({
                    'success': False,
                    'message': 'Tài khoản này không có quyền Quản trị. Vui lòng sử dụng trang đăng nhập dành cho User.'
                }, status=403)
            
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


# ============================================
# API LOGIN CHO CỔNG KHẢO SÁT (congkhaosat_main)
# ============================================

@require_http_methods(["POST"])
@csrf_exempt
def congkhaosat_login_api(request):
    """
    API đăng nhập cho cổng khảo sát (Bước 1)
    """
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ!'
        }, status=400)
    
    if not username or not password:
        return JsonResponse({
            'success': False,
            'message': 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'
        }, status=400)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if is_admin_user(user):
            return JsonResponse({
                'success': False,
                'message': 'Tài khoản này là Quản trị viên. Vui lòng sử dụng trang đăng nhập dành cho Admin.'
            }, status=403)
        
        login(request, user)
        
        if not remember:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(1209600)
        
        return JsonResponse({
            'success': True,
            'message': 'Đăng nhập thành công!',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name() or user.username,
                'email': user.email or '',
                'phone': user.phone_number or '',
                'position': user.position or '',
                'organization': user.organization.name if user.organization else '',
                'organization_id': user.organization.id if user.organization else None,
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Sai tên đăng nhập hoặc mật khẩu!'
        }, status=401)


@require_http_methods(["POST"])
@csrf_exempt
def congkhaosat_logout_api(request):
    """
    API đăng xuất cho cổng khảo sát
    """
    logout(request)
    return JsonResponse({'success': True})


@require_http_methods(["GET"])
def congkhaosat_check_auth(request):
    """
    Kiểm tra trạng thái đăng nhập cho cổng khảo sát
    """
    if request.user.is_authenticated and not is_admin_user(request.user):
        return JsonResponse({
            'logged_in': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email or '',
                'phone': request.user.phone_number or '',
                'position': request.user.position or '',
                'organization': request.user.organization.name if request.user.organization else '',
                'organization_id': request.user.organization.id if request.user.organization else None,
            }
        })
    return JsonResponse({'logged_in': False})


# ============================================
# API XÁC MINH SỐ ĐIỆN THOẠI (MỚI)
# ============================================

# apps/accounts/views.py

import re  # Thêm import re ở đầu file

def validate_phone_number(phone):
    """
    Validate số điện thoại Việt Nam
    - 10 hoặc 11 số
    - Bắt đầu bằng 0 hoặc 84
    - Đầu số hợp lệ: 09, 08, 07, 03, 05, 02
    """
    if not phone:
        return False, "Vui lòng nhập số điện thoại"
    
    # Xóa khoảng trắng và ký tự đặc biệt
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Kiểm tra chỉ chứa số
    if not phone.isdigit():
        return False, "Số điện thoại không hợp lệ"
    
    # Kiểm tra độ dài (10 hoặc 11 số)
    if len(phone) not in [10, 11]:
        return False, "Số điện thoại không hợp lệ"
    
    # Kiểm tra đầu số hợp lệ
    valid_prefixes = ['09', '08', '07', '03', '05', '02', '01']
    if not any(phone.startswith(prefix) for prefix in valid_prefixes):
        return False, "Đầu số điện thoại không hợp lệ"
    
    return True, phone


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def congkhaosat_verify_phone(request):
    """
    API xác minh số điện thoại - Bước 3
    """
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number', '').strip()
        target_group_id = data.get('target_group_id')
        
        user = request.user
        
        # Validate phone number
        is_valid, result = validate_phone_number(phone_number)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'message': result
            }, status=400)
        
        phone_number = result  # Lấy SĐT đã được format
        
        if not target_group_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin nhóm đối tượng!'
            }, status=400)
        
        # Lấy target group
        try:
            target_group = TargetGroup.objects.get(id=target_group_id, is_active=True)
        except TargetGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhóm đối tượng!'
            }, status=404)
        
        # Lưu target_group_code vào session
        request.session['current_target_group_code'] = target_group.code
        
        # Lấy danh sách form từ group
        assigned_forms = target_group.forms or []
        
        # Kiểm tra user hiện tại đã có SĐT này chưa
        if not user.phone_number:
            # Kiểm tra SĐT này đã được đăng ký với user khác chưa
            existing_user = User.objects.filter(phone_number=phone_number).exclude(id=user.id).first()
            if existing_user:
                return JsonResponse({
                    'success': False,
                    'message': f'Số điện thoại {phone_number} đã được đăng ký với tài khoản khác. Vui lòng liên hệ quản trị viên!'
                }, status=400)
            
            user.phone_number = phone_number
            user.save()
            logger.info(f"Updated user phone number: {phone_number}")
        else:
            # User đã có SĐT, kiểm tra xem có đang nhập SĐT khác không
            if user.phone_number != phone_number:
                # Kiểm tra SĐT mới đã được đăng ký với user khác chưa
                existing_user = User.objects.filter(phone_number=phone_number).exclude(id=user.id).first()
                if existing_user:
                    return JsonResponse({
                        'success': False,
                        'message': f'Số điện thoại {phone_number} đã được đăng ký với tài khoản khác. Vui lòng liên hệ quản trị viên!'
                    }, status=400)
                
                # Cập nhật SĐT mới
                user.phone_number = phone_number
                user.save()
                logger.info(f"Updated user phone number from {user.phone_number} to {phone_number}")
        
        # Lấy survey active đầu tiên
        active_survey = Survey.objects.filter(status='active').order_by('-created_at').first()
        
        if not active_survey:
            return JsonResponse({
                'success': False,
                'message': 'Hiện chưa có đợt khảo sát nào đang hoạt động!'
            }, status=400)
        
        # Tìm participant theo user, SĐT và target_group_code
        participant = SurveyParticipant.objects.filter(
            user=user,
            phone=phone_number,
            target_group_code=target_group.code,
            status='draft'
        ).first()
        
        with transaction.atomic():
            if participant:
                # Cập nhật participant cũ
                participant.assigned_forms = assigned_forms
                participant.target_group_name = target_group.name
                participant.survey = active_survey
                participant.session_key = request.session.session_key or ''
                participant.ip_address = request.META.get('REMOTE_ADDR')
                participant.user_agent = request.META.get('HTTP_USER_AGENT', '')
                participant.save()
                
                # Lấy danh sách progress hiện có
                existing_progresses = SurveyProgress.objects.filter(participant=participant)
                existing_form_codes = set(progress.form_code for progress in existing_progresses)
                
                # Tạo progress mới cho các form chưa có
                for form_code in assigned_forms:
                    if form_code not in existing_form_codes:
                        survey = Survey.objects.filter(code=form_code, status='active').first()
                        if survey:
                            SurveyProgress.objects.create(
                                participant=participant,
                                survey=survey,
                                form_code=form_code,
                                status='not_started'
                            )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Đã tìm thấy dữ liệu khảo sát của bạn!',
                    'is_existing': True,
                    'participant_id': participant.id,
                    'progress_count': SurveyProgress.objects.filter(participant=participant).count()
                })
            else:
                # Tạo participant mới
                participant = SurveyParticipant.objects.create(
                    survey=active_survey,
                    user=user,
                    full_name=user.get_full_name() or user.username,
                    email=user.email or '',
                    phone=phone_number,
                    position=user.position or '',
                    department=user.organization.name if user.organization else '',
                    agency=user.organization.name if user.organization else '',
                    assigned_forms=assigned_forms,
                    target_group_code=target_group.code,
                    target_group_name=target_group.name,
                    status='draft',
                    session_key=request.session.session_key or '',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
                
                # Tạo progress cho từng form
                for form_code in assigned_forms:
                    survey = Survey.objects.filter(code=form_code, status='active').first()
                    if survey:
                        SurveyProgress.objects.create(
                            participant=participant,
                            survey=survey,
                            form_code=form_code,
                            status='not_started'
                        )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Tạo mới dữ liệu khảo sát thành công!',
                    'is_existing': False,
                    'participant_id': participant.id,
                    'progress_count': len(assigned_forms)
                })
        
    except Exception as e:
        logger.error(f"Error verifying phone: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ============================================
# API LẤY KHẢO SÁT THEO NHÓM ĐỐI TƯỢNG
# ============================================

# apps/accounts/views.py

@login_required
def get_surveys_by_group_api(request, group_id):
    """API lấy danh sách khảo sát theo nhóm - Phân biệt theo session_key"""
    try:
        user = request.user
        session_key = request.session.session_key
        
        # Lấy group
        try:
            group = TargetGroup.objects.get(id=group_id, is_active=True)
        except TargetGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhóm đối tượng'
            }, status=404)
        
        # Lấy danh sách form codes từ group
        form_codes = group.forms or []
        
        if not form_codes:
            return JsonResponse({
                'success': True,
                'data': [],
                'message': 'Nhóm này chưa có biểu mẫu nào'
            })
        
        # Lấy danh sách survey từ form codes
        surveys = Survey.objects.filter(
            code__in=form_codes,
            status='active'
        ).order_by('code')
        
        # Lấy participant theo user + session_key
        participant = SurveyParticipant.objects.filter(
            user=user,
            session_key=session_key,
            target_group_code=group.code,
            status='draft'
        ).order_by('-created_at').first()
        
        if not participant:
            return JsonResponse({
                'success': True,
                'data': [],
                'message': 'Chưa có dữ liệu participant cho session này'
            })
        
        # Lấy progress cho từng survey
        data = []
        for survey in surveys:
            progress = SurveyProgress.objects.filter(
                participant=participant,
                form_code=survey.code
            ).first()
            
            if not progress:
                progress = SurveyProgress.objects.create(
                    participant=participant,
                    survey=survey,
                    form_code=survey.code,
                    status='not_started'
                )
            
            # Tính tiến độ
            progress_percent = 0
            status = progress.status
            
            if progress.response:
                answers = progress.response.answers or {}
                total_questions = 0
                answered = 0
                
                if survey:
                    for section in survey.sections.all():
                        for question in section.questions.all():
                            if question.question_type and question.question_type.code not in ['title', 'paragraph']:
                                total_questions += 1
                                if str(question.id) in answers:
                                    answered += 1
                    
                    if total_questions > 0:
                        progress_percent = round((answered / total_questions) * 100)
                        if progress_percent >= 100 and status != 'completed':
                            status = 'completed'
                            progress.status = 'completed'
                            progress.completed_at = timezone.now()
                            progress.save()
                        elif progress_percent > 0 and status == 'not_started':
                            status = 'in_progress'
                            progress.status = 'in_progress'
                            progress.save()
            
            data.append({
                'id': survey.id,
                'code': survey.code,
                'title': survey.title,
                'description': survey.description or '',
                'question_count': survey.get_question_count() if hasattr(survey, 'get_question_count') else 0,
                'status': status,
                'progress_id': progress.id,
                'progress_percent': progress_percent,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error in get_surveys_by_group_api: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ============================================
# API BẮT ĐẦU KHẢO SÁT (SAU KHI NHẬP THÔNG TIN CÁ NHÂN)
# ============================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def congkhaosat_start_survey(request):
    """
    API bắt đầu khảo sát sau khi nhập thông tin cá nhân
    """
    try:
        data = json.loads(request.body)
        survey_id = data.get('survey_id')
        progress_id = data.get('progress_id')
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        position = data.get('position', '').strip()
        department = data.get('department', '').strip()
        target_group_id = data.get('target_group_id')
        
        user = request.user
        
        # Validate
        if not survey_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu ID khảo sát'
            }, status=400)
        
        if not full_name or not email or not phone or not position:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng điền đầy đủ thông tin cá nhân'
            }, status=400)
        
        # Lấy survey
        try:
            survey = Survey.objects.get(id=survey_id, status='active')
        except Survey.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy khảo sát'
            }, status=404)
        
        # Lấy hoặc tạo participant
        participant = SurveyParticipant.objects.filter(
            user=user,
            phone=phone,
            status='draft'
        ).order_by('-created_at').first()
        
        if not participant:
            participant = SurveyParticipant.objects.create(
                survey=survey,
                user=user,
                full_name=full_name,
                email=email,
                phone=phone,
                position=position,
                department=department or user.organization.name if user.organization else '',
                agency=user.organization.name if user.organization else '',
                assigned_forms=[survey.code],
                status='draft',
                session_key=request.session.session_key or '',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        else:
            # Cập nhật thông tin cá nhân cho participant
            participant.full_name = full_name
            participant.email = email
            participant.phone = phone
            participant.position = position
            if department:
                participant.department = department
            participant.save()
        
        # Lấy hoặc tạo progress
        if progress_id:
            try:
                progress = SurveyProgress.objects.get(id=progress_id)
            except SurveyProgress.DoesNotExist:
                progress = None
        else:
            progress = SurveyProgress.objects.filter(
                participant=participant,
                form_code=survey.code
            ).first()
        
        if not progress:
            progress = SurveyProgress.objects.create(
                participant=participant,
                survey=survey,
                form_code=survey.code,
                status='in_progress',
                started_at=timezone.now()
            )
        
        # Tạo response nếu chưa có
        if not progress.response:
            response = Response.objects.create(
                survey=survey,
                status='draft',
                answers={},
                section_progress={},
                user=user,
                respondent_name=full_name,
                respondent_email=email,
                respondent_phone=phone,
                respondent_position=position,
                respondent_department=department or user.organization.name if user.organization else '',
                respondent_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            progress.response = response
            progress.status = 'in_progress'
            progress.started_at = timezone.now()
            progress.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Bắt đầu khảo sát thành công!',
            'redirect_url': f'/survey/public/{survey.id}/?progress_id={progress.id}'
        })
        
    except Exception as e:
        logger.error(f"Error in congkhaosat_start_survey: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ============================================
# SURVEY DASHBOARD (Giữ nguyên)
# ============================================

# apps/accounts/views.py

@login_required
def survey_dashboard(request):
    """Dashboard của người khảo sát - Phân biệt theo session_key"""
    user = request.user
    
    if is_admin_user(user):
        return redirect('/analytics/')
    
    # Lấy target group code từ session
    target_group_code = request.session.get('current_target_group_code')
    
    # Lấy session_key
    session_key = request.session.session_key
    
    logger.info(f"Dashboard - User: {user.username}, Session: {session_key}, TargetGroupCode: {target_group_code}")
    
    # LẤY PARTICIPANT THEO USER + SESSION_KEY + TARGET_GROUP_CODE
    participant = None
    
    if target_group_code and session_key:
        participant = SurveyParticipant.objects.filter(
            user=user,
            session_key=session_key,
            target_group_code=target_group_code,
            status='draft'
        ).order_by('-created_at').first()
        logger.info(f"Found participant by session + target: {participant.id if participant else 'None'}")
    
    # Nếu chưa có, lấy participant mới nhất của session này
    if not participant and session_key:
        participant = SurveyParticipant.objects.filter(
            user=user,
            session_key=session_key,
            status='draft'
        ).order_by('-created_at').first()
        logger.info(f"Found latest participant by session: {participant.id if participant else 'None'}")
    
    # Nếu chưa có participant, render trang với thông báo
    if not participant:
        # Render dashboard với thông báo chưa có dữ liệu
        return render(request, 'accounts/survey_dashboard.html', {
            'error': 'Bạn chưa chọn nhóm đối tượng. Vui lòng quay lại trang chủ để chọn nhóm.',
            'no_participant': True,
            'user': user,
        })
    
    # Lưu target_group_code vào session nếu chưa có
    if not target_group_code and participant.target_group_code:
        request.session['current_target_group_code'] = participant.target_group_code
        target_group_code = participant.target_group_code
        logger.info(f"Set session target_group_code from participant: {target_group_code}")
    
    # Lấy danh sách progress
    progress_list = []
    assigned_forms = participant.assigned_forms or []
    
    logger.info(f"Assigned forms for participant {participant.id}: {assigned_forms}")
    
    for form_code in assigned_forms:
        # Lấy hoặc tạo progress
        progress = SurveyProgress.objects.filter(
            participant=participant,
            form_code=form_code
        ).first()
        
        if not progress:
            survey_obj = Survey.objects.filter(code=form_code, status='active').first()
            progress = SurveyProgress.objects.create(
                participant=participant,
                survey=survey_obj,
                form_code=form_code,
                status='not_started'
            )
        
        # Đảm bảo survey được gán
        if not progress.survey:
            survey_obj = Survey.objects.filter(code=form_code, status='active').first()
            if survey_obj:
                progress.survey = survey_obj
                progress.save()
        
        # Tính tiến độ
        if progress.response:
            answers = progress.response.answers or {}
            total_questions = 0
            answered = 0
            
            if progress.survey:
                for section in progress.survey.sections.all():
                    for question in section.questions.all():
                        if question.question_type and question.question_type.code not in ['title', 'paragraph']:
                            total_questions += 1
                            if str(question.id) in answers:
                                answered += 1
                
                if total_questions > 0:
                    progress.progress_percent = round((answered / total_questions) * 100)
                    if progress.progress_percent >= 100 and progress.status != 'completed':
                        progress.status = 'completed'
                        progress.completed_at = timezone.now()
                    progress.save()
        
        progress_list.append(progress)
    
    # Sắp xếp
    status_order = {'in_progress': 0, 'not_started': 1, 'completed': 2}
    progress_list.sort(key=lambda p: status_order.get(p.status, 3))
    
    total = len(progress_list)
    completed = sum(1 for p in progress_list if p.status == 'completed')
    in_progress = sum(1 for p in progress_list if p.status == 'in_progress')
    not_started = sum(1 for p in progress_list if p.status == 'not_started')
    overall_progress = round((completed / total) * 100) if total > 0 else 0
    
    context = {
        'participant': participant,
        'progresses': progress_list,
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'not_started': not_started,
        'overall_progress': overall_progress,
        'can_update_info': True,
        'user': user,
        'target_group_name': participant.target_group_name or 'Chưa có nhóm',
        'target_group_code': participant.target_group_code or '',
        'session_key': session_key,
    }
    
    return render(request, 'accounts/survey_dashboard.html', context)


# ============================================
# TIẾP TỤC LÀM KHẢO SÁT
# ============================================

@login_required
def survey_dashboard_continue(request, progress_id):
    """
    Tiếp tục làm một bài khảo sát cụ thể
    """
    try:
        progress = SurveyProgress.objects.get(id=progress_id)
    except SurveyProgress.DoesNotExist:
        return redirect('accounts:survey_dashboard')
    
    if progress.participant.user != request.user:
        return redirect('accounts:survey_dashboard')
    
    if progress.status == 'completed':
        return render(request, 'accounts/survey_dashboard.html', {
            'message': 'Bạn đã hoàn thành khảo sát này.',
            'progress': progress,
            'can_update_info': True,
        })
    
    if not progress.response:
        response = Response.objects.create(
            survey=progress.survey,
            status='draft',
            answers={},
            section_progress={},
            user=request.user,
            respondent_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        progress.response = response
        progress.status = 'in_progress'
        progress.started_at = timezone.now()
        progress.save()
    
    return redirect(f'/survey/public/{progress.survey.id}/?progress_id={progress.id}')


# ============================================
# API PUBLIC - Lấy danh sách đơn vị
# ============================================

@login_required
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


# ============================================
# API PUBLIC - Lấy danh sách nhóm đối tượng
# ============================================

def get_target_groups_api(request):
    """
    API lấy danh sách nhóm đối tượng để hiển thị
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
# API PUBLIC - Lấy danh sách biểu mẫu
# ============================================

def get_survey_forms_api(request):
    """
    API lấy danh sách tất cả biểu mẫu khảo sát
    """
    try:
        surveys = Survey.objects.filter(status='active').values(
            'id', 'code', 'title', 'description', 'status'
        ).order_by('code')
        
        data = []
        for survey in surveys:
            question_count = 0
            try:
                from apps.survey.models import Section, Question
                sections = Section.objects.filter(survey_id=survey['id'])
                for section in sections:
                    question_count += Question.objects.filter(section=section).count()
            except:
                pass
            
            data.append({
                'id': survey['id'],
                'code': survey['code'] or f"BM-{str(survey['id']).zfill(2)}",
                'name': survey['title'],
                'description': survey['description'] or '',
                'status': survey['status'],
                'question_count': question_count,
            })
        
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
# EXPORT PDF
# ============================================

import io
import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings

logger = logging.getLogger(__name__)


@login_required(login_url='/accounts/login/')
def export_response_pdf(request, response_id):
    """
    Xuất phiếu trả lời khảo sát ra file PDF - Hỗ trợ Tiếng Việt
    """
    try:
        from apps.survey.models import Response
        import json
        
        response = get_object_or_404(Response, id=response_id)
        
        if response.user != request.user:
            return HttpResponse('Bạn không có quyền truy cập!', status=403)
        
        survey = response.survey
        answers = response.answers or {}
        
        # Đăng ký font
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttf",
            os.path.join(settings.BASE_DIR, 'fonts', 'DejaVuSans.ttf'),
            os.path.join(settings.BASE_DIR, 'fonts', 'arial.ttf'),
        ]
        
        font_available = False
        font_name = 'Helvetica'
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('VietnamFont', font_path))
                    font_name = 'VietnamFont'
                    font_available = True
                    break
                except Exception as e:
                    continue
        
        if not font_available:
            logger.warning("Không tìm thấy font hỗ trợ Tiếng Việt, sử dụng font mặc định")
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName=font_name,
            encoding='utf-8'
        )
        
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            fontName=font_name,
            encoding='utf-8'
        )
        
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            fontName=font_name,
            encoding='utf-8'
        )
        
        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            fontName=font_name,
            textColor=colors.HexColor('#2563eb'),
            encoding='utf-8'
        )
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName=font_name,
            encoding='utf-8'
        )
        
        story = []
        
        # Tiêu đề
        story.append(Paragraph("PHIẾU TRẢ LỜI KHẢO SÁT", title_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>{survey.title}</b>", heading_style))
        story.append(Spacer(1, 4))
        
        # Thông tin người trả lời
        user_info = [
            ['Họ và tên:', response.respondent_name or response.user.get_full_name() or 'Chưa có'],
            ['Email:', response.respondent_email or response.user.email or 'Chưa có'],
            ['Thời gian nộp:', response.submitted_at.strftime('%H:%M %d/%m/%Y') if response.submitted_at else 'Chưa nộp'],
            ['Thời gian làm bài:', f"{response.time_taken} giây" if response.time_taken else 'Chưa có'],
        ]
        
        info_table = Table(user_info, colWidths=[60*mm, 90*mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 12))
        
        # Duyệt qua các section và câu hỏi
        sections = survey.sections.all().order_by('order')
        question_counter = 0
        
        for section in sections:
            story.append(Paragraph(f"<b>{section.title}</b>", heading_style))
            if section.description:
                story.append(Paragraph(section.description, info_style))
            
            questions = section.questions.all().order_by('order')
            
            for question in questions:
                question_counter += 1
                q_id = str(question.id)
                answer = answers.get(q_id, '')
                
                if question.question_type and question.question_type.code in ['title', 'paragraph']:
                    continue
                
                q_text = f"{question_counter}. {question.title}"
                story.append(Paragraph(q_text, question_style))
                
                if answer:
                    if isinstance(answer, dict) and answer.get('type') == 'grid':
                        grid_data = answer.get('data', [])
                        
                        if grid_data and len(grid_data) > 0:
                            num_cols = len(grid_data[0]) if grid_data else 0
                            
                            if num_cols > 0:
                                grid_table_data = []
                                
                                headers = ['Tiêu chí']
                                if question.config and question.config.get('criteria_label'):
                                    headers = [question.config.get('criteria_label', 'Tiêu chí')]
                                
                                if question.config and question.config.get('scale'):
                                    for item in question.config.get('scale', []):
                                        if isinstance(item, dict):
                                            headers.append(item.get('label', str(item.get('value', ''))))
                                        else:
                                            headers.append(str(item))
                                else:
                                    for i in range(1, num_cols):
                                        headers.append(str(i))
                                
                                while len(headers) < num_cols:
                                    headers.append(str(len(headers)))
                                
                                grid_table_data.append(headers)
                                
                                for row in grid_data:
                                    row_data = []
                                    for cell in row:
                                        if cell is None:
                                            row_data.append('')
                                        else:
                                            row_data.append(str(cell))
                                    grid_table_data.append(row_data)
                                
                                col_widths = [50*mm]
                                for i in range(1, num_cols):
                                    col_widths.append(20*mm)
                                
                                grid_table = Table(grid_table_data, colWidths=col_widths)
                                grid_table.setStyle(TableStyle([
                                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ]))
                                story.append(grid_table)
                            else:
                                story.append(Paragraph("<i>Không có dữ liệu</i>", answer_style))
                        else:
                            story.append(Paragraph("<i>Không có dữ liệu</i>", answer_style))
                    
                    elif isinstance(answer, list):
                        answer_text = ', '.join(str(a) for a in answer if a)
                        if answer_text:
                            story.append(Paragraph(answer_text, answer_style))
                        else:
                            story.append(Paragraph("<i>Chưa trả lời</i>", answer_style))
                    
                    elif isinstance(answer, dict):
                        if answer:
                            answer_text = ', '.join(f"{k}: {v}" for k, v in answer.items() if v)
                            if answer_text:
                                story.append(Paragraph(answer_text, answer_style))
                            else:
                                story.append(Paragraph("<i>Chưa trả lời</i>", answer_style))
                        else:
                            story.append(Paragraph("<i>Chưa trả lời</i>", answer_style))
                    
                    else:
                        if str(answer).strip():
                            story.append(Paragraph(str(answer), answer_style))
                        else:
                            story.append(Paragraph("<i>Chưa trả lời</i>", answer_style))
                else:
                    story.append(Paragraph("<i>Chưa trả lời</i>", answer_style))
                
                story.append(Spacer(1, 4))
            
            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
            story.append(Spacer(1, 8))
        
        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"<i>Xuất ngày {timezone.now().strftime('%H:%M %d/%m/%Y')}</i>",
            info_style
        ))
        
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        response_pdf = HttpResponse(content_type='application/pdf')
        response_pdf['Content-Disposition'] = f'attachment; filename="khao_sat_{survey.code}_{response.id}.pdf"'
        response_pdf.write(pdf_data)
        
        return response_pdf
        
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Lỗi khi xuất PDF: {str(e)}", status=500)


# ============================================
# API TẠO PARTICIPANT (Bước 3 - Xác nhận)
# ============================================

# apps/accounts/views.py

# apps/accounts/views.py

# apps/accounts/views.py

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def congkhaosat_create_participant(request):
    """API tạo participant sau khi xác nhận - Lưu session_key"""
    try:
        data = json.loads(request.body)
        target_group_id = data.get('target_group_id')
        organization_id = data.get('organization_id')
        
        user = request.user
        
        if not target_group_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin nhóm đối tượng'
            }, status=400)
        
        try:
            target_group = TargetGroup.objects.get(id=target_group_id, is_active=True)
        except TargetGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhóm đối tượng'
            }, status=404)
        
        organization = None
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                pass
        
        assigned_forms = target_group.forms or []
        active_survey = Survey.objects.filter(status='active').order_by('-created_at').first()
        
        # Lấy session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        logger.info(f"Create participant - User: {user.username}, Session: {session_key}, TargetGroup: {target_group.code}")
        
        # Lưu target_group_code vào session
        request.session['current_target_group_code'] = target_group.code
        
        # TÌM PARTICIPANT THEO USER + SESSION_KEY + TARGET_GROUP_CODE
        existing_participant = SurveyParticipant.objects.filter(
            user=user,
            session_key=session_key,
            target_group_code=target_group.code,
            status='draft'
        ).first()
        
        if existing_participant:
            logger.info(f"Found existing participant: {existing_participant.id}")
            existing_participant.assigned_forms = assigned_forms
            existing_participant.target_group_name = target_group.name
            existing_participant.department = organization.name if organization else ''
            existing_participant.agency = organization.name if organization else ''
            existing_participant.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cập nhật participant thành công',
                'participant_id': existing_participant.id
            })
        
        # Tạo participant mới với session_key
        participant = SurveyParticipant.objects.create(
            survey=active_survey,
            user=user,
            full_name=user.get_full_name() or user.username,
            email=user.email or '',
            phone='',  # Không cần SĐT
            position=user.position or '',
            department=organization.name if organization else '',
            agency=organization.name if organization else '',
            assigned_forms=assigned_forms,
            target_group_code=target_group.code,
            target_group_name=target_group.name,
            status='draft',
            session_key=session_key,  # ← LƯU SESSION_KEY
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        logger.info(f"Created new participant: {participant.id} with session: {session_key}")
        
        # Tạo progress cho từng form
        for form_code in assigned_forms:
            survey = Survey.objects.filter(code=form_code, status='active').first()
            if survey:
                SurveyProgress.objects.create(
                    participant=participant,
                    survey=survey,
                    form_code=form_code,
                    status='not_started'
                )
                logger.info(f"Created progress for form: {form_code}")
        
        return JsonResponse({
            'success': True,
            'message': 'Tạo participant thành công',
            'participant_id': participant.id
        })
        
    except Exception as e:
        logger.error(f"Error creating participant: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
# apps/accounts/views.py

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def switch_target_group_api(request):
    """
    API chuyển đổi nhóm đối tượng
    """
    try:
        data = json.loads(request.body)
        target_group_id = data.get('target_group_id')
        
        user = request.user
        
        if not target_group_id:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin nhóm đối tượng'
            }, status=400)
        
        try:
            target_group = TargetGroup.objects.get(id=target_group_id, is_active=True)
        except TargetGroup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhóm đối tượng'
            }, status=404)
        
        # Lưu target_group_code vào session
        request.session['current_target_group_code'] = target_group.code
        logger.info(f"Switch group - User: {user.username}, New group: {target_group.code}")
        
        return JsonResponse({
            'success': True,
            'message': f'Đã chuyển sang nhóm "{target_group.name}"',
            'target_group_code': target_group.code
        })
        
    except Exception as e:
        logger.error(f"Error switching target group: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)



# apps/accounts/views.py

@login_required
def get_user_target_groups_api(request):
    """
    API lấy danh sách nhóm đối tượng mà user đã tham gia
    """
    try:
        user = request.user
        
        if not user.phone_number:
            return JsonResponse({
                'success': True,
                'data': []
            })
        
        # Lấy tất cả participant của user
        participants = SurveyParticipant.objects.filter(
            user=user,
            phone=user.phone_number
        ).order_by('-created_at')
        
        groups_data = []
        seen_group_codes = set()
        current_group_code = request.session.get('current_target_group_code')
        
        for p in participants:
            if p.target_group_code and p.target_group_code not in seen_group_codes:
                seen_group_codes.add(p.target_group_code)
                
                # Tìm TargetGroup để lấy id
                target_group = TargetGroup.objects.filter(code=p.target_group_code).first()
                
                groups_data.append({
                    'id': target_group.id if target_group else None,
                    'code': p.target_group_code,
                    'name': p.target_group_name or p.target_group_code,
                    'form_count': len(p.assigned_forms or []),
                    'is_current': p.target_group_code == current_group_code
                })
        
        logger.info(f"User target groups - User: {user.username}, Groups: {len(groups_data)}")
        
        return JsonResponse({
            'success': True,
            'data': groups_data
        })
    except Exception as e:
        logger.error(f"Error getting user target groups: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)