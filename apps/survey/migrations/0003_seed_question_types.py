# apps/survey/migrations/0003_seed_question_types.py
# -*- coding: utf-8 -*-

from django.db import migrations


QUESTION_TYPES = [
    {
        "code": "title",
        "name": "Tiêu đề",
        "icon": "type",
        "has_options": False,
        "has_validation": False,
    },
    {
        "code": "paragraph",
        "name": "Đoạn văn",
        "icon": "align-left",
        "has_options": False,
        "has_validation": False,
    },
    {
        "code": "short-text",
        "name": "Văn bản ngắn",
        "icon": "minus",
        "has_options": False,
        "has_validation": True,
    },
    {
        "code": "long-text",
        "name": "Văn bản dài",
        "icon": "text",
        "has_options": False,
        "has_validation": True,
    },
    {
        "code": "single-choice",
        "name": "Một lựa chọn",
        "icon": "circle-dot",
        "has_options": True,
        "has_validation": False,
    },
    {
        "code": "multi-choice",
        "name": "Nhiều lựa chọn",
        "icon": "check-square",
        "has_options": True,
        "has_validation": False,
    },
    {
        "code": "rating-grid",
        "name": "Lưới đánh giá",
        "icon": "grid-3x3",
        "has_options": False,
        "has_validation": False,
    },
    {
        "code": "data-table",
        "name": "Bảng dữ liệu",
        "icon": "table",
        "has_options": False,
        "has_validation": False,
    },
    {
        "code": "personal-info",
        "name": "Thông tin cá nhân",
        "icon": "user",
        "has_options": False,
        "has_validation": True,
    },
    {
        "code": "section-break",
        "name": "Phần mới",
        "icon": "layout",
        "has_options": False,
        "has_validation": False,
    },
]


def seed_question_types(apps, schema_editor):
    QuestionType = apps.get_model("survey", "QuestionType")
    for item in QUESTION_TYPES:
        QuestionType.objects.get_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "icon": item["icon"],
                "has_options": item["has_options"],
                "has_validation": item["has_validation"],
            },
        )


def unseed_question_types(apps, schema_editor):
    QuestionType = apps.get_model("survey", "QuestionType")
    codes = [item["code"] for item in QUESTION_TYPES]
    QuestionType.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    # ✅ SỬA: dependencies phải là migration đã apply trước đó
    dependencies = [
        ("survey", "0002_section_remove_question_survey_and_more"),  # ✅ Đúng
    ]

    operations = [
        migrations.RunPython(seed_question_types, unseed_question_types),
    ]