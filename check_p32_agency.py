import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from apps.survey.models import SurveyParticipant
    p = SurveyParticipant.objects.get(id=32)
    with open('p32_agency.txt', 'w', encoding='utf-8') as f:
        f.write(f"Participant 32 agency: {p.agency}\n")
except Exception as e:
    with open('p32_agency.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
