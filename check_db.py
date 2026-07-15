import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from apps.analytics.models import TargetGroup
    groups = list(TargetGroup.objects.all().values_list('name', flat=True))
    with open('target_groups_out.txt', 'w', encoding='utf-8') as f:
        for g in groups:
            f.write(f"{g}\n")
    print("Done")
except Exception as e:
    print("Error:", e)
