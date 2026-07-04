# BÁO CÁO PHÂN TÍCH HỆ THỐNG SURVEY

---

## 1. CẤU TRÚC THƯ MỤC DỰ ÁN

```
Survey/
├── apps/
│   ├── accounts/          # Quản lý tài khoản, đơn vị, cổng khảo sát công chức (public)
│   │   ├── models.py      # Organization, User
│   │   ├── views.py       # Login, APIs public, cổng khảo sát 3 bước
│   │   ├── urls.py        # URLs của accounts
│   │   ├── admin.py, apps.py, tests.py
│   │   ├── migrations/
│   │   └── templates/accounts/
│   │       ├── congkhaosat_main.html    # Cổng khảo sát công chức (3 bước)
│   │       ├── login.html               # Trang đăng nhập
│   │       ├── survey_dashboard.html    # Dashboard của người dùng khảo sát
│   │       └── user_login.html          # Login form cũ
│   │
│   ├── analytics/         # Dashboard Admin, quản lý nhóm/biểu mẫu/tài khoản
│   │   ├── models.py      # ScoringConfig, AggregatedResult, ComparisonReport, TargetGroup
│   │   ├── views.py       # Dashboard views + REST API CRUD (target groups, assignments, survey-forms, accounts)
│   │   ├── urls.py        # URLs analytics (UI + API)
│   │   ├── serializers.py # TargetGroupSerializer, AssignmentSerializer, SurveySimpleSerializer
│   │   ├── admin.py, apps.py, tests.py
│   │   ├── migrations/
│   │   └── templates/analytics/
│   │       ├── dashboard_base.html     # Base layout cho dashboard Admin
│   │       ├── dashboard.html           # Trang tổng quan
│   │       ├── target_groups.html       # Quản lý nhóm đối tượng
│   │       ├── survey_forms.html        # Quản lý biểu mẫu
│   │       ├── assignments.html         # Gán biểu mẫu cho nhóm
│   │       └── account_manage.html      # Quản lý tài khoản
│   │
│   ├── survey/            # Quản lý khảo sát - sections - questions - responses
│   │   ├── models.py      # SurveyCategory, Survey, Section, QuestionType, Question, Blocklist,
│   │   │                  # Response, SurveyAssignment, SurveyParticipant, SurveyProgress
│   │   ├── views.py       # REST API (DRF class-based views) + Public survey views
│   │   ├── urls.py        # URLs survey (API + Public)
│   │   ├── serializers.py # SurveySerializer, SectionSerializer, QuestionSerializer, v.v.
│   │   ├── admin.py, apps.py, tests.py
│   │   ├── migrations/
│   │   └── templates/survey/
│   │       ├── survey_main.html        # Trang chỉnh sửa khảo sát (builder)
│   │       ├── survey_public.html      # Trang làm khảo sát (public)
│   │       └── survey-template.html    # Template mẫu
│   │
├── config/                # Cấu hình Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py        # Cấu hình chính
│   ├── urls.py            # URL root
│   └── wsgi.py
│
├── static/                # Static files
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/             # Base templates
│   ├── base.html
│   └── components/
│
├── manage.py
├── requirements.txt
├── db.sqlite3             # Database SQLite
└── README.md
```

---

## 2. FILE SETTINGS.PY

### INSTALLED_APPS
```python
INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.survey',      # App quản lý khảo sát
    'apps.analytics',   # App dashboard & báo cáo
    'apps.accounts',    # App quản lý tài khoản & cổng khảo sát
]
```

### AUTH_USER_MODEL
- **Không được khai báo tường minh** trong `settings.py`
- Tuy nhiên, model `apps.accounts.models.User` kế thừa từ `AbstractUser` và được sử dụng xuyên suốt project
- Trong các `ForeignKey` ở survey, analytics đều tham chiếu `'accounts.User'`

### Cấu hình Database (SQLite3)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

### MIDDLEWARE
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### TEMPLATES
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # templates/ gốc
        'APP_DIRS': True,                    # Tự tìm trong <app>/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### STATIC & MEDIA
```python
STATIC_URL = 'static/'
# (Không có cấu hình STATICFILES_DIRS và MEDIA trong file gốc)
```

---

## 3. CÁC MODEL TRONG TỪNG APP

### 3.1. apps/accounts/models.py

| Model | Fields | Ghi chú |
|-------|--------|---------|
| **Organization** | `name`, `code` (unique), `level` (city/department/district/ward/unit), `parent` (FK self), `is_active` | Tổ chức/Đơn vị hành chính |
| **User** (AbstractUser) | `phone_number`, `organization` (FK->Organization), `position`, `is_surveyor`, `last_active_at`, `groups` (M2M override), `user_permissions` (M2M override) | Model người dùng tùy chỉnh |

### 3.2. apps/analytics/models.py

| Model | Fields | Ghi chú |
|-------|--------|---------|
| **ScoringConfig** | `name`, `survey` (FK->survey.Survey), `criteria_mapping` (JSONField), `created_at`, `is_active` | Cấu hình chấm điểm |
| **AggregatedResult** | `survey` (FK->survey.Survey), `level`, `entity_name`, `entity_code`, `total_responses`, `average_score`, `raw_data` (JSONField), `calculated_at`, `year`, `quarter` | Kết quả tổng hợp theo cấp độ |
| **ComparisonReport** | `name`, `survey` (FK->survey.Survey), `comparison_type` (units/years/groups), `report_data` (JSONField), `generated_at`, `export_file` (FileField) | Báo cáo so sánh |
| **TargetGroup** | `code` (unique), `name`, `description`, `icon` (choice: bi-person-badge, bi-shield-check...), `is_active`, `surveys` (M2M->survey.Survey), `forms` (JSONField), `created_at`, `updated_at` | **Nhóm đối tượng** tham gia khảo sát |

### 3.3. apps/survey/models.py

| Model | Fields | Ghi chú |
|-------|--------|---------|
| **SurveyCategory** | `name` (unique), `description`, `icon`, `created_at` | Danh mục khảo sát |
| **Survey** | `title`, `slug` (unique), `description`, `category` (FK->SurveyCategory), `start_date`, `end_date`, `allow_after_deadline`, `status` (draft/active/closed/archived), `target_groups` (JSONField), `settings` (JSONField), `created_at`, `updated_at`, `code` (unique, auto BM-XXX) | **Đợt khảo sát** |
| **Section** | `survey` (FK->Survey), `code` (A,B,C...), `title`, `description`, `icon`, `order`, `created_at`, `updated_at` | **Phần** khảo sát |
| **QuestionType** | `name` (unique), `code` (unique), `icon`, `has_options`, `has_validation`, `created_at` | Loại câu hỏi (radio, checkbox, text, scale...) |
| **Question** | `section` (FK->Section), `component_type` (question/title/paragraph/section_break/personal_info), `title`, `description`, `question_type` (FK->QuestionType), `is_required`, `order`, `options` (JSONField), `condition_logic` (JSONField), `config` (JSONField) | **Câu hỏi** (có logic điều kiện) |
| **Blocklist** | `block_type` (ip/email/device/user), `value`, `reason`, `created_at`, `expires_at` | Danh sách đen chặn |
| **Response** | `survey` (FK->Survey), `respondent_ip`, `respondent_device_id`, `respondent_email`, `user_agent`, `started_at`, `submitted_at`, `time_taken`, `status` (draft/submitted), `answers` (JSONField), `section_progress` (JSONField), `is_verified`, `verification_token`, `is_cleaned`, `is_duplicate`, `user` (FK->accounts.User) | **Phiếu trả lời** |
| **SurveyAssignment** | `survey` (FK->Survey), `form_code`, `form_name`, `form_description`, `target_group_code`, `target_group_name`, `target_group_description`, `section` (FK->Section), `is_active`, `order` | **Phân công** nhóm ↔ biểu mẫu |
| **SurveyParticipant** | `survey` (FK->Survey), `agency`, `target_group_code`, `target_group_name`, `full_name`, `position`, `department`, `phone`, `email`, `notes`, `assigned_forms` (JSONField), `response` (OTO->Response), `user` (FK->accounts.User), `ip_address`, `user_agent`, `session_key`, `status` (draft/submitted/expired/cancelled) | **Người tham gia** khảo sát (thông tin từ cổng khảo sát 3 bước) |
| **SurveyProgress** | `participant` (FK->SurveyParticipant), `survey` (FK->Survey), `form_code`, `response` (OTO->Response), `status` (not_started/in_progress/completed/expired), `progress_percent`, `started_at`, `completed_at`, `last_accessed_at` | **Tiến độ** làm khảo sát cho từng biểu mẫu |

---

## 4. CÁC URL CHÍNH

### 4.1. core/urls.py (URL Root)
```python
urlpatterns = [
    path('', root_redirect),                    # → /analytics/ nếu đã login, /accounts/login/ nếu chưa
    path('admin/', admin.site.urls),
    path('survey/', include('apps.survey.urls')),     # prefix: /survey/
    path('accounts/', include('apps.accounts.urls')), # prefix: /accounts/
    path('analytics/', include('apps.analytics.urls')),# prefix: /analytics/
]
```

### 4.2. apps/accounts/urls.py (prefix: /accounts/)
| URL Pattern | View | Mô tả |
|-------------|------|-------|
| `/` | `accounts_main_render` | Trang chủ |
| `/login/` | `login_view` | Đăng nhập (GET form, POST JSON) |
| `/congkhaosat/` | `congkhaosat_view` | Cổng khảo sát công chức (3 bước) |
| `/api/congkhaosat/init/` | `congkhaosat_init` | API khởi tạo phiếu khảo sát |
| `/api/congkhaosat/submit/` | `congkhaosat_submit` | API submit thông tin + khảo sát |
| `/api/organizations/` | `get_organizations_api` | API lấy danh sách đơn vị |
| `/api/target-groups/` | `get_target_groups_api` | API lấy nhóm đối tượng (public) |
| `/api/survey-forms/` | `get_survey_forms_api` | API lấy biểu mẫu (public) |
| `/survey-dashboard/` | `survey_dashboard` | Dashboard người dùng khảo sát |
| `/survey-dashboard/continue/<int:progress_id>/` | `survey_dashboard_continue` | Tiếp tục làm khảo sát |

### 4.3. apps/analytics/urls.py (prefix: /analytics/)
| URL Pattern | View | Mô tả |
|-------------|------|-------|
| `/` | `dashboard_home` | Dashboard tổng quan |
| `/surveys/` | `survey_list_view` | Danh sách đợt khảo sát (UI) |
| `/target-groups/` | `target_groups_view` | Quản lý nhóm đối tượng (UI) |
| `/survey-forms/` | `survey_forms_view` | Quản lý biểu mẫu (UI) |
| `/assignments/` | `assignments_view` | Gán biểu mẫu cho nhóm (UI) |
| `/account-manage/` | `account_manage` | Quản lý tài khoản (UI) |
| **API Target Groups** | | |
| `/api/target-groups/` | `target_group_list_api` | Danh sách nhóm (GET) |
| `/api/target-groups/<int:group_id>/` | `target_group_detail_api` | Chi tiết nhóm (GET) |
| `/api/target-groups/create/` | `target_group_create_api` | Tạo nhóm (POST) |
| `/api/target-groups/<int:group_id>/update/` | `target_group_update_api` | Cập nhật nhóm (PUT/PATCH) |
| `/api/target-groups/<int:group_id>/delete/` | `target_group_delete_api` | Xóa nhóm (DELETE) |
| `/api/target-groups/options/` | `target_group_options_api` | Options cho select (GET) |
| **API Assignments** | | |
| `/api/assignments/` | `assignment_list_api` | Danh sách gán (GET) |
| `/api/assignments/<int:group_id>/` | `assignment_detail_api` | Chi tiết gán (GET) |
| `/api/assignments/create/` | `assignment_create_api` | Tạo gán (POST) |
| `/api/assignments/<int:group_id>/update/` | `assignment_update_api` | Cập nhật gán (PUT/PATCH) |
| `/api/assignments/<int:group_id>/delete/` | `assignment_delete_api` | Xóa gán (DELETE) |
| `/api/assignments/<int:group_id>/remove-form/` | `assignment_remove_form_api` | Gỡ 1 biểu mẫu (POST) |
| `/api/assignments/surveys/` | `assignment_surveys_api` | Danh sách survey (GET) |
| **API Survey Forms** | | |
| `/api/survey-forms/` | `survey_forms_list_api` | Danh sách biểu mẫu (GET) |
| `/api/survey-forms/<int:survey_id>/` | `survey_form_detail_api` | Chi tiết biểu mẫu (GET) |
| `/api/survey-forms/create/` | `survey_form_create_api` | Tạo biểu mẫu (POST) |
| `/api/survey-forms/<int:survey_id>/update/` | `survey_form_update_api` | Cập nhật (PUT/PATCH) |
| `/api/survey-forms/<int:survey_id>/delete/` | `survey_form_delete_api` | Xóa (DELETE) |
| `/api/survey-forms/categories/` | `survey_form_categories_api` | Danh mục (GET) |
| **API Accounts** | | |
| `/api/accounts/` | `account_list_api` | Danh sách tài khoản (GET) |
| `/api/accounts/<int:user_id>/` | `account_detail_api` | Chi tiết (GET) |
| `/api/accounts/create/` | `account_create_api` | Tạo (POST) |
| `/api/accounts/<int:user_id>/update/` | `account_update_api` | Cập nhật (PUT/PATCH) |
| `/api/accounts/<int:user_id>/delete/` | `account_delete_api` | Xóa (DELETE) |
| `/api/accounts/organizations/` | `account_organizations_api` | Tổ chức (GET) |
| `/api/accounts/bulk-action/` | `account_bulk_action_api` | Thao tác hàng loạt (POST) |

### 4.4. apps/survey/urls.py (prefix: /survey/)
| URL Pattern | View | Mô tả |
|-------------|------|-------|
| `/survey-edit/` | `survey_edit_render` | Trang builder khảo sát |
| **API CRUD Surveys** | | |
| `/api/surveys/` | `SurveyListCreateView` | GET/POST |
| `/api/surveys/<int:pk>/` | `SurveyDetailView` | GET/PUT/DELETE |
| `/api/surveys/<int:survey_id>/sections/` | `SectionListCreateView` | GET/POST |
| `/api/sections/<int:pk>/` | `SectionDetailView` | GET/PUT/DELETE |
| `/api/sections/<int:section_id>/questions/` | `QuestionListCreateView` | GET/POST |
| `/api/questions/<int:pk>/` | `QuestionDetailView` | GET/PUT/DELETE |
| `/api/surveys/<int:survey_id>/duplicate/` | `duplicate_survey` | Nhân bản |
| `/api/surveys/<int:survey_id>/export/` | `export_survey` | Xuất JSON |
| `/api/surveys/<int:survey_id>/publish/` | `publish_survey` | Phát hành |
| `/api/responses/` | `ResponseCreateView` | Tạo/cập nhật response |
| `/api/responses/<int:pk>/` | `ResponseDetailView` | Chi tiết response |
| `/api/responses/<int:survey_id>/stats/` | `SurveyStatsView` | Thống kê |
| `/api/categories/` | `CategoryListView` | Danh mục |
| `/api/question-types/` | `QuestionTypeListView` | Loại câu hỏi |
| **PUBLIC** | | |
| `/public/<int:survey_id>/` | `survey_public_view` | Làm khảo sát |
| `/public/<int:survey_id>/embed/` | `survey_public_embed` | Embed mode |
| `/public/<int:survey_id>/preview/` | `survey_public_preview` | Xem trước |
| `/public/<int:survey_id>/survey2/` | `survey2_view` | Giao diện survey 2 |
| **PUBLIC API** | | |
| `/api/public/surveys/<int:survey_id>/` | `SurveyPublicDetailView` | GET (ko cần auth) |
| `/api/public/surveys/<int:survey_id>/response/` | `PublicResponseView` | GET/POST |
| `/api/public/responses/submit/` | `survey_submit_response` | Submit response |
| `/api/public/surveys/<int:survey_id>/mapping/` | `get_survey_mapping` | Mapping nhóm ↔ biểu mẫu |
| `/api/public/surveys/<int:survey_id>/target-groups/` | `get_target_groups` | Nhóm đối tượng |

---

## 5. VIEWS CHÍNH CỦA TỪNG APP

### 5.1. apps/accounts/views.py (673 dòng)
- **`login_view`** - GET/POST: Form login → authenticate → session
- **`get_organizations_api`** - API lấy danh sách đơn vị (có filter `is_active=True`)
- **`get_target_groups_api`** - API lấy nhóm đối tượng (public)
- **`get_survey_forms_api`** - API lấy biểu mẫu + đếm câu hỏi
- **`congkhaosat_view`** - Cổng khảo sát 3 bước (Xác minh → Cá nhân → Xác nhận)
- **`congkhaosat_init`** - Khởi tạo phiếu khảo sát, trả về sections + questions
- **`congkhaosat_submit`** - Lưu thông tin participant + response, redirect survey-dashboard
- **`survey_dashboard`** - Dashboard người dùng: danh sách biểu mẫu được gán + tiến độ
- **`survey_dashboard_continue`** - Tiếp tục/sửa bài khảo sát

### 5.2. apps/analytics/views.py (1483 dòng)
- **UI Views (render templates):** `dashboard_home`, `survey_list_view`, `target_groups_view`, `survey_forms_view`, `assignments_view`, `account_manage`
- **API Target Groups:** CRUD + options
- **API Assignments:** CRUD + remove-form + surveys/forms options
- **API Survey Forms:** CRUD + categories
- **API Accounts:** CRUD + organizations + bulk-action

### 5.3. apps/survey/views.py (969 dòng)
- **`survey_edit_render`** - Trang builder khảo sát
- **`duplicate_survey`** - Nhân bản survey + sections + questions
- **`export_survey`** - Xuất survey JSON
- **`publish_survey`** - Phát hành survey (draft → active)
- **`SurveyListCreateView`** - API Survey CRUD (DRF)
- **`SurveyDetailView`** - API Survey detail
- **`SectionListCreateView`** - API Section CRUD
- **`SectionDetailView`** - API Section detail
- **`QuestionListCreateView`** - API Question CRUD
- **`QuestionDetailView`** - API Question detail
- **`ResponseCreateView`** - API Response create/update
- **`ResponseDetailView`** - API Response detail
- **`SurveyStatsView`** - API thống kê (total, submitted, drafts, section stats)
- **`CategoryListView`** - API danh mục
- **`QuestionTypeListView`** - API loại câu hỏi
- **`survey_public_view`** - Trang public làm khảo sát
- **`survey_submit_response`** - API submit response (có cập nhật SurveyProgress)
- **`survey_public_embed`** - Embed mode
- **`survey_public_preview`** - Preview mode
- **`survey2_view`** - Giao diện survey 2
- **`SurveyPublicDetailView`** - API public survey detail
- **`PublicResponseView`** - API public response (GET/POST)
- **`get_survey_mapping`** - API mapping nhóm ↔ biểu mẫu
- **`get_target_groups`** - API nhóm đối tượng (từ mapping)

---

## 6. TEMPLATES

### 6.1. apps/accounts/templates/accounts/ (4 files)
| File | Mô tả |
|------|-------|
| `congkhaosat_main.html` | Cổng khảo sát công chức (giao diện 3 bước chính) |
| `login.html` | Trang đăng nhập (AJAX) |
| `survey_dashboard.html` | Dashboard người dùng khảo sát, danh sách biểu mẫu được gán |
| `user_login.html` | Login form cũ |

### 6.2. apps/analytics/templates/analytics/ (6 files)
| File | Mô tả |
|------|-------|
| `dashboard_base.html` | Base layout dashboard Admin (sidebar, navbar) |
| `dashboard.html` | Trang tổng quan (thống kê) |
| `target_groups.html` | Quản lý nhóm đối tượng (CRUD) |
| `survey_forms.html` | Quản lý biểu mẫu (CRUD) |
| `assignments.html` | Gán biểu mẫu cho nhóm |
| `account_manage.html` | Quản lý tài khoản người dùng |

### 6.3. apps/survey/templates/survey/ (3 files)
| File | Mô tả |
|------|-------|
| `survey_main.html` | Trang builder khảo sát (tạo/sửa survey, sections, questions) |
| `survey_public.html` | Trang làm khảo sát (public - người dùng) |
| `survey-template.html` | Template mẫu |

---

## 7. CÁC API ENDPOINT ĐANG DÙNG

### 7.1. Public APIs (không cần đăng nhập)
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/accounts/api/organizations/` | GET | Lấy danh sách đơn vị (dropdown) |
| `/accounts/api/target-groups/` | GET | Lấy nhóm đối tượng (public) |
| `/accounts/api/survey-forms/` | GET | Lấy biểu mẫu + đếm câu hỏi |
| `/accounts/api/congkhaosat/init/` | POST | Khởi tạo phiếu khảo sát (trả về sections+questions) |
| `/accounts/api/congkhaosat/submit/` | POST | Submit thông tin + chuyển sang làm khảo sát |
| `/survey/api/public/surveys/<id>/` | GET | Chi tiết survey public |
| `/survey/api/public/surveys/<id>/response/` | GET/POST | Lấy/tạo response |
| `/survey/api/public/responses/submit/` | POST | Submit câu trả lời |
| `/survey/api/public/surveys/<id>/mapping/` | GET | Mapping nhóm ↔ biểu mẫu |
| `/survey/api/public/surveys/<id>/target-groups/` | GET | Nhóm đối tượng (từ mapping) |

### 7.2. Protected APIs (cần đăng nhập)

**Analytics:**
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/analytics/api/target-groups/` | GET | Danh sách nhóm (phân trang, tìm kiếm) |
| `/analytics/api/target-groups/<id>/` | GET | Chi tiết nhóm |
| `/analytics/api/target-groups/create/` | POST | Tạo nhóm |
| `/analytics/api/target-groups/<id>/update/` | PUT/PATCH | Cập nhật nhóm |
| `/analytics/api/target-groups/<id>/delete/` | DELETE | Xóa nhóm |
| `/analytics/api/target-groups/options/` | GET | Options cho select |
| `/analytics/api/assignments/` | GET | Danh sách gán (phân trang) |
| `/analytics/api/assignments/<id>/` | GET | Chi tiết gán |
| `/analytics/api/assignments/create/` | POST | Tạo gán |
| `/analytics/api/assignments/<id>/update/` | PUT/PATCH | Sửa gán |
| `/analytics/api/assignments/<id>/delete/` | DELETE | Xóa gán |
| `/analytics/api/assignments/<id>/remove-form/` | POST | Gỡ 1 biểu mẫu |
| `/analytics/api/assignments/surveys/` | GET | Danh sách survey |
| `/analytics/api/survey-forms/` | GET | Danh sách biểu mẫu |
| `/analytics/api/survey-forms/<id>/` | GET | Chi tiết biểu mẫu |
| `/analytics/api/survey-forms/create/` | POST | Tạo biểu mẫu |
| `/analytics/api/survey-forms/<id>/update/` | PUT/PATCH | Sửa biểu mẫu |
| `/analytics/api/survey-forms/<id>/delete/` | DELETE | Xóa biểu mẫu |
| `/analytics/api/survey-forms/categories/` | GET | Danh mục |
| `/analytics/api/accounts/` | GET | Danh sách tài khoản |
| `/analytics/api/accounts/<id>/` | GET | Chi tiết tài khoản |
| `/analytics/api/accounts/create/` | POST | Tạo tài khoản |
| `/analytics/api/accounts/<id>/update/` | PUT/PATCH | Cập nhật tài khoản |
| `/analytics/api/accounts/<id>/delete/` | DELETE | Xóa tài khoản |
| `/analytics/api/accounts/organizations/` | GET | Tổ chức |
| `/analytics/api/accounts/bulk-action/` | POST | Thao tác hàng loạt |

**Survey (builder):**
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/survey/api/surveys/` | GET/POST | Danh sách/tạo survey |
| `/survey/api/surveys/<id>/` | GET/PUT/DELETE | Chi tiết/sửa/xóa survey |
| `/survey/api/surveys/<id>/sections/` | GET/POST | Sections của survey |
| `/survey/api/sections/<id>/` | GET/PUT/DELETE | Chi tiết section |
| `/survey/api/sections/<id>/questions/` | GET/POST | Questions của section |
| `/survey/api/questions/<id>/` | GET/PUT/DELETE | Chi tiết question |
| `/survey/api/surveys/<id>/duplicate/` | POST | Nhân bản survey |
| `/survey/api/surveys/<id>/export/` | GET | Xuất JSON |
| `/survey/api/surveys/<id>/publish/` | POST | Phát hành |
| `/survey/api/responses/` | POST | Tạo/cập nhật response |
| `/survey/api/responses/<id>/` | GET | Chi tiết response |
| `/survey/api/responses/<id>/stats/` | GET | Thống kê response |
| `/survey/api/categories/` | GET | Danh mục |
| `/survey/api/question-types/` | GET | Loại câu hỏi |

---

## 8. CÁC CHỨC NĂNG CHÍNH CỦA HỆ THỐNG

### 8.1. Quản lý tài khoản (Account Management)
- Tạo, sửa, xóa, khóa/mở khóa tài khoản người dùng
- Phân quyền: Admin (superuser), Manager (staff), Staff (user thường)
- Gán người dùng vào đơn vị (Organization) với chức vụ (position)
- Thao tác hàng loạt: kích hoạt, khóa, xóa nhiều tài khoản cùng lúc
- Đăng nhập qua form AJAX với ghi nhớ session

### 8.2. Quản lý đơn vị (Organization Management)
- Tổ chức cây đơn vị hành chính 5 cấp:
  - Thành phố → Sở/Ngành → Quận/Huyện → Xã/Phường → Đơn vị sự nghiệp
- Mỗi đơn vị có mã code và tên riêng, có thể có đơn vị cha

### 8.3. Quản lý nhóm đối tượng (Target Group Management)
- Tạo nhóm đối tượng khảo sát (VD: Lãnh đạo, Chuyên trách, CNTT, Cán bộ...)
- Mỗi nhóm có icon riêng, mã code, mô tả
- Gán biểu mẫu (forms) cho từng nhóm (lưu dạng JSONField)
- Kích hoạt/vô hiệu hóa nhóm

### 8.4. Quản lý biểu mẫu (Survey Form Management)
- Tạo đợt khảo sát với tiêu đề, mô tả, thời gian bắt đầu/kết thúc
- Mã biểu mẫu tự động: BM-001, BM-002,...
- Builder tạo câu hỏi: sections (A, B, C...) → Questions (nhiều loại)
- Các loại câu hỏi: radio, checkbox, text, scale, dropdown, grid...
- Hỗ trợ component_type: question, title, paragraph, section_break, personal_info
- Câu hỏi có options, logic điều kiện (condition_logic), validation
- Nhân bản, xuất JSON, phát hành khảo sát

### 8.5. Gán biểu mẫu (Assignment Management)
- Gán một hoặc nhiều biểu mẫu cho một nhóm đối tượng
- Tạo mapping SurveyAssignment: survey ↔ target_group ↔ form_code
- Gỡ biểu mẫu khỏi nhóm

### 8.6. Cổng khảo sát công chức (Public Survey Portal) - 3 Bước
- **Bước 1 - Xác minh:** Chọn đơn vị công tác + nhóm đối tượng
- **Bước 2 - Cá nhân:** Nhập họ tên, chức vụ, bộ phận, SĐT, email, ghi chú
- **Bước 3 - Xác nhận:** Review thông tin, xem danh sách biểu mẫu được gán
- Tự động lưu phiên làm việc (session key), cho phép làm lại nếu chưa nộp

### 8.7. Dashboard Người dùng
- Hiển thị danh sách biểu mẫu được gán sau khi xác nhận cổng khảo sát
- Theo dõi tiến độ từng biểu mẫu: Chưa bắt đầu / Đang làm / Hoàn thành
- Sắp xếp theo trạng thái ưu tiên
- Thống kê tổng quan: tổng số, đã hoàn thành, đang làm, chưa làm

### 8.8. Dashboard Admin
- **Tổng quan:** Thống kê số liệu khảo sát
- **Quản lý nhóm đối tượng:** CRUD nhóm
- **Quản lý biểu mẫu:** CRUD biểu mẫu
- **Gán biểu mẫu:** Quản lý gán nhóm ↔ biểu mẫu
- **Quản lý tài khoản:** CRUD tài khoản, thao tác hàng loạt

### 8.9. Làm khảo sát (Public Survey Taking)
- Giao diện public làm khảo sát theo sections
- Tự động lưu draft khi làm dở
- Theo dõi tiến độ từng section
- Submit response → cập nhật SurveyProgress

### 8.10. Báo cáo & Phân tích (Scoring & Aggregation)
- **ScoringConfig:** Cấu hình chấm điểm với criteria_mapping (JSON)
- **AggregatedResult:** Kết quả tổng hợp theo cấp (city/department/district/ward/unit/group)
- **ComparisonReport:** Báo cáo so sánh (giữa đơn vị, giữa năm, giữa nhóm)
- Hỗ trợ xuất file PDF/Excel

---

## 9. QUY TRÌNH LUỒNG DỮ LIỆU

### 9.1. Luồng quản trị hệ thống

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ADMIN (Quản trị viên)                                                      │
│                                                                             │
│  1. Tạo tài khoản User (staff)                                             │
│     → POST /analytics/api/accounts/create/                                 │
│     → Gán Organization, role, position                                      │
│                                                                             │
│  2. Tạo đơn vị (Organization)                                              │
│     → Django Admin hoặc API                                                 │
│     → Phân cấp: city → department → district → ward → unit                 │
│                                                                             │
│  3. Tạo nhóm đối tượng (TargetGroup)                                       │
│     → POST /analytics/api/target-groups/create/                             │
│     → VD: Lãnh đạo (CBQL), Chuyên trách (CT), CNTT...                      │
│                                                                             │
│  4. Tạo biểu mẫu khảo sát (Survey)                                         │
│     → POST /survey/api/surveys/ hoặc /analytics/api/survey-forms/create/    │
│     → Thêm Sections (A, B, C...) + Questions (radio, checkbox, text...)     │
│     → Phát hành: POST /survey/api/surveys/{id}/publish/                     │
│                                                                             │
│  5. Gán biểu mẫu cho nhóm đối tượng                                        │
│     → POST /analytics/api/assignments/create/                               │
│     → Nhóm CBQL được gán BM-03, BM-04...                                   │
│     → Hoặc tạo SurveyAssignment mapping chi tiết                           │
│                                                                             │
│  6. Xem báo cáo trên Dashboard                                              │
│     → /analytics/ - Dashboard tổng quan                                     │
│     → Kết quả tổng hợp từ AggregatedResult                                  │
│     → So sánh từ ComparisonReport                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2. Luồng User (Công chức) làm khảo sát

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  USER (Công chức - Người dùng cuối)                                          │
│                                                                             │
│  1. Đăng nhập (nếu có tài khoản)                                           │
│     → POST /accounts/login/ → authenticate → session                        │
│                                                                             │
│  2. Vào Cổng khảo sát công chức                                            │
│     → GET /accounts/congkhaosat/?survey_id=X                               │
│                                                                             │
│  ═══════════════════════════ 3 BƯỚC ═══════════════════════════════════    │
│                                                                             │
│  BƯỚC 1 - XÁC MINH                                                         │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ • Chọn đơn vị công tác (GET /accounts/api/organizations/)     │          │
│  │ • Chọn nhóm đối tượng (GET /accounts/api/target-groups/)      │          │
│  │   → Xem danh sách biểu mẫu được gán (từ target_group.forms)   │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                              ↓                                               │
│  BƯỚC 2 - CÁ NHÂN                                                          │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ • Nhập: Họ tên, Chức vụ, Bộ phận, SĐT, Email, Ghi chú       │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                              ↓                                               │
│  BƯỚC 3 - XÁC NHẬN                                                         │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ • Xem lại toàn bộ thông tin                                 │          │
│  │ • Xem danh sách biểu mẫu được gán                           │          │
│  │ → POST /accounts/api/congkhaosat/submit/                     │          │
│  │   → Tạo SurveyParticipant + Response (draft)                 │          │
│  │   → Tạo SurveyProgress (not_started) cho từng biểu mẫu       │          │
│  └──────────────────────────────────────────────────────────────┘          │
│  ═══════════════════════════════════════════════════════════════════════    │
│                              ↓                                               │
│  3. Dashboard khảo sát cá nhân                                             │
│     → GET /accounts/survey-dashboard/                                      │
│     → Hiển thị danh sách biểu mẫu được gán + tiến độ                       │
│     • [Chưa bắt đầu] [Đang làm] [Hoàn thành]                              │
│                              ↓                                               │
│  4. Làm khảo sát (cho từng biểu mẫu)                                       │
│     → Click "Tiếp tục" → GET /survey/public/{survey_id}/                   │
│     → Lấy câu hỏi theo sections                                             │
│     → Trả lời → tự động lưu draft (AJAX)                                    │
│     → POST /survey/api/public/responses/submit/ khi hoàn thành              │
│       → Cập nhật SurveyProgress → completed                                 │
│                              ↓                                               │
│  5. Kết quả → Dashboard Admin (phía Admin)                                 │
│     → AggregatedResult được tính toán                                       │
│     → Hiển thị trên dashboard, báo cáo so sánh                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3. Sơ đồ quan hệ dữ liệu chính

```
                  ┌──────────────┐
                  │ Organization │
                  └──────┬───────┘
                         │ 1
                         │ *
                  ┌──────▼───────┐          ┌───────────────────┐
                  │     User     │──────────│  SurveyParticipant │
                  └──────────────┘          └────────┬──────────┘
                                                     │ 1
                                                     │ *
                         ┌───────────────────────────▼──────────────┐
                         │           SurveyProgress                  │
                         │  (theo dõi từng biểu mẫu cho participant) │
                         └──────┬────────────────────────┬──────────┘
                                │ 1                      │ *
                    ┌───────────▼──────────────┐      ┌──▼──────────────┐
                    │        Response          │      │     Survey      │
                    │  (phiếu trả lời / draft) │      │ (đợt khảo sát)  │
                    └──────────────────────────┘      └──┬──────────────┘
                                                          │ 1
                                                          │ *
                    ┌──────────────────────────┐      ┌──▼──────────────┐
                    │     SurveyAssignment      │◄─────│     Section     │
                    │  (mapping nhóm ↔ biểu mẫu) │      └──┬──────────────┘
                    └──────────────────────────┘          │ 1
                                                          │ *
                    ┌──────────────────────────┐      ┌──▼──────────────┐
                    │      TargetGroup          │      │    Question     │
                    │  (nhóm đối tượng)         │      └──┬──────────────┘
                    └──────────────────────────┘         │ *
                                                  ┌──────▼──────────────┐
                                                  │    QuestionType     │
                                                  └─────────────────────┘
```

### 9.4. Mô tả luồng dữ liệu tóm tắt

```
Admin tạo tài khoản ──────────► User đăng nhập
       │                              │
       │                              ▼
       │                   Vào Cổng khảo sát
       │                       3 bước
       │                              │
       ▼                              ▼
Admin tạo nhóm đối tượng ──► Chọn nhóm → Xem biểu mẫu được gán
       │                              │
       │                              ▼
       ▼                   Nhập thông tin cá nhân
Admin tạo biểu mẫu ──────► Xác nhận → Tạo participant
       │                              │
       │                              ▼
       ▼                   Dashboard khảo sát → Làm bài
Admin gán biểu mẫu ──────► Submit response → Hoàn thành
       │                              │
       │                              ▼
       ▼                   Kết quả → Dashboard Admin
Xem báo cáo ◄──────────── Báo cáo so sánh → Báo cáo tổng hợp