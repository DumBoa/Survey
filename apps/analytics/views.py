# apps/analytics/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import models
import json

# Import models từ analytics
from .models import TargetGroup

# Import models từ survey
from apps.survey.models import Survey as SurveyModel, SurveyCategory as SurveyCategoryModel

# ============================================
# TRANG DASHBOARD
# ============================================

@login_required(login_url='/accounts/login/')
def dashboard_home(request):
    """Trang dashboard tổng quan"""
    return render(request, 'analytics/dashboard.html', {'active_menu': 'dashboard'})


@login_required(login_url='/accounts/login/')
def survey_list_view(request):
    """Danh sách đợt khảo sát"""
    return render(request, 'analytics/surveys.html', {'active_menu': 'surveys'})


@login_required(login_url='/accounts/login/')
def target_groups_view(request):
    """Quản lý nhóm đối tượng"""
    return render(request, 'analytics/target_groups.html', {'active_menu': 'target_groups'})


@login_required(login_url='/accounts/login/')
def survey_forms_view(request):
    """Quản lý biểu mẫu"""
    return render(request, 'analytics/survey_forms.html', {'active_menu': 'survey_forms'})


@login_required(login_url='/accounts/login/')
def assignments_view(request):
    """Gán biểu mẫu cho nhóm"""
    return render(request, 'analytics/assignments.html', {'active_menu': 'assignments'})

@login_required(login_url='/accounts/login/')
def account_manage(request):
    context = {
        'active_menu': 'account_manage',
    }
    return render(request, 'analytics/account_manage.html', context)
# ============================================
# API TARGET GROUPS
# ============================================

@login_required(login_url='/accounts/login/')
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
@csrf_exempt
@require_http_methods(["POST"])
def target_group_create_api(request):
    """
    API tạo mới nhóm đối tượng
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        if not data.get('code'):
            return JsonResponse({
                'success': False,
                'error': 'Mã nhóm là bắt buộc'
            }, status=400)
        
        if not data.get('name'):
            return JsonResponse({
                'success': False,
                'error': 'Tên nhóm là bắt buộc'
            }, status=400)
        
        if TargetGroup.objects.filter(code=data['code']).exists():
            return JsonResponse({
                'success': False,
                'error': f'Mã nhóm "{data["code"]}" đã tồn tại'
            }, status=400)
        
        group = TargetGroup.objects.create(
            code=data['code'].strip().upper(),
            name=data['name'].strip(),
            description=data.get('description', ''),
            icon=data.get('icon', 'bi-people'),
            is_active=data.get('is_active', True),
            forms=data.get('forms', [])
        )
        
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
def target_group_options_api(request):
    """
    API lấy danh sách nhóm để dùng trong select
    """
    try:
        groups = TargetGroup.objects.filter(is_active=True).order_by('name')
        data = [{'id': g.id, 'code': g.code, 'name': g.name} for g in groups]
        
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
def assignment_list_api(request):
    """
    API lấy danh sách gán biểu mẫu cho nhóm
    """
    try:
        print("="*60)
        print("ASSIGNMENT_LIST_API - START")
        print("="*60)
        
        # Kiểm tra user đã login chưa
        print(f"User: {request.user}")
        print(f"User authenticated: {request.user.is_authenticated}")
        
        # Lấy tất cả nhóm
        queryset = TargetGroup.objects.all().order_by('-created_at')
        print(f"Total groups in database: {queryset.count()}")
        
        # In chi tiết từng group
        for idx, group in enumerate(queryset, 1):
            print(f"  {idx}. ID: {group.id}, Code: {group.code}, Name: {group.name}, Forms: {group.forms}")
        
        # Lọc theo nhóm
        group_id = request.GET.get('group')
        if group_id:
            queryset = queryset.filter(id=group_id)
            print(f"Filtered by group_id: {group_id}")
        
        # Lọc theo trạng thái
        status = request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
            print("Filtered by status: active")
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            print("Filtered by status: inactive")
        
        # Lọc theo biểu mẫu
        form_code = request.GET.get('form')
        if form_code:
            # Lọc các nhóm có chứa form_code trong danh sách forms
            queryset = queryset.filter(forms__contains=[form_code])
            print(f"Filtered by form_code: {form_code}")
        
        # Tìm kiếm
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(code__icontains=search) |
                models.Q(name__icontains=search)
            )
            print(f"Search keyword: {search}")
        
        print(f"Final queryset count after all filters: {queryset.count()}")
        
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        print(f"Page: {page}, Per page: {per_page}")
        
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
        
        print(f"Data to return: {len(data)} items")
        print("="*60)
        
        return JsonResponse({
            'success': True,
            'data': data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERROR in assignment_list_api: {error_detail}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'detail': error_detail
        }, status=500)


@login_required(login_url='/accounts/login/')
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
            group.forms = data['forms']
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
@csrf_exempt
@require_http_methods(["DELETE"])
def assignment_delete_api(request, group_id):
    """
    API xóa gán biểu mẫu (xóa tất cả forms của nhóm)
    """
    try:
        group = get_object_or_404(TargetGroup, id=group_id)
        
        # Xóa tất cả forms được gán
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
        
        # Kiểm tra và gỡ form_code khỏi danh sách
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
    
@login_required(login_url='/accounts/login/')
def assignment_surveys_api(request):
    """
    API lấy danh sách survey để chọn trong dropdown
    """
    try:
        surveys = SurveyModel.objects.filter(
            status__in=['active', 'draft']
        ).order_by('-created_at')
        
        data = [{
            'id': s.id,
            'title': s.title,
            'status': s.status,
        } for s in surveys]
        
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
def assignment_forms_options_api(request):
    """
    API lấy danh sách biểu mẫu (survey) để chọn
    """
    try:
        surveys = SurveyModel.objects.filter(
            status__in=['active', 'draft']
        ).order_by('id')
        
        data = []
        for survey in surveys:
            # SỬA: DÙNG CODE TỪ DATABASE
            code = survey.code if survey.code else f"BM-{str(survey.id).zfill(3)}"
            data.append({
                'id': survey.id,
                'code': code,  # ĐÃ CÓ ĐỊNH DẠNG BM-XXX
                'name': f"{survey.title} - {code}",  # HIỂN THỊ TITLE + CODE
                'title': survey.title,
                'description': survey.description or '',
                'section': survey.category.name if survey.category else '',
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
# API QUẢN LÝ BIỂU MẪU (SURVEY FORMS)
# ============================================

@login_required(login_url='/accounts/login/')
def survey_forms_list_api(request):
    """
    API lấy danh sách biểu mẫu (Survey) để quản lý
    """
    try:
        surveys = SurveyModel.objects.all().order_by('-created_at')
        
        # Filter theo status
        status = request.GET.get('status')
        if status:
            surveys = surveys.filter(status=status)
        
        # Tìm kiếm
        search = request.GET.get('search', '')
        if search:
            surveys = surveys.filter(
                models.Q(title__icontains=search) |
                models.Q(slug__icontains=search) |
                models.Q(code__icontains=search)  # THÊM TÌM KIẾM THEO CODE
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        paginator = Paginator(surveys, per_page)
        page_obj = paginator.get_page(page)
        
        data = []
        for survey in page_obj:
            try:
                # Đếm số câu hỏi
                question_count = 0
                for section in survey.sections.all():
                    question_count += section.questions.count()
                
                # SỬA: DÙNG CODE TỪ DATABASE
                form_code = survey.code if survey.code else f"BM-{str(survey.id).zfill(3)}"
                
                # Tìm các nhóm đã gán biểu mẫu này
                try:
                    assigned_groups = TargetGroup.objects.filter(forms__contains=[form_code])
                    group_names = [g.name for g in assigned_groups]
                except:
                    group_names = []
                
                data.append({
                    'id': survey.id,
                    'code': form_code,  # ĐÃ CÓ ĐỊNH DẠNG BM-XXX
                    'name': f"{survey.title} - {form_code}",  # HIỂN THỊ TITLE + CODE
                    'title': survey.title,  # GIỮ TITLE RIÊNG
                    'description': survey.description or '',
                    'section': survey.category.name if survey.category else '',
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
        import traceback
        print(f"Error in survey_forms_list_api: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# API SURVEY FORMS - Chi tiết
# ============================================

@login_required(login_url='/accounts/login/')
def survey_form_detail_api(request, survey_id):
    """API lấy chi tiết một biểu mẫu (Survey)"""
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # SỬA: DÙNG CODE TỪ DATABASE
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
                'code': form_code,  # ĐÃ CÓ ĐỊNH DẠNG BM-XXX
                'name': f"{survey.title} - {form_code}",  # HIỂN THỊ TITLE + CODE
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
        
        # Tạo slug
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while SurveyModel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Xử lý category
        category = None
        category_id = data.get('category_id')
        if category_id:
            try:
                category = SurveyCategoryModel.objects.get(id=category_id)
            except SurveyCategoryModel.DoesNotExist:
                pass
        
        # Xử lý dates
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
        
        # THÊM XỬ LÝ CODE
        code = data.get('code', '').strip()
        if code:
            # Kiểm tra code đã tồn tại chưa
            if SurveyModel.objects.filter(code=code).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Mã biểu mẫu "{code}" đã tồn tại'
                }, status=400)
        # Nếu không có code, để model tự tạo
        
        # Tạo survey
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
            code=code if code else None,  # THÊM DÒNG NÀY
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
        
        # THÊM XỬ LÝ CODE
        if 'code' in data and data['code']:
            code = data['code'].strip()
            # Kiểm tra code đã tồn tại chưa (trừ chính nó)
            if SurveyModel.objects.filter(code=code).exclude(id=survey.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Mã biểu mẫu "{code}" đã tồn tại'
                }, status=400)
            survey.code = code
        
        # Cập nhật các field khác
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
@csrf_exempt
@require_http_methods(["DELETE"])
def survey_form_delete_api(request, survey_id):
    """
    API xóa biểu mẫu (Survey) - Chuyển sang archived nếu đã có response
    """
    try:
        from apps.survey.models import Survey as SurveyModel
        
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # Kiểm tra xem có response không
        has_responses = survey.responses.filter(status='submitted').exists()
        
        if has_responses:
            # Nếu đã có response, chuyển sang archived thay vì xóa
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
            # Nếu chưa có response, xóa hoàn toàn
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
# apps/analytics/views.py - Thêm vào cuối file

# ============================================
# API QUẢN LÝ TÀI KHOẢN (ACCOUNTS)
# ============================================

from apps.accounts.models import User, Organization

@login_required(login_url='/accounts/login/')
def account_list_api(request):
    """
    API lấy danh sách tài khoản người dùng
    """
    try:
        queryset = User.objects.all().order_by('-date_joined')
        
        # Filter theo đơn vị
        department = request.GET.get('department')
        if department:
            queryset = queryset.filter(organization__name__icontains=department)
        
        # Filter theo vai trò
        role = request.GET.get('role')
        if role == 'admin':
            queryset = queryset.filter(is_superuser=True)
        elif role == 'manager':
            queryset = queryset.filter(is_staff=True, is_superuser=False)
        elif role == 'staff':
            queryset = queryset.filter(is_staff=False, is_superuser=False, is_active=True)
        elif role == 'viewer':
            queryset = queryset.filter(is_staff=False, is_superuser=False)
        
        # Filter theo trạng thái
        status = request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'pending':
            queryset = queryset.filter(is_active=False, last_login__isnull=True)
        
        # Tìm kiếm
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(phone_number__icontains=search)
            )
        
        # Pagination
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
        import traceback
        print(f"Error in account_list_api: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
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
@csrf_exempt
@require_http_methods(["POST"])
def account_create_api(request):
    """API tạo mới tài khoản"""
    try:
        from django.contrib.auth.hashers import make_password
        
        data = json.loads(request.body) if request.body else {}
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
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
        
        return JsonResponse({
            'success': True,
            'message': 'Tạo tài khoản thành công!',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.last_name} {user.first_name}".strip(),
                'is_active': user.is_active,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def account_update_api(request, user_id):
    """API cập nhật tài khoản"""
    try:
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body) if request.body else {}
        
        if 'username' in data and data['username']:
            new_username = data['username'].strip()
            if new_username != user.username and User.objects.filter(username=new_username).exists():
                return JsonResponse({'success': False, 'error': f'Tên đăng nhập "{new_username}" đã tồn tại'}, status=400)
            user.username = new_username
        
        if 'email' in data and data['email']:
            new_email = data['email'].strip()
            if new_email != user.email and User.objects.filter(email=new_email).exists():
                return JsonResponse({'success': False, 'error': f'Email "{new_email}" đã được sử dụng'}, status=400)
            user.email = new_email
        
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            name_parts = full_name.split()
            user.first_name = name_parts[-1] if name_parts else ''
            user.last_name = ' '.join(name_parts[:-1]) if len(name_parts) > 1 else ''
        
        if 'phone' in data:
            user.phone_number = data['phone']
        if 'position' in data:
            user.position = data['position']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'organization_id' in data:
            if data['organization_id']:
                try:
                    user.organization = Organization.objects.get(id=data['organization_id'])
                except Organization.DoesNotExist:
                    pass
            else:
                user.organization = None
        
        if 'role' in data:
            role = data['role']
            user.is_superuser = role == 'admin'
            user.is_staff = role in ['admin', 'manager']
        
        if 'password' in data and data['password']:
            if len(data['password']) >= 8:
                from django.contrib.auth.hashers import make_password
                user.password = make_password(data['password'])
        
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
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='/accounts/login/')
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