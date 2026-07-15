import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from apps.survey.models import SurveyParticipant, SurveyProgress
    p = SurveyParticipant.objects.get(id=32)
    
    with open('p32_out.txt', 'w', encoding='utf-8') as f:
        f.write(f"Participant 32: {p.full_name}, Target Group: {p.target_group_name}\n")
        f.write(f"Assigned forms: {p.assigned_forms}\n")
        
        progresses = SurveyProgress.objects.filter(participant=p)
        for prog in progresses:
            f.write(f"Form: {prog.form_code}, Status: {prog.status}, Percent: {prog.progress_percent}\n")
            
except Exception as e:
    with open('p32_out.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
