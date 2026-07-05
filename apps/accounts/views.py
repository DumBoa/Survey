# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import json

from .models import User, Organization
from apps.analytics.models import TargetGroup
from apps.survey.models import Survey, SurveyParticipant, SurveyProgress, Response


# ============================================
# TRANG CHỦ
# ============================================

def accounts_main_render(request):
    """
    Trang chủ của accounts - redirect dựa trên trạng thái đăng nhập
    """
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            return redirect('/analytics/')
        return redirect('/accounts/survey-dashboard/')
    # Chưa đăng nhập -> vào trang user login
    return redirect('/accounts/user-login/')


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
    """Đăng xuất và quay về trang login"""
    logout(request)
    return redirect('/accounts/login/')


# ============================================
# LOGIN ADMIN - Dành cho Quản trị viên
# ============================================

# apps/accounts/views.py - Sửa hàm login_view

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
        
        # Debug log
        print(f"Admin login attempt: username={username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Kiểm tra nếu không phải admin thì không cho đăng nhập ở đây
            if not is_admin_user(user):
                return JsonResponse({
                    'success': False,
                    'message': 'Tài khoản này không có quyền Quản trị. Vui lòng sử dụng trang đăng nhập dành cho User tại /accounts/user-login/'
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
            print(f"Authentication failed for username: {username}")
            return JsonResponse({
                'success': False,
                'message': 'Sai tên đăng nhập hoặc mật khẩu!'
            }, status=401)


# ============================================
# LOGIN USER - Dành cho Người khảo sát
# ============================================

# apps/accounts/views.py - Sửa hàm user_login_view

@require_http_methods(["GET", "POST"])
@csrf_exempt
def user_login_view(request):
    """
    Trang đăng nhập dành cho User (người khảo sát)
    """
    if request.method == 'GET':
        if request.user.is_authenticated:
            if is_admin_user(request.user):
                return redirect('/analytics/')
            return redirect('/accounts/survey-dashboard/')
        return render(request, 'accounts/user_login.html')
    
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
        
        # Debug log
        print(f"User login attempt: username={username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Kiểm tra nếu là admin thì không cho đăng nhập ở đây
            if is_admin_user(user):
                return JsonResponse({
                    'success': False,
                    'message': 'Tài khoản này là Quản trị viên. Vui lòng sử dụng trang đăng nhập dành cho Admin tại /accounts/login/'
                }, status=403)
            
            login(request, user)
            
            if not remember:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            
            return JsonResponse({
                'success': True,
                'message': 'Đăng nhập thành công!',
                'redirect_url': '/accounts/survey-dashboard/'
            })
        else:
            # Debug log
            print(f"Authentication failed for username: {username}")
            return JsonResponse({
                'success': False,
                'message': 'Sai tên đăng nhập hoặc mật khẩu!'
            }, status=401)


# ============================================
# DASHBOARD USER - Dành cho người khảo sát
# ============================================

# apps/accounts/views.py - Hàm survey_dashboard

@login_required
def survey_dashboard(request):
    """
    Dashboard của người khảo sát
    Hiển thị danh sách biểu mẫu được gán dựa trên TargetGroup của user
    """
    user = request.user
    
    # Nếu là admin, chuyển sang analytics
    if is_admin_user(user):
        return redirect('/analytics/')
    
    # Lấy hoặc tạo SurveyParticipant cho user
    participant = SurveyParticipant.objects.filter(
        user=user,
        status='draft'
    ).order_by('-created_at').first()
    
    # Nếu chưa có participant, tạo mới với thông tin từ User
    if not participant:
        # Tìm survey đang active
        active_survey = Survey.objects.filter(status='active').order_by('-created_at').first()
        
        if not active_survey:
            return render(request, 'accounts/survey_dashboard.html', {
                'message': 'Hiện tại chưa có đợt khảo sát nào đang hoạt động.',
                'participant': None,
                'progresses': [],
                'total': 0,
                'completed': 0,
                'in_progress': 0,
                'not_started': 0,
                'overall_progress': 0,
                'can_update_info': True,
            })
        
        # ============================================================
        # LẤY DANH SÁCH BIỂU MẪU TỪ TARGET GROUP CỦA USER
        # ============================================================
        assigned_forms = []
        
        # Lấy các nhóm đối tượng mà user thuộc về
        target_groups = user.target_groups.filter(is_active=True)
        
        if target_groups.exists():
            # Duyệt từng nhóm và lấy danh sách biểu mẫu
            for group in target_groups:
                if group.forms:
                    assigned_forms.extend(group.forms)
            # Loại bỏ trùng lặp
            assigned_forms = list(set(assigned_forms))
        else:
            # FALLBACK: Nếu user chưa được gán nhóm, lấy tất cả forms từ tất cả nhóm
            all_groups = TargetGroup.objects.filter(is_active=True)
            for group in all_groups:
                if group.forms:
                    assigned_forms.extend(group.forms)
            assigned_forms = list(set(assigned_forms))
        
        # Tạo participant mới
        participant = SurveyParticipant.objects.create(
            survey=active_survey,
            user=user,
            full_name=user.get_full_name() or user.username,
            email=user.email or '',
            phone=user.phone_number or '',
            position=user.position or '',
            department=user.organization.name if user.organization else '',
            agency=user.organization.name if user.organization else '',
            assigned_forms=assigned_forms,
            status='draft',
            session_key=request.session.session_key or '',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    
    # Nếu vẫn chưa có participant, báo lỗi
    if not participant:
        return render(request, 'accounts/survey_dashboard.html', {
            'message': 'Không thể xác định thông tin khảo sát. Vui lòng liên hệ quản trị viên.',
            'participant': None,
            'progresses': [],
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'not_started': 0,
            'overall_progress': 0,
            'can_update_info': True,
        })
    
    # Lấy danh sách biểu mẫu được gán từ participant
    assigned_forms = participant.assigned_forms or []
    
    if not assigned_forms:
        return render(request, 'accounts/survey_dashboard.html', {
            'participant': participant,
            'message': 'Bạn chưa được gán biểu mẫu nào. Vui lòng liên hệ quản trị viên.',
            'progresses': [],
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'not_started': 0,
            'overall_progress': 0,
            'can_update_info': True,
        })
    
    # Lấy hoặc tạo progress cho từng biểu mẫu
    progress_list = []
    for form_code in assigned_forms:
        progress, created = SurveyProgress.objects.get_or_create(
            participant=participant,
            form_code=form_code,
            defaults={
                'status': 'not_started',
                'survey': Survey.objects.filter(code=form_code).first()
            }
        )
        
        # Nếu đã có survey, gán vào
        if not progress.survey:
            survey_obj = Survey.objects.filter(code=form_code, status='active').first()
            if survey_obj:
                progress.survey = survey_obj
                progress.save()
        
        # Cập nhật tiến độ từ response nếu có
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
                    # Nếu đã hoàn thành 100% và status chưa phải completed
                    if progress.progress_percent >= 100 and progress.status != 'completed':
                        progress.status = 'completed'
                        progress.completed_at = timezone.now()
                    progress.save()
        
        progress_list.append(progress)
    
    # Sắp xếp: Đang làm > Chưa làm > Hoàn thành
    status_order = {'in_progress': 0, 'not_started': 1, 'completed': 2}
    progress_list.sort(key=lambda p: status_order.get(p.status, 3))
    
    # Thống kê chung
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
    }
    
    return render(request, 'accounts/survey_dashboard.html', context)


# ============================================
# CẬP NHẬT THÔNG TIN USER
# ============================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_user_info(request):
    """
    API cập nhật thông tin cá nhân của user
    """
    try:
        data = json.loads(request.body)
        user = request.user
        
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            name_parts = full_name.split()
            user.first_name = name_parts[-1] if name_parts else ''
            user.last_name = ' '.join(name_parts[:-1]) if len(name_parts) > 1 else ''
        
        if 'email' in data:
            user.email = data['email'].strip()
        
        if 'phone' in data:
            user.phone_number = data['phone'].strip()
        
        if 'position' in data:
            user.position = data['position'].strip()
        
        if 'organization_id' in data and data['organization_id']:
            try:
                org = Organization.objects.get(id=data['organization_id'])
                user.organization = org
            except Organization.DoesNotExist:
                pass
        
        user.save()
        
        # Cập nhật participant nếu có
        participant = SurveyParticipant.objects.filter(
            user=user,
            status='draft'
        ).first()
        
        if participant:
            participant.full_name = user.get_full_name() or user.username
            participant.email = user.email or ''
            participant.phone = user.phone_number or ''
            participant.position = user.position or ''
            if user.organization:
                participant.department = user.organization.name
                participant.agency = user.organization.name
            participant.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cập nhật thông tin thành công!',
            'data': {
                'full_name': user.get_full_name() or user.username,
                'email': user.email,
                'phone': user.phone_number,
                'position': user.position,
                'organization': user.organization.name if user.organization else '',
                'organization_id': user.organization.id if user.organization else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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