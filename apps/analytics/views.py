# apps/analytics/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.core.paginator import Paginator
from django.db import models
import json

# Import models từ analytics
from .models import TargetGroup

# Import models từ survey
from apps.survey.models import Survey as SurveyModel, SurveyCategory as SurveyCategoryModel
from apps.survey.models import SurveyUnitStatus

# Import từ accounts để kiểm tra role
from apps.accounts.views import is_admin_user
from apps.accounts.models import User, Organization


# ============================================
# DECORATOR KIỂM TRA ADMIN
# ============================================

from functools import wraps

def admin_required(view_func):
    """Decorator yêu cầu user phải là admin/staff"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        if not is_admin_user(request.user):
            return redirect('/accounts/survey-dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================
# TRANG DASHBOARD
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def dashboard_home(request):
    """Trang dashboard tổng quan"""
    return render(request, 'analytics/dashboard.html', {'active_menu': 'dashboard'})


@login_required(login_url='/accounts/login/')
@admin_required
def target_groups_view(request):
    """Quản lý nhóm đối tượng"""
    return render(request, 'analytics/target_groups.html', {'active_menu': 'target_groups'})


@login_required(login_url='/accounts/login/')
@admin_required
def survey_forms_view(request):
    """Quản lý biểu mẫu"""
    return render(request, 'analytics/survey_forms.html', {'active_menu': 'survey_forms'})


@login_required(login_url='/accounts/login/')
@admin_required
def assignments_view(request):
    """Gán biểu mẫu cho nhóm"""
    return render(request, 'analytics/assignments.html', {'active_menu': 'assignments'})


@login_required(login_url='/accounts/login/')
@admin_required
def account_manage(request):
    context = {
        'active_menu': 'account_manage',
    }
    return render(request, 'analytics/account_manage.html', context)


@login_required(login_url='/accounts/login/')
@xframe_options_sameorigin
def tongquankhaosat_view(request):
    """Trang tổng hợp đơn vị khảo sát"""
    is_iframe = request.GET.get('iframe') == 'true'
    base_template = 'analytics/iframe_base.html' if is_iframe else 'analytics/dashboard_base.html'
    return render(request, 'analytics/tongquankhaosat.html', {
        'active_menu': 'survey_dashboard',
        'base_template': base_template
    })

@xframe_options_sameorigin
def public_survey_dashboard_view(request):
    """Trang tổng hợp tiến độ khảo sát Public (không cần đăng nhập)"""
    from django.conf import settings
    portal_login_url = '/accounts/sipas/' if getattr(settings, 'PROJECT_TYPE', '') == 'SIPAS' else '/accounts/cchc/'
    
    return render(request, 'analytics/public_survey_dashboard.html', {
        'portal_login_url': portal_login_url
    })


# ============================================
# API TARGET GROUPS
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def target_group_list_api(request):
    """
    API lấy danh sách nhóm đối tượng
    """
    try:
        queryset = TargetGroup.objects.all().order_by('-created_at')

        # Filter theo status
        status = request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        category_id = request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter theo search
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(code__icontains=search) |
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )

        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for group in page_obj:
            data.append({
                'id': group.id,
                'code': group.code,
                'name': group.name,
                'description': group.description,
                'icon': group.icon,
                'is_active': group.is_active,
                'category_id': group.category_id,
                'category_name': group.category.name if group.category else None,
                'forms': group.forms if group.forms else [],
                'form_count': len(group.forms) if group.forms else 0,
                'created_at': group.created_at.isoformat(),
                'updated_at': group.updated_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'data': data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def target_group_detail_api(request, group_id):
    """
    API lấy chi tiết một nhóm đối tượng
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)

        data = {
            'id': group.id,
            'code': group.code,
            'name': group.name,
            'description': group.description,
            'icon': group.icon,
            'is_active': group.is_active,
            'category_id': group.category_id,
            'category_name': group.category.name if group.category else None,
            'forms': group.forms if group.forms else [],
            'created_at': group.created_at.isoformat(),
            'updated_at': group.updated_at.isoformat(),
        }

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def target_group_create_api(request):
    """
    API tạo mới nhóm đối tượng
    """
    try:
        data = json.loads(request.body) if request.body else {}

        # Nếu có category_id thì không bắt buộc truyền mã nhóm, sẽ tự sinh. 
        # Cần kiểm tra logic này, nhưng tạm thời yêu cầu mã nhóm.
        if not data.get('code') and not data.get('category_id'):
            return JsonResponse({
                'success': False,
                'error': 'Mã nhóm hoặc danh mục là bắt buộc'
            }, status=400)

        if not data.get('name'):
            return JsonResponse({
                'success': False,
                'error': 'Tên nhóm là bắt buộc'
            }, status=400)

        if data.get('code') and TargetGroup.objects.filter(code=data['code']).exists():
            return JsonResponse({
                'success': False,
                'error': f'Mã nhóm "{data["code"]}" đã tồn tại'
            }, status=400)

        group = TargetGroup(
            code=data.get('code', '').strip().upper(),
            name=data['name'].strip(),
            description=data.get('description', ''),
            icon=data.get('icon', 'bi-people'),
            is_active=data.get('is_active', True),
            forms=data.get('forms', []),
            category_id=data.get('category_id')
        )
        group.save()

        return JsonResponse({
            'success': True,
            'message': 'Tạo nhóm thành công!',
            'data': {
                'id': group.id,
                'code': group.code,
                'name': group.name,
                'is_active': group.is_active,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def target_group_update_api(request, group_id):
    """
    API cập nhật nhóm đối tượng
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)
        data = json.loads(request.body) if request.body else {}

        if 'code' in data and data['code'] != group.code:
            if TargetGroup.objects.filter(code=data['code']).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Mã nhóm "{data["code"]}" đã tồn tại'
                }, status=400)
            group.code = data['code'].strip().upper()

        if 'name' in data:
            group.name = data['name'].strip()
        if 'description' in data:
            group.description = data['description']
        if 'icon' in data:
            group.icon = data['icon']
        if 'is_active' in data:
            group.is_active = data['is_active']
        if 'forms' in data:
            group.forms = data['forms']

        group.save()

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật nhóm thành công!',
            'data': {
                'id': group.id,
                'code': group.code,
                'name': group.name,
                'is_active': group.is_active,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def target_group_delete_api(request, group_id):
    """
    API xóa nhóm đối tượng
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)
        group.delete()

        return JsonResponse({
            'success': True,
            'message': 'Xóa nhóm thành công!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def target_group_options_api(request):
    """
    API lấy danh sách nhóm để dùng trong select
    """
    try:
        groups = TargetGroup.objects.filter(is_active=True).order_by('name')
        data = [{'id': g.id, 'code': g.code, 'name': g.name, 'category_id': g.category_id, 'category_name': g.category.name if g.category else None} for g in groups]

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
# API ASSIGNMENTS
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def assignment_list_api(request):
    """
    API lấy danh sách gán biểu mẫu cho nhóm
    """
    try:
        queryset = TargetGroup.objects.all().order_by('-created_at')

        group_id = request.GET.get('group')
        if group_id:
            queryset = queryset.filter(id=group_id)

        status = request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        form_code = request.GET.get('form')
        if form_code:
            queryset = queryset.filter(forms__contains=[form_code])

        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(code__icontains=search) |
                models.Q(name__icontains=search)
            )

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for group in page_obj:
            forms = group.forms if group.forms else []
            data.append({
                'group_id': group.id,
                'group_code': group.code,
                'group_name': group.name,
                'group_icon': group.icon,
                'forms': forms,
                'is_active': group.is_active,
                'form_count': len(forms),
            })

        return JsonResponse({
            'success': True,
            'data': data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def assignment_detail_api(request, group_id):
    """
    API lấy chi tiết gán của một nhóm
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)

        data = {
            'group_id': group.id,
            'group_code': group.code,
            'group_name': group.name,
            'group_icon': group.icon,
            'group_description': group.description,
            'forms': group.forms if group.forms else [],
            'is_active': group.is_active,
            'created_at': group.created_at.isoformat(),
            'updated_at': group.updated_at.isoformat(),
        }

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def assignment_create_api(request):
    """
    API tạo gán biểu mẫu mới cho nhóm
    """
    try:
        data = json.loads(request.body) if request.body else {}

        group_id = data.get('group_id')
        forms = data.get('forms', [])
        is_active = data.get('is_active', True)

        if not group_id:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng chọn nhóm đối tượng'
            }, status=400)

        if not forms:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng chọn ít nhất một biểu mẫu'
            }, status=400)

        group = get_object_or_404(TargetGroup, id=group_id)
        
        if forms and group.category_id:
            surveys = SurveyModel.objects.filter(code__in=forms)
            for survey in surveys:
                if survey.category_id != group.category_id:
                    return JsonResponse({
                        'success': False,
                        'error': f'Biểu mẫu "{survey.code}" không thuộc cùng danh mục với nhóm đối tượng.'
                    }, status=400)
                    
        group.forms = forms
        group.is_active = is_active
        group.save()

        return JsonResponse({
            'success': True,
            'message': 'Gán biểu mẫu thành công!',
            'data': {
                'group_id': group.id,
                'group_code': group.code,
                'group_name': group.name,
                'forms': group.forms,
                'is_active': group.is_active,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def assignment_update_api(request, group_id):
    """
    API cập nhật gán biểu mẫu cho nhóm
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)
        data = json.loads(request.body) if request.body else {}

        if 'forms' in data:
            forms = data['forms']
            if forms and group.category_id:
                surveys = SurveyModel.objects.filter(code__in=forms)
                for survey in surveys:
                    if survey.category_id != group.category_id:
                        return JsonResponse({
                            'success': False,
                            'error': f'Biểu mẫu "{survey.code}" không thuộc cùng danh mục với nhóm đối tượng.'
                        }, status=400)
            group.forms = forms
        if 'is_active' in data:
            group.is_active = data['is_active']

        group.save()

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật gán biểu mẫu thành công!',
            'data': {
                'group_id': group.id,
                'group_code': group.code,
                'group_name': group.name,
                'forms': group.forms,
                'is_active': group.is_active,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def assignment_delete_api(request, group_id):
    """
    API xóa gán biểu mẫu (xóa tất cả forms của nhóm)
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)

        group.forms = []
        group.save()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa tất cả biểu mẫu được gán cho nhóm "{group.name}"!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def assignment_remove_form_api(request, group_id):
    """
    API gỡ một biểu mẫu cụ thể khỏi nhóm
    """
    try:
        data = json.loads(request.body) if request.body else {}
        form_code = data.get('form_code')

        if not form_code:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng cung cấp mã biểu mẫu cần gỡ'
            }, status=400)

        group = get_object_or_404(TargetGroup, id=group_id)

        if group.forms and form_code in group.forms:
            group.forms = [f for f in group.forms if f != form_code]
            group.save()
            return JsonResponse({
                'success': True,
                'message': f'Đã gỡ biểu mẫu "{form_code}" khỏi nhóm "{group.name}"',
                'data': {
                    'group_id': group.id,
                    'group_name': group.name,
                    'forms': group.forms
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Biểu mẫu "{form_code}" không được gán cho nhóm này'
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# API QUẢN LÝ BIỂU MẪU (SURVEY FORMS)
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def survey_forms_list_api(request):
    """
    API lấy danh sách biểu mẫu (Survey) để quản lý
    """
    try:
        surveys = SurveyModel.objects.all().order_by('-created_at')

        status = request.GET.get('status')
        if status:
            surveys = surveys.filter(status=status)

        search = request.GET.get('search', '')
        if search:
            surveys = surveys.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(code__icontains=search)
            )

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(surveys, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for survey in page_obj:
            try:
                question_count = 0
                for section in survey.sections.all():
                    question_count += section.questions.count()

                form_code = survey.code if survey.code else f"BM-{str(survey.id).zfill(3)}"

                try:
                    assigned_groups = TargetGroup.objects.filter(forms__contains=[form_code])
                    group_names = [g.name for g in assigned_groups]
                except:
                    group_names = []

                data.append({
                    'id': survey.id,
                    'code': form_code,
                    'name': f"{survey.title} - {form_code}",
                    'title': survey.title,
                    'description': survey.description or '',
                    'section': survey.category.name if survey.category else '',
                    'category_id': survey.category_id,
                    'groups': group_names,
                    'status': survey.status,
                    'status_display': survey.get_status_display(),
                    'is_active': survey.status == 'active',
                    'question_count': question_count,
                    'section_count': survey.sections.count(),
                    'created_at': survey.created_at.isoformat() if survey.created_at else None,
                    'start_date': survey.start_date.isoformat() if survey.start_date else None,
                    'end_date': survey.end_date.isoformat() if survey.end_date else None,
                })
            except Exception as e:
                print(f"Error processing survey {survey.id}: {e}")
                continue

        return JsonResponse({
            'success': True,
            'data': data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def survey_form_detail_api(request, survey_id):
    """API lấy chi tiết một biểu mẫu (Survey)"""
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)

        form_code = survey.code if survey.code else f"BM-{str(survey.id).zfill(3)}"

        sections_data = []
        for section in survey.sections.all().order_by('order'):
            questions_data = []
            for question in section.questions.all().order_by('order'):
                questions_data.append({
                    'id': question.id,
                    'title': question.title,
                    'description': question.description,
                    'question_type': question.question_type.name if question.question_type else None,
                    'question_type_code': question.question_type.code if question.question_type else None,
                    'is_required': question.is_required,
                    'order': question.order,
                    'options': question.options,
                    'component_type': question.component_type,
                })

            sections_data.append({
                'id': section.id,
                'code': section.code,
                'title': section.title,
                'description': section.description,
                'icon': section.icon,
                'order': section.order,
                'questions': questions_data,
                'total_questions': len(questions_data)
            })

        return JsonResponse({
            'success': True,
            'data': {
                'id': survey.id,
                'code': form_code,
                'name': f"{survey.title} - {form_code}",
                'title': survey.title,
                'slug': survey.slug,
                'description': survey.description,
                'category': survey.category.name if survey.category else None,
                'category_id': survey.category.id if survey.category else None,
                'status': survey.status,
                'status_display': survey.get_status_display(),
                'start_date': survey.start_date.isoformat() if survey.start_date else None,
                'end_date': survey.end_date.isoformat() if survey.end_date else None,
                'allow_after_deadline': survey.allow_after_deadline,
                'target_groups': survey.target_groups,
                'settings': survey.settings,
                'sections': sections_data,
                'total_sections': len(sections_data),
                'total_questions': sum(s['total_questions'] for s in sections_data),
                'created_at': survey.created_at.isoformat(),
                'updated_at': survey.updated_at.isoformat(),
                'response_count': survey.responses.filter(status='submitted').count(),
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def survey_form_create_api(request):
    """
    API tạo biểu mẫu mới (Survey)
    """
    try:
        from django.utils.text import slugify
        from django.utils import timezone

        data = json.loads(request.body) if request.body else {}

        title = data.get('title', '').strip()
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng nhập tên biểu mẫu'
            }, status=400)

        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while SurveyModel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        category = None
        category_id = data.get('category_id')
        if category_id:
            try:
                category = SurveyCategoryModel.objects.get(id=category_id)
            except SurveyCategoryModel.DoesNotExist:
                pass

        start_date = data.get('start_date')
        if start_date:
            try:
                start_date = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                start_date = timezone.now()
        else:
            start_date = timezone.now()

        end_date = data.get('end_date')
        if end_date:
            try:
                end_date = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                end_date = timezone.now() + timezone.timedelta(days=30)
        else:
            end_date = timezone.now() + timezone.timedelta(days=30)

        code = data.get('code', '').strip()
        if code:
            if SurveyModel.objects.filter(code=code).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Mã biểu mẫu "{code}" đã tồn tại'
                }, status=400)

        survey = SurveyModel.objects.create(
            title=title,
            slug=slug,
            description=data.get('description', ''),
            category=category,
            start_date=start_date,
            end_date=end_date,
            status=data.get('status', 'draft'),
            target_groups=data.get('target_groups', []),
            settings=data.get('settings', {}),
            code=code if code else None,
            allow_after_deadline=data.get('allow_after_deadline', False),
        )

        return JsonResponse({
            'success': True,
            'message': 'Tạo biểu mẫu thành công!',
            'data': {
                'id': survey.id,
                'code': survey.code,
                'title': survey.title,
                'slug': survey.slug,
                'status': survey.status,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def survey_form_update_api(request, survey_id):
    """
    API cập nhật biểu mẫu (Survey)
    """
    try:
        from django.utils.text import slugify
        from django.utils import timezone

        survey = get_object_or_404(SurveyModel, id=survey_id)
        data = json.loads(request.body) if request.body else {}

        if 'code' in data and data['code']:
            code = data['code'].strip()
            if SurveyModel.objects.filter(code=code).exclude(id=survey.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Mã biểu mẫu "{code}" đã tồn tại'
                }, status=400)
            survey.code = code

        if 'title' in data and data['title']:
            survey.title = data['title'].strip()
            base_slug = slugify(data['title'])
            slug = base_slug
            counter = 1
            while SurveyModel.objects.filter(slug=slug).exclude(id=survey.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            survey.slug = slug

        if 'description' in data:
            survey.description = data['description']

        if 'status' in data:
            survey.status = data['status']

        if 'target_groups' in data:
            survey.target_groups = data['target_groups']

        if 'settings' in data:
            survey.settings = data['settings']

        if 'allow_after_deadline' in data:
            survey.allow_after_deadline = data['allow_after_deadline']

        if 'category_id' in data:
            if data['category_id']:
                try:
                    survey.category = SurveyCategoryModel.objects.get(id=data['category_id'])
                except SurveyCategoryModel.DoesNotExist:
                    pass
            else:
                survey.category = None

        if 'start_date' in data and data['start_date']:
            try:
                survey.start_date = timezone.datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except:
                pass

        if 'end_date' in data and data['end_date']:
            try:
                survey.end_date = timezone.datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except:
                pass

        survey.save()

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật biểu mẫu thành công!',
            'data': {
                'id': survey.id,
                'code': survey.code,
                'title': survey.title,
                'slug': survey.slug,
                'status': survey.status,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def survey_form_delete_api(request, survey_id):
    """
    API xóa biểu mẫu (Survey) - Chuyển sang archived nếu đã có response
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)

        has_responses = survey.responses.filter(status='submitted').exists()

        if has_responses:
            survey.status = 'archived'
            survey.save()
            return JsonResponse({
                'success': True,
                'message': 'Biểu mẫu đã có phản hồi nên được chuyển sang trạng thái lưu trữ thay vì xóa.',
                'action': 'archived',
                'survey_id': survey.id,
                'new_status': survey.status
            })
        else:
            survey.delete()
            return JsonResponse({
                'success': True,
                'message': 'Xóa biểu mẫu thành công!',
                'action': 'deleted',
                'survey_id': survey_id
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def survey_form_categories_api(request):
    """
    API lấy danh sách danh mục khảo sát
    """
    try:
        categories = SurveyCategoryModel.objects.all().order_by('name')
        data = [{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
        } for cat in categories]

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required(login_url='/accounts/login/')
@admin_required
def survey_form_next_code_api(request):
    """
    API lấy mã code dự kiến tiếp theo cho 1 category
    """
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'success': False, 'error': 'Missing category_id'})
        
    try:
        category = SurveyCategoryModel.objects.get(id=category_id)
        prefix = category.name.split()[0].upper()
        
        count = SurveyModel.objects.filter(category=category).count()
        next_count = count + 1
        new_code = f"{prefix}-BM-{next_count:02d}"
        
        while SurveyModel.objects.filter(code=new_code).exists():
            next_count += 1
            new_code = f"{prefix}-BM-{next_count:02d}"
            
        return JsonResponse({
            'success': True,
            'code': new_code,
            'prefix': prefix
        })
    except SurveyCategoryModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================
# API QUẢN LÝ TÀI KHOẢN (ACCOUNTS)
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def account_list_api(request):
    """
    API lấy danh sách tài khoản người dùng
    """
    try:
        queryset = User.objects.all().order_by('-date_joined')

        department = request.GET.get('department')
        if department:
            queryset = queryset.filter(organization__name__icontains=department)

        role = request.GET.get('role')
        if role == 'admin':
            queryset = queryset.filter(is_superuser=True)
        elif role == 'manager':
            queryset = queryset.filter(is_staff=True, is_superuser=False)
        elif role == 'staff':
            queryset = queryset.filter(is_staff=False, is_superuser=False, is_active=True)
        elif role == 'viewer':
            queryset = queryset.filter(is_staff=False, is_superuser=False)

        status = request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'pending':
            queryset = queryset.filter(is_active=False, last_login__isnull=True)

        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(phone_number__icontains=search)
            )

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        data = []
        for user in page_obj:
            full_name = f"{user.last_name} {user.first_name}".strip() or user.username

            if user.is_superuser:
                role_display = "Quản trị viên"
                role_code = "admin"
            elif user.is_staff:
                role_display = "Quản lý"
                role_code = "manager"
            else:
                role_display = "Nhân viên"
                role_code = "staff"

            if user.is_active:
                if user.last_login:
                    status_display = "Hoạt động"
                    status_class = "success"
                else:
                    status_display = "Chờ kích hoạt"
                    status_class = "warning"
            else:
                status_display = "Đã khóa"
                status_class = "danger"

            data.append({
                'id': user.id,
                'username': user.username,
                'full_name': full_name,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone_number or '',
                'organization': user.organization.name if user.organization else '',
                'organization_id': user.organization.id if user.organization else None,
                'position': user.position or '',
                'role': role_code,
                'role_display': role_display,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'status': status_display,
                'status_class': status_class,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'initials': ''.join([word[0].upper() for word in full_name.split() if word])[:2] or user.username[:2].upper(),
                'target_groups': [{'id': g.id, 'name': g.name} for g in user.target_groups.all()],
                'target_groups_display': ', '.join([g.name for g in user.target_groups.all()]),
            })

        return JsonResponse({
            'success': True,
            'data': data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def account_detail_api(request, user_id):
    """API lấy chi tiết một tài khoản"""
    try:
        user = get_object_or_404(User, id=user_id)

        full_name = f"{user.last_name} {user.first_name}".strip() or user.username

        if user.is_superuser:
            role_display = "Quản trị viên"
            role_code = "admin"
        elif user.is_staff:
            role_display = "Quản lý"
            role_code = "manager"
        else:
            role_display = "Nhân viên"
            role_code = "staff"

        if user.is_active:
            if user.last_login:
                status_display = "Hoạt động"
                status_class = "success"
            else:
                status_display = "Chờ kích hoạt"
                status_class = "warning"
        else:
            status_display = "Đã khóa"
            status_class = "danger"

        data = {
            'id': user.id,
            'username': user.username,
            'full_name': full_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone_number or '',
            'organization': user.organization.name if user.organization else '',
            'organization_id': user.organization.id if user.organization else None,
            'position': user.position or '',
            'role': role_code,
            'role_display': role_display,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'status': status_display,
            'status_class': status_class,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'initials': ''.join([word[0].upper() for word in full_name.split() if word])[:2] or user.username[:2].upper(),
            'target_groups': [{'id': g.id, 'name': g.name} for g in user.target_groups.all()],
        }

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def account_create_api(request):
    """API tạo mới tài khoản"""
    try:
        from django.contrib.auth.hashers import make_password
        from apps.analytics.models import TargetGroup

        data = json.loads(request.body) if request.body else {}

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        target_group_ids = data.get('target_groups', [])

        if not username:
            return JsonResponse({'success': False, 'error': 'Tên đăng nhập là bắt buộc'}, status=400)
        if not email:
            return JsonResponse({'success': False, 'error': 'Email là bắt buộc'}, status=400)
        if not password or len(password) < 8:
            return JsonResponse({'success': False, 'error': 'Mật khẩu phải có ít nhất 8 ký tự'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': f'Tên đăng nhập "{username}" đã tồn tại'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': f'Email "{email}" đã được sử dụng'}, status=400)

        name_parts = full_name.split()
        first_name = name_parts[-1] if name_parts else ''
        last_name = ' '.join(name_parts[:-1]) if len(name_parts) > 1 else ''

        organization = None
        organization_id = data.get('organization_id')
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                pass

        role = data.get('role', 'staff')
        is_staff = role in ['admin', 'manager']
        is_superuser = role == 'admin'

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            phone_number=data.get('phone', ''),
            organization=organization,
            position=data.get('position', ''),
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=data.get('is_active', True),
        )

        # Gán nhóm đối tượng cho user
        if target_group_ids:
            target_groups = TargetGroup.objects.filter(id__in=target_group_ids)
            user.target_groups.set(target_groups)

        return JsonResponse({
            'success': True,
            'message': 'Tạo tài khoản thành công!',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.last_name} {user.first_name}".strip(),
                'is_active': user.is_active,
                'target_groups': [{'id': g.id, 'name': g.name} for g in user.target_groups.all()],
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def account_update_api(request, user_id):
    """API cập nhật tài khoản"""
    try:
        from apps.analytics.models import TargetGroup

        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body) if request.body else {}

        # Cập nhật username
        if 'username' in data and data['username']:
            new_username = data['username'].strip()
            if new_username != user.username and User.objects.filter(username=new_username).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Tên đăng nhập "{new_username}" đã tồn tại'
                }, status=400)
            user.username = new_username

        # Cập nhật email
        if 'email' in data and data['email']:
            new_email = data['email'].strip()
            if new_email != user.email and User.objects.filter(email=new_email).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Email "{new_email}" đã được sử dụng'
                }, status=400)
            user.email = new_email

        # Cập nhật họ tên
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            name_parts = full_name.split()
            user.first_name = name_parts[-1] if name_parts else ''
            user.last_name = ' '.join(name_parts[:-1]) if len(name_parts) > 1 else ''

        # Cập nhật các field khác
        if 'phone' in data:
            user.phone_number = data['phone']
        if 'position' in data:
            user.position = data['position']
        if 'is_active' in data:
            user.is_active = data['is_active']

        # Cập nhật tổ chức
        if 'organization_id' in data:
            if data['organization_id']:
                try:
                    user.organization = Organization.objects.get(id=data['organization_id'])
                except Organization.DoesNotExist:
                    pass
            else:
                user.organization = None

        # Cập nhật role
        if 'role' in data:
            role = data['role']
            user.is_superuser = role == 'admin'
            user.is_staff = role in ['admin', 'manager']

        # Cập nhật mật khẩu
        if 'password' in data and data['password']:
            if len(data['password']) >= 8:
                from django.contrib.auth.hashers import make_password
                user.password = make_password(data['password'])

        # Cập nhật nhóm đối tượng
        if 'target_groups' in data:
            target_group_ids = data.get('target_groups', [])
            if target_group_ids:
                target_groups = TargetGroup.objects.filter(id__in=target_group_ids)
                user.target_groups.set(target_groups)
            else:
                user.target_groups.clear()

        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật tài khoản thành công!',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.last_name} {user.first_name}".strip(),
                'is_active': user.is_active,
                'target_groups': [{'id': g.id, 'name': g.name} for g in user.target_groups.all()],
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def account_delete_api(request, user_id):
    """API xóa tài khoản"""
    try:
        if request.user.id == user_id:
            return JsonResponse({'success': False, 'error': 'Bạn không thể xóa tài khoản của chính mình!'}, status=400)

        user = get_object_or_404(User, id=user_id)
        user.delete()

        return JsonResponse({'success': True, 'message': 'Xóa tài khoản thành công!'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def account_organizations_api(request):
    """API lấy danh sách tổ chức/đơn vị"""
    try:
        orgs = Organization.objects.filter(is_active=True).order_by('name')
        data = [{
            'id': org.id,
            'name': org.name,
            'code': org.code,
            'level': org.level,
            'level_display': org.get_level_display(),
        } for org in orgs]

        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def account_bulk_action_api(request):
    """API thao tác hàng loạt trên tài khoản"""
    try:
        data = json.loads(request.body) if request.body else {}
        user_ids = data.get('user_ids', [])
        action = data.get('action', '')

        if not user_ids:
            return JsonResponse({'success': False, 'error': 'Vui lòng chọn ít nhất một tài khoản'}, status=400)

        if request.user.id in user_ids:
            return JsonResponse({'success': False, 'error': 'Bạn không thể thực hiện thao tác trên tài khoản của chính mình!'}, status=400)

        users = User.objects.filter(id__in=user_ids)

        if action == 'activate':
            users.update(is_active=True)
            message = f'Đã kích hoạt {users.count()} tài khoản'
        elif action == 'deactivate':
            users.update(is_active=False)
            message = f'Đã khóa {users.count()} tài khoản'
        elif action == 'delete':
            users.delete()
            message = f'Đã xóa {users.count()} tài khoản'
        else:
            return JsonResponse({'success': False, 'error': 'Hành động không hợp lệ'}, status=400)

        return JsonResponse({'success': True, 'message': message})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# API DASHBOARD - TỔNG HỢP ĐƠN VỊ KHẢO SÁT
# ============================================

# apps/analytics/views.py - Sửa hàm survey_unit_dashboard_api

@login_required(login_url='/accounts/login/')
@admin_required
def survey_unit_dashboard_api(request, survey_id):
    """
    API lấy dữ liệu dashboard tổng hợp đơn vị khảo sát
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        from apps.survey.utils import update_survey_unit_status
        update_survey_unit_status(survey_id)
        
        # Lấy tất cả đơn vị cấp Sở (department)
        departments = Organization.objects.filter(
            level='department',
            is_active=True
        ).order_by('name')
        
        # Lấy tất cả đơn vị cấp Xã/Phường (ward)
        wards = Organization.objects.filter(
            level='ward',
            is_active=True
        ).order_by('name')
        
        # Lấy trạng thái của từng đơn vị trong khảo sát này
        all_statuses = SurveyUnitStatus.objects.filter(survey=survey)
        status_map = {s.organization_id: s for s in all_statuses}
        
        # Tổng số khảo sát đang active
        total_surveys = SurveyModel.objects.filter(status='active').count()
        
        # Dữ liệu bảng Sở
        dept_table = []
        for dept in departments:
            status = status_map.get(dept.id)
            
            # Số khảo sát đã hoàn thành của đơn vị này (tính trên tất cả survey active)
            unit_completed = SurveyUnitStatus.objects.filter(
                organization=dept,
                status='completed'
            ).count()
            
            dept_table.append({
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'status': status.status if status else 'pending',
                'status_display': dict(SurveyUnitStatus.STATUS_CHOICES).get(status.status if status else 'pending', 'Chưa hoàn thành'),
                'completed_at': status.completed_at.isoformat() if status and status.completed_at else None,
                'done': unit_completed,
                'total': total_surveys,
                'progress_display': f"{unit_completed}/{total_surveys}",
                'progress_percent': round((unit_completed / total_surveys * 100) if total_surveys > 0 else 0, 1),
            })
        
        # Dữ liệu bảng Xã/Phường
        ward_table = []
        for ward in wards:
            status = status_map.get(ward.id)
            
            unit_completed = SurveyUnitStatus.objects.filter(
                organization=ward,
                status='completed'
            ).count()
            
            ward_table.append({
                'id': ward.id,
                'name': ward.name,
                'code': ward.code,
                'status': status.status if status else 'pending',
                'status_display': dict(SurveyUnitStatus.STATUS_CHOICES).get(status.status if status else 'pending', 'Chưa hoàn thành'),
                'completed_at': status.completed_at.isoformat() if status and status.completed_at else None,
                'done': unit_completed,
                'total': total_surveys,
                'progress_display': f"{unit_completed}/{total_surveys}",
                'progress_percent': round((unit_completed / total_surveys * 100) if total_surveys > 0 else 0, 1),
            })
        
        # Thống kê cấp Sở
        dept_statuses = all_statuses.filter(organization__level='department')
        dept_completed = dept_statuses.filter(status='completed').count()
        dept_pending = dept_statuses.filter(status='pending').count()
        dept_in_progress = dept_statuses.filter(status='in_progress').count()
        dept_total = departments.count()
        
        # Thống kê cấp Xã/Phường
        ward_statuses = all_statuses.filter(organization__level='ward')
        ward_completed = ward_statuses.filter(status='completed').count()
        ward_pending = ward_statuses.filter(status='pending').count()
        ward_in_progress = ward_statuses.filter(status='in_progress').count()
        ward_total = wards.count()
        
        # Tổng hợp chung
        total_completed = dept_completed + ward_completed
        total_pending = dept_pending + ward_pending
        total_in_progress = dept_in_progress + ward_in_progress
        total_units = dept_total + ward_total
        
        return JsonResponse({
            'success': True,
            'data': {
                'survey': {
                    'id': survey.id,
                    'title': survey.title,
                    'code': survey.code,
                    'status': survey.status,
                },
                'summary': {
                    'total_units': total_units,
                    'completed': total_completed,
                    'pending': total_pending,
                    'in_progress': total_in_progress,
                    'completion_rate': round((total_completed / total_units * 100) if total_units > 0 else 0, 1),
                },
                'department': {
                    'total': dept_total,
                    'completed': dept_completed,
                    'pending': dept_pending,
                    'in_progress': dept_in_progress,
                    'list': dept_table,
                },
                'ward': {
                    'total': ward_total,
                    'completed': ward_completed,
                    'pending': ward_pending,
                    'in_progress': ward_in_progress,
                    'list': ward_table,
                }
            }
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

# ============================================
# TRANG QUẢN LÝ ĐƠN VỊ (ORGANIZATION)
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def organization_manage_view(request):
    """Trang quản lý đơn vị"""
    return render(request, 'analytics/organization_manage.html', {'active_menu': 'organization_manage'})


@login_required(login_url='/accounts/login/')
@admin_required
def organization_list_api(request):
    """
    API lấy danh sách đơn vị (Organization)
    """
    try:
        queryset = Organization.objects.all().order_by('name')

        # Filter theo cấp độ
        level = request.GET.get('level')
        if level and level != 'all':
            queryset = queryset.filter(level=level)

        # Filter theo trạng thái
        status = request.GET.get('status')
        if status and status != 'all':
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)

        # Tìm kiếm theo tên hoặc mã
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(code__icontains=search)
            )

        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        # Tạo map parent name
        parent_map = {org.id: org.name for org in Organization.objects.all()}

        data = []
        for org in page_obj:
            data.append({
                'id': org.id,
                'code': org.code,
                'name': org.name,
                'level': org.level,
                'level_display': org.get_level_display(),
                'parent': parent_map.get(org.parent_id) if org.parent_id else None,
                'parent_id': org.parent_id,
                'is_active': org.is_active,
                'created_at': org.created_at.isoformat() if hasattr(org, 'created_at') else None,
            })

        return JsonResponse({
            'success': True,
            'data': data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def organization_detail_api(request, org_id):
    """API lấy chi tiết một đơn vị"""
    try:
        org = get_object_or_404(Organization, id=org_id)

        data = {
            'id': org.id,
            'code': org.code,
            'name': org.name,
            'level': org.level,
            'level_display': org.get_level_display(),
            'parent_id': org.parent_id,
            'parent': org.parent.name if org.parent else None,
            'is_active': org.is_active,
        }

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def organization_create_api(request):
    """API tạo mới đơn vị"""
    try:
        data = json.loads(request.body) if request.body else {}

        code = data.get('code', '').strip()
        name = data.get('name', '').strip()
        level = data.get('level', '')
        parent_id = data.get('parent_id')
        is_active = data.get('is_active', True)

        if not code:
            return JsonResponse({'success': False, 'error': 'Mã đơn vị là bắt buộc'}, status=400)

        if not name:
            return JsonResponse({'success': False, 'error': 'Tên đơn vị là bắt buộc'}, status=400)

        if not level:
            return JsonResponse({'success': False, 'error': 'Cấp độ là bắt buộc'}, status=400)

        if Organization.objects.filter(code=code).exists():
            return JsonResponse({'success': False, 'error': f'Mã đơn vị "{code}" đã tồn tại'}, status=400)

        parent = None
        if parent_id:
            try:
                parent = Organization.objects.get(id=parent_id)
            except Organization.DoesNotExist:
                pass

        org = Organization.objects.create(
            code=code.upper(),
            name=name,
            level=level,
            parent=parent,
            is_active=is_active
        )

        return JsonResponse({
            'success': True,
            'message': 'Tạo đơn vị thành công!',
            'data': {
                'id': org.id,
                'code': org.code,
                'name': org.name,
                'level': org.level,
                'is_active': org.is_active,
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def organization_update_api(request, org_id):
    """API cập nhật đơn vị"""
    try:
        org = get_object_or_404(Organization, id=org_id)
        data = json.loads(request.body) if request.body else {}

        if 'code' in data and data['code']:
            new_code = data['code'].strip().upper()
            if new_code != org.code and Organization.objects.filter(code=new_code).exists():
                return JsonResponse({'success': False, 'error': f'Mã đơn vị "{new_code}" đã tồn tại'}, status=400)
            org.code = new_code

        if 'name' in data and data['name']:
            org.name = data['name'].strip()

        if 'level' in data and data['level']:
            org.level = data['level']

        if 'parent_id' in data:
            if data['parent_id']:
                try:
                    org.parent = Organization.objects.get(id=data['parent_id'])
                except Organization.DoesNotExist:
                    org.parent = None
            else:
                org.parent = None

        if 'is_active' in data:
            org.is_active = data['is_active']

        org.save()

        return JsonResponse({
            'success': True,
            'message': 'Cập nhật đơn vị thành công!',
            'data': {
                'id': org.id,
                'code': org.code,
                'name': org.name,
                'level': org.level,
                'is_active': org.is_active,
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def organization_delete_api(request, org_id):
    """API xóa đơn vị"""
    try:
        org = get_object_or_404(Organization, id=org_id)

        # Kiểm tra xem đơn vị có đơn vị con không
        if Organization.objects.filter(parent=org).exists():
            return JsonResponse({
                'success': False,
                'error': 'Không thể xóa đơn vị này vì còn đơn vị con!'
            }, status=400)

        # Kiểm tra xem đơn vị có user không
        if User.objects.filter(organization=org).exists():
            return JsonResponse({
                'success': False,
                'error': 'Không thể xóa đơn vị này vì còn người dùng thuộc đơn vị!'
            }, status=400)

        org.delete()

        return JsonResponse({
            'success': True,
            'message': 'Xóa đơn vị thành công!'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@admin_required
def organization_options_api(request):
    """API lấy danh sách đơn vị để dùng trong dropdown (chọn đơn vị cha)"""
    try:
        orgs = Organization.objects.filter(is_active=True).order_by('name')
        data = [{'id': org.id, 'code': org.code, 'name': org.name, 'level': org.level} for org in orgs]

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# API THỐNG KÊ ĐƠN VỊ (DASHBOARD CARDS)
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
def organization_stats_api(request):
    """
    API lấy thống kê nhanh cho dashboard cards
    GET /api/organizations/stats/
    """
    try:
        total = Organization.objects.count()
        active = Organization.objects.filter(is_active=True).count()
        inactive = Organization.objects.filter(is_active=False).count()
        
        # Đếm theo cấp độ
        level_counts = {}
        for level_code, level_label in Organization.LEVEL_CHOICES:
            count = Organization.objects.filter(level=level_code).count()
            if count > 0:
                level_counts[level_code] = {
                    'count': count,
                    'label': level_label
                }
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': total,
                'active': active,
                'inactive': inactive,
                'by_level': level_counts,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# API XÓA HÀNG LOẠT ĐƠN VỊ
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def organization_bulk_delete_api(request):
    """
    API xóa hàng loạt đơn vị
    POST /api/organizations/bulk-delete/
    Body: {"ids": [1, 2, 3]}
    """
    try:
        data = json.loads(request.body) if request.body else {}
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng chọn ít nhất một đơn vị'
            }, status=400)
        
        deleted_count = 0
        errors = []
        
        for org_id in ids:
            try:
                org = Organization.objects.get(id=org_id)
                
                # Kiểm tra đơn vị con
                if Organization.objects.filter(parent=org).exists():
                    errors.append(f'Đơn vị "{org.name}" còn đơn vị con')
                    continue
                
                # Kiểm tra user
                if User.objects.filter(organization=org).exists():
                    errors.append(f'Đơn vị "{org.name}" còn người dùng')
                    continue
                
                org.delete()
                deleted_count += 1
                
            except Organization.DoesNotExist:
                errors.append(f'Đơn vị ID {org_id} không tồn tại')
        
        message = f'Đã xóa {deleted_count} đơn vị'
        if errors:
            message += f'. Lỗi: {", ".join(errors[:3])}'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'deleted_count': deleted_count,
            'errors': errors
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# API TOGGLE TRẠNG THÁI ĐƠN VỊ
# ============================================

@login_required(login_url='/accounts/login/')
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def organization_toggle_status_api(request, org_id):
    """
    API bật/tắt trạng thái đơn vị
    POST /api/organizations/<id>/toggle-status/
    """
    try:
        org = get_object_or_404(Organization, id=org_id)
        org.is_active = not org.is_active
        org.save()
        
        status_text = 'Hoạt động' if org.is_active else 'Tạm dừng'
        
        return JsonResponse({
            'success': True,
            'message': f'Đã chuyển trạng thái đơn vị "{org.name}" sang "{status_text}"',
            'data': {
                'id': org.id,
                'is_active': org.is_active,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# API TỔNG HỢP KHẢO SÁT (SURVEY SUMMARY)
# ============================================

def organization_survey_summary_api(request):
    """
    API lấy tổng hợp tiến độ khảo sát theo đơn vị
    GET /api/organizations/survey-summary/
    Phân loại: department → Sở/Ngành, ward → Phường/Xã, còn lại → Khác
    Tiến độ = số người dùng đã hoàn thành / tổng số người dùng trong đơn vị
    """
    try:
        from apps.survey.models import SurveyProgress
        from apps.accounts.models import Organization, User
        from apps.analytics.models import TargetGroup
        
        # Lấy tất cả organization (kể cả không active, kể cả 0 user)
        all_orgs = Organization.objects.all().order_by('name')
        
        def process_org_list(orgs):
            org_list = []
            total_completed = 0
            total_in_progress = 0
            total_pending = 0
            total_objects = 0
            total_completed_objects = 0
            
            from apps.survey.models import SurveyParticipant, SurveyProgress
            
            for org in orgs:
                target_objects_count = 3
                total_objects += target_objects_count
                
                users = User.objects.filter(organization=org, is_active=True)
                
                if not users.exists():
                    org_list.append({
                        'id': org.id,
                        'name': org.name,
                        'code': org.code,
                        'level': org.level,
                        'total_users': target_objects_count,
                        'completed_users': 0,
                        'progress_percent': 0,
                        'status': 'pending',
                        'users': []
                    })
                    total_pending += 1
                    continue
                
                user_list = []
                completed_objects_count = 0
                
                participations = SurveyParticipant.objects.filter(user__in=users)
                
                for participant in participations:
                    assigned_forms = participant.assigned_forms or []
                    n_assigned = len(assigned_forms)
                    
                    if n_assigned > 0:
                        n_completed = SurveyProgress.objects.filter(
                            participant=participant,
                            form_code__in=assigned_forms,
                            status='completed'
                        ).count()
                        is_done = (n_completed == n_assigned)
                    else:
                        is_done = False
                        
                    if is_done:
                        completed_objects_count += 1
                    
                    last_progress = SurveyProgress.objects.filter(
                        participant=participant,
                        status='completed'
                    ).order_by('-completed_at').first()
                    
                    user_list.append({
                        'id': participant.id,
                        'full_name': participant.full_name or participant.email or f"Đối tượng {participant.id}",
                        'email': participant.email or '',
                        'completed': is_done,
                        'completed_at': last_progress.completed_at.isoformat() if (last_progress and last_progress.completed_at) else None
                    })
                
                pct = round((completed_objects_count / target_objects_count * 100), 1)
                if pct > 100:
                    pct = 100.0
                
                if pct >= 100:
                    status = 'completed'
                    total_completed += 1
                elif completed_objects_count > 0:
                    status = 'in_progress'
                    total_in_progress += 1
                else:
                    status = 'pending'
                    total_pending += 1
                
                total_completed_objects += completed_objects_count
                
                org_list.append({
                    'id': org.id,
                    'name': org.name,
                    'code': org.code,
                    'level': org.level,
                    'total_users': target_objects_count,
                    'completed_users': completed_objects_count,
                    'progress_percent': pct,
                    'status': status,
                    'users': user_list if request.user.is_authenticated else []
                })
            
            return org_list, total_completed, total_in_progress, total_pending, total_objects, total_completed_objects
        
        # Phân loại theo level
        dept_orgs = all_orgs.filter(level='department')
        ward_orgs = all_orgs.filter(level='ward')
        other_orgs = all_orgs.exclude(level__in=['department', 'ward'])
        
        dept_list, dept_c, dept_ip, dept_p, dept_u, dept_cu = process_org_list(dept_orgs)
        ward_list, ward_c, ward_ip, ward_p, ward_u, ward_cu = process_org_list(ward_orgs)
        other_list, other_c, other_ip, other_p, other_u, other_cu = process_org_list(other_orgs)
        
        # Tổng hợp
        total_orgs = len(dept_list) + len(ward_list) + len(other_list)
        total_completed = dept_c + ward_c + other_c
        total_in_progress = dept_ip + ward_ip + other_ip
        total_pending = dept_p + ward_p + other_p
        grand_users = dept_u + ward_u + other_u
        grand_completed = dept_cu + ward_cu + other_cu
        overall_rate = round((grand_completed / grand_users * 100), 1) if grand_users > 0 else 0
        
        return JsonResponse({
            'success': True,
            'data': {
                'summary': {
                    'total_orgs': total_orgs,
                    'total_users': grand_users,
                    'completed_orgs': total_completed,
                    'in_progress_orgs': total_in_progress,
                    'pending_orgs': total_pending,
                    'completed_users': grand_completed,
                    'completion_rate': overall_rate,
                },
                'department': {
                    'total': len(dept_list),
                    'completed': dept_c,
                    'in_progress': dept_ip,
                    'pending': dept_p,
                    'total_users': dept_u,
                    'completed_users': dept_cu,
                    'list': dept_list,
                },
                'ward': {
                    'total': len(ward_list),
                    'completed': ward_c,
                    'in_progress': ward_ip,
                    'pending': ward_p,
                    'total_users': ward_u,
                    'completed_users': ward_cu,
                    'list': ward_list,
                },
                'other': {
                    'total': len(other_list),
                    'completed': other_c,
                    'in_progress': other_ip,
                    'pending': other_p,
                    'total_users': other_u,
                    'completed_users': other_cu,
                    'list': other_list,
                }
            }
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# apps/analytics/views.py - Giữ lại hàm cũ cho tương thích ngược
@login_required(login_url='/accounts/login/')
@admin_required
def organization_with_status_api(request):
    """API cũ - giữ tương thích"""
    return organization_survey_summary_api(request)
