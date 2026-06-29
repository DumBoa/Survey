# apps/analytics/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models
import json

# Import models từ survey
from apps.survey.models import Survey as SurveyModel, SurveyCategory as SurveyCategoryModel, Response as ResponseModel


def analytics_main_render(request):
    return render(request, 'analytics/analytics_main.html')


# ============================================
# QUẢN LÝ BIỂU MẪU KHẢO SÁT
# ============================================

@login_required(login_url='/accounts/login/')
def survey_list_render(request):
    """
    Render trang quản lý biểu mẫu khảo sát
    """
    return render(request, 'analytics/qly_bieumau.html')


@login_required(login_url='/accounts/login/')
def survey_list_api(request):
    """
    API lấy danh sách biểu mẫu khảo sát
    """
    try:
        surveys = SurveyModel.objects.all().order_by('-created_at')
        
        # Filter
        status_filter = request.GET.get('status')
        category_filter = request.GET.get('category')
        search = request.GET.get('search', '')
        
        if status_filter:
            surveys = surveys.filter(status=status_filter)
        if category_filter:
            surveys = surveys.filter(category__name=category_filter)
        if search:
            surveys = surveys.filter(
                models.Q(title__icontains=search) | 
                models.Q(slug__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 5))
        start = (page - 1) * per_page
        end = start + per_page
        
        total = surveys.count()
        survey_list = surveys[start:end]
        
        data = []
        for survey in survey_list:
            # Count responses
            response_count = survey.responses.filter(status='submitted').count()
            
            # Get question count
            question_count = 0
            for section in survey.sections.all():
                question_count += section.questions.count()
            
            # Get creator name
            creator_name = 'Hệ thống'
            if hasattr(survey, 'created_by') and survey.created_by:
                creator_name = survey.created_by.get_full_name() or survey.created_by.username
            
            data.append({
                'id': survey.id,
                'code': f'KS-{str(survey.id).zfill(3)}',
                'name': survey.title,
                'category': survey.category.name if survey.category else 'Chưa phân loại',
                'status': survey.get_status_display(),
                'status_code': survey.status,
                'creator': creator_name,
                'created': survey.created_at.strftime('%Y-%m-%d'),
                'updated': survey.updated_at.strftime('%Y-%m-%d'),
                'questions': question_count,
                'responses': response_count,
                'start_date': survey.start_date.strftime('%Y-%m-%d %H:%M') if survey.start_date else '',
                'end_date': survey.end_date.strftime('%Y-%m-%d %H:%M') if survey.end_date else '',
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
def survey_detail_api(request, survey_id):
    """
    API lấy chi tiết một biểu mẫu
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # Get sections and questions
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
                    'config': question.config,
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
        
        # Get response stats
        total_responses = survey.responses.count()
        submitted_responses = survey.responses.filter(status='submitted').count()
        draft_responses = survey.responses.filter(status='draft').count()
        
        # Get creator name
        creator_name = 'Hệ thống'
        if hasattr(survey, 'created_by') and survey.created_by:
            creator_name = survey.created_by.get_full_name() or survey.created_by.username
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': survey.id,
                'title': survey.title,
                'slug': survey.slug,
                'description': survey.description,
                'category': {
                    'id': survey.category.id if survey.category else None,
                    'name': survey.category.name if survey.category else None,
                } if survey.category else None,
                'status': survey.status,
                'status_display': survey.get_status_display(),
                'start_date': survey.start_date.isoformat() if survey.start_date else None,
                'end_date': survey.end_date.isoformat() if survey.end_date else None,
                'allow_after_deadline': survey.allow_after_deadline,
                'target_groups': survey.target_groups,
                'settings': survey.settings,
                'sections': sections_data,
                'stats': {
                    'total_responses': total_responses,
                    'submitted': submitted_responses,
                    'drafts': draft_responses,
                    'completion_rate': round(submitted_responses / total_responses * 100, 2) if total_responses > 0 else 0
                },
                'creator': creator_name,
                'created_at': survey.created_at.isoformat(),
                'updated_at': survey.updated_at.isoformat(),
            }
        })
        
    except SurveyModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy biểu mẫu'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@csrf_exempt
@require_http_methods(["POST"])
def survey_create_api(request):
    """
    API tạo biểu mẫu khảo sát mới
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        from django.utils.text import slugify
        base_slug = slugify(data.get('title', 'untitled'))
        slug = base_slug
        counter = 1
        while SurveyModel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Get category if provided
        category = None
        if data.get('category_id'):
            try:
                category = SurveyCategoryModel.objects.get(id=data['category_id'])
            except SurveyCategoryModel.DoesNotExist:
                pass
        
        # Parse dates
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
        
        survey = SurveyModel.objects.create(
            title=data.get('title', 'Biểu mẫu mới'),
            slug=slug,
            description=data.get('description', ''),
            category=category,
            start_date=start_date,
            end_date=end_date,
            status=data.get('status', 'draft'),
            target_groups=data.get('target_groups', []),
            settings=data.get('settings', {})
        )
        
        # Nếu có user đăng nhập, gán created_by (nếu model có field này)
        if hasattr(survey, 'created_by') and request.user.is_authenticated:
            survey.created_by = request.user
            survey.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Tạo biểu mẫu thành công!',
            'survey_id': survey.id,
            'data': {
                'id': survey.id,
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
def survey_update_api(request, survey_id):
    """
    API cập nhật biểu mẫu khảo sát
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        data = json.loads(request.body) if request.body else {}
        
        # Update fields
        updatable_fields = ['title', 'description', 'status', 'target_groups', 'settings', 'allow_after_deadline']
        for field in updatable_fields:
            if field in data:
                setattr(survey, field, data[field])
        
        # Update dates
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
        
        # Update category
        if 'category_id' in data:
            if data['category_id']:
                try:
                    survey.category = SurveyCategoryModel.objects.get(id=data['category_id'])
                except SurveyCategoryModel.DoesNotExist:
                    pass
            else:
                survey.category = None
        
        # Update slug if title changed
        if 'title' in data and data['title'] != survey.title:
            from django.utils.text import slugify
            base_slug = slugify(data['title'])
            slug = base_slug
            counter = 1
            while SurveyModel.objects.filter(slug=slug).exclude(id=survey.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            survey.slug = slug
        
        survey.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cập nhật biểu mẫu thành công!',
            'data': {
                'id': survey.id,
                'title': survey.title,
                'slug': survey.slug,
                'status': survey.status,
            }
        })
        
    except SurveyModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy biểu mẫu'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@csrf_exempt
@require_http_methods(["DELETE"])
def survey_delete_api(request, survey_id):
    """
    API xóa biểu mẫu khảo sát
    """
    try:
        survey = get_object_or_404(SurveyModel, id=survey_id)
        
        # Check if survey has responses
        if survey.responses.filter(status='submitted').exists():
            return JsonResponse({
                'success': False,
                'error': 'Không thể xóa biểu mẫu đã có phản hồi. Vui lòng lưu trữ thay vì xóa.'
            }, status=400)
        
        survey.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Xóa biểu mẫu thành công!'
        })
        
    except SurveyModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy biểu mẫu'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
@csrf_exempt
@require_http_methods(["POST"])
def survey_bulk_action_api(request):
    """
    API thực hiện hành động hàng loạt trên nhiều biểu mẫu
    """
    try:
        data = json.loads(request.body) if request.body else {}
        survey_ids = data.get('survey_ids', [])
        action = data.get('action')
        
        if not survey_ids:
            return JsonResponse({
                'success': False,
                'error': 'Không có biểu mẫu nào được chọn'
            }, status=400)
        
        if action not in ['archive', 'delete', 'publish', 'close']:
            return JsonResponse({
                'success': False,
                'error': 'Hành động không hợp lệ'
            }, status=400)
        
        surveys = SurveyModel.objects.filter(id__in=survey_ids)
        count = surveys.count()
        
        if action == 'archive':
            surveys.update(status='archived')
            message = f'Đã lưu trữ {count} biểu mẫu'
        elif action == 'publish':
            surveys.update(status='active')
            message = f'Đã phát hành {count} biểu mẫu'
        elif action == 'close':
            surveys.update(status='closed')
            message = f'Đã đóng {count} biểu mẫu'
        elif action == 'delete':
            # Only delete if no responses
            deletable = []
            for survey in surveys:
                if not survey.responses.filter(status='submitted').exists():
                    deletable.append(survey.id)
            
            if deletable:
                SurveyModel.objects.filter(id__in=deletable).delete()
                message = f'Đã xóa {len(deletable)} biểu mẫu'
            else:
                message = 'Không có biểu mẫu nào được xóa (đều có phản hồi)'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
def survey_categories_api(request):
    """
    API lấy danh sách danh mục khảo sát
    """
    try:
        categories = SurveyCategoryModel.objects.all().order_by('name')
        data = [{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'icon': cat.icon,
            'count': SurveyModel.objects.filter(category=cat).count()
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
def survey_stats_api(request):
    """
    API lấy thống kê tổng quan
    """
    try:
        total = SurveyModel.objects.count()
        active = SurveyModel.objects.filter(status='active').count()
        draft = SurveyModel.objects.filter(status='draft').count()
        closed = SurveyModel.objects.filter(status='closed').count()
        archived = SurveyModel.objects.filter(status='archived').count()
        
        # Total responses
        total_responses = ResponseModel.objects.filter(status='submitted').count()
        
        # Recent surveys
        recent = SurveyModel.objects.all().order_by('-created_at')[:5]
        recent_data = [{
            'id': s.id,
            'title': s.title,
            'status': s.get_status_display(),
            'created': s.created_at.strftime('%Y-%m-%d'),
        } for s in recent]
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': total,
                'active': active,
                'draft': draft,
                'closed': closed,
                'archived': archived,
                'total_responses': total_responses,
                'recent': recent_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)