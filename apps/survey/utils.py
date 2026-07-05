# apps/survey/utils.py
from django.utils import timezone
from django.db.models import Count, Q
from apps.survey.models import Survey, SurveyUnitStatus, Response, SurveyProgress
from apps.accounts.models import Organization, User
from apps.analytics.models import TargetGroup


def update_survey_unit_status(survey_id):
    """
    Cập nhật trạng thái hoàn thành cho tất cả đơn vị trong một đợt khảo sát
    """
    try:
        survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return False
    
    # Lấy tất cả đơn vị có user thuộc nhóm đối tượng của khảo sát
    target_groups = TargetGroup.objects.filter(surveys=survey)
    target_group_ids = target_groups.values_list('id', flat=True)
    
    if not target_group_ids:
        # Nếu không có target group, tạo status cho tất cả organization có user
        users = User.objects.filter(is_active=True)
    else:
        users = User.objects.filter(target_groups__in=target_group_ids, is_active=True).distinct()
    
    # Nhóm user theo organization
    org_user_map = {}
    for user in users:
        if user.organization:
            if user.organization.id not in org_user_map:
                org_user_map[user.organization.id] = []
            org_user_map[user.organization.id].append(user.id)
    
    if not org_user_map:
        return False
    
    # Lấy tất cả organization đã có status
    existing_statuses = SurveyUnitStatus.objects.filter(survey=survey)
    existing_org_ids = set(existing_statuses.values_list('organization_id', flat=True))
    
    # Tạo status cho các organization mới
    for org_id in org_user_map.keys():
        if org_id not in existing_org_ids:
            SurveyUnitStatus.objects.create(
                survey=survey,
                organization_id=org_id,
                status='pending',
                total_assignees=len(org_user_map[org_id]),
                completed_count=0
            )
    
    # Cập nhật status cho từng organization
    for org_id, user_ids in org_user_map.items():
        # Đếm số user đã hoàn thành
        completed_count = Response.objects.filter(
            survey=survey,
            user_id__in=user_ids,
            status='submitted'
        ).count()
        
        total_assignees = len(user_ids)
        
        status_obj, created = SurveyUnitStatus.objects.get_or_create(
            survey=survey,
            organization_id=org_id,
            defaults={
                'total_assignees': total_assignees,
                'completed_count': completed_count,
                'status': 'completed' if completed_count >= total_assignees else 'pending'
            }
        )
        
        if not created:
            status_obj.total_assignees = total_assignees
            status_obj.completed_count = completed_count
        
        # Xác định trạng thái
        if completed_count >= total_assignees and total_assignees > 0:
            status_obj.status = 'completed'
            if not status_obj.completed_at:
                status_obj.completed_at = timezone.now()
        elif completed_count > 0:
            status_obj.status = 'in_progress'
        else:
            status_obj.status = 'pending'
        
        status_obj.save()
    
    return True


def update_all_surveys_status():
    """Cập nhật trạng thái cho tất cả khảo sát đang active"""
    surveys = Survey.objects.filter(status='active')
    for survey in surveys:
        update_survey_unit_status(survey.id)
    return True


def get_survey_unit_summary(survey_id):
    """Lấy tổng hợp trạng thái đơn vị cho một khảo sát"""
    try:
        survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return None
    
    update_survey_unit_status(survey_id)
    
    statuses = SurveyUnitStatus.objects.filter(survey=survey)
    
    total = statuses.count()
    completed = statuses.filter(status='completed').count()
    
    return {
        'survey_id': survey.id,
        'survey_title': survey.title,
        'total_units': total,
        'completed': completed,
        'in_progress': statuses.filter(status='in_progress').count(),
        'pending': statuses.filter(status='pending').count(),
        'completion_rate': round((completed / total * 100) if total > 0 else 0, 1),
    }
    return summary