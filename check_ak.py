import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from apps.accounts.models import Organization, User
    from apps.survey.models import SurveyParticipant
    org = Organization.objects.get(name="An Khánh")
    users = User.objects.filter(organization=org)
    
    with open('ak_users.txt', 'w', encoding='utf-8') as f:
        f.write(f"Org An Khánh ID: {org.id}\n")
        for u in users:
            f.write(f"User {u.id}: {u.username}\n")
            parts = SurveyParticipant.objects.filter(user=u)
            for p in parts:
                f.write(f"  Participant {p.id}: {p.target_group_name} - Agency: {p.agency}\n")
except Exception as e:
    with open('ak_users.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
