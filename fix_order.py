import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.survey.models import Survey, Section, Question
for s in Survey.objects.all():
    for i, sec in enumerate(s.sections.order_by('id')):
        sec.order = i
        sec.save()
        for j, q in enumerate(sec.questions.order_by('id')):
            q.order = j
            q.save()
