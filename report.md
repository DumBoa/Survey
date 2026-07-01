# PROJECT FILE STRUCTURE

```
Survey/
│
├── manage.py                          # Django CLI entry point
├── db.sqlite3                         # SQLite database file
├── README.md
├── report.md                          # This file
│
├── config/                            # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   │
│   ├── accounts/                      # App: User accounts & authentication
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py
│   │   └── templates/
│   │       └── accounts/
│   │           ├── login.html
│   │           ├── congkhaosat_main.html
│   │           ├── congkhaosat_success.html
│   │           └── survey_dashboard.html
│   │
│   ├── analytics/                     # App: Analytics & reporting
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_targetgroup.py
│   │   └── templates/
│   │       └── analytics/
│   │           ├── assignments.html
│   │           ├── dashboard.html
│   │           ├── dashboard_base.html
│   │           ├── survey_forms.html
│   │           └── target_groups.html
│   │
│   └── survey/                        # App: Core survey builder
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py
│       ├── management/
│       │   └── commands/
│       │       └── seed_question_types.py
│       ├── migrations/
│       │   ├── __init__.py
│       │   ├── 0001_initial.py
│       │   ├── 0002_section_remove_question_survey_and_more.py
│       │   ├── 0003_seed_question_types.py
│       │   ├── 0004_question_component_type_and_more.py
│       │   ├── 0005_surveyassignment_surveyparticipant.py
│       │   ├── 0006_survey_code.py
│       │   ├── 0007_surveyprogress.py
│       │   └── 0008_alter_surveyprogress_survey.py
│       └── templates/
│           └── survey/
│               ├── survey_main.html       # MAIN SURVEY BUILDER UI (all JS here)
│               ├── survey_public.html     # Public survey view
│               └── survey-template.html
│
├── static/
│   ├── css/
│   │   ├── header-nav.css
│   │   └── phieunhap.css
│   ├── js/
│   │   └── header-nav.js
│   ├── images/
│   ├── libs/
│   └── media/
│
└── templates/
    ├── base.html
    ├── components/
    │   ├── header-nav.html
    │   └── header.html
    └── layouts/
```

## Key Files Description

| File | Description |
|------|-------------|
| `apps/survey/templates/survey/survey_main.html` | **Main survey builder interface** - contains all JavaScript logic for creating, editing, importing/exporting surveys, including drag & drop, rich text editing, Word import (mammoth.js), page management, and component rendering (3583 lines) |
| `apps/survey/templates/survey/survey_public.html` | Public-facing survey view for respondents |
| `apps/survey/models.py` | Backend data models (Survey, Section, Question, Response, etc.) |
| `apps/survey/serializers.py` | DRF serializers for the survey API |
| `apps/survey/views.py` | View logic (API endpoints) |
| `apps/survey/urls.py` | URL routing for survey app |
| `apps/analytics/` | Analytics module (dashboard, target groups, assignments) |
| `apps/accounts/` | User authentication and survey dashboard |
| `config/settings.py` | Django project settings |
| `config/urls.py` | Root URL configuration |