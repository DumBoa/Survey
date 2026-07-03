# apps/survey/management/commands/seed_question_types.py
from django.core.management.base import BaseCommand
from apps.survey.models import QuestionType


class Command(BaseCommand):
    help = 'Seed question types for survey'

    def handle(self, *args, **options):
        question_types = [
            {'name': 'Văn bản ngắn', 'code': 'short-text', 'icon': 'minus', 'has_options': False},
            {'name': 'Văn bản dài', 'code': 'long-text', 'icon': 'text', 'has_options': False},
            {'name': 'Một lựa chọn', 'code': 'single-choice', 'icon': 'circle-dot', 'has_options': True},
            {'name': 'Nhiều lựa chọn', 'code': 'multi-choice', 'icon': 'check-square', 'has_options': True},
            {'name': 'Lưới đánh giá', 'code': 'rating-grid', 'icon': 'grid-3x3', 'has_options': True},
            {'name': 'Bảng dữ liệu', 'code': 'data-table', 'icon': 'table', 'has_options': False},
            {'name': 'Thông tin cá nhân', 'code': 'personal-info', 'icon': 'user', 'has_options': False},
        ]

        for qt in question_types:
            obj, created = QuestionType.objects.get_or_create(
                code=qt['code'],
                defaults=qt
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {qt["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Exists: {qt["name"]}'))