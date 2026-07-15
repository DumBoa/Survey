import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from apps.survey.models import SurveyParticipant
    p = SurveyParticipant.objects.get(id=32)
    with open('p32_user.txt', 'w', encoding='utf-8') as f:
        f.write(f"Participant 32 User ID: {p.user_id}\n")
        if p.user:
            f.write(f"User Org ID: {p.user.organization_id}\n")
            f.write(f"User is_active: {p.user.is_active}\n")
            f.write(f"User org name: {p.user.organization.name if p.user.organization else 'None'}\n")
except Exception as e:
    with open('p32_user.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
