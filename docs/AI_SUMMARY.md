# TỔNG QUAN DỰ ÁN SURVEYPLUS (CHO AI KHÁC)

## 1. GIỚI THIỆU

**SurveyPlus** là hệ thống khảo sát trực tuyến xây dựng trên **Django 6.x + Django REST Framework**, phục vụ công tác đánh giá **Chỉ số Cải cách Hành chính (CCHC)**. Hệ thống hỗ trợ đa cấp độ quản lý từ Thành phố → Sở/Ngành → Quận/Huyện → Xã/Phường → Đơn vị sự nghiệp.

- **Ngôn ngữ:** Python (Django 6.x)
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Frontend:** HTML/CSS/JS (vanilla) + Bootstrap
- **PDF:** ReportLab
- **Git:** https://github.com/DumBoa/Survey.git

---

## 2. CẤU TRÚC THƯ MỤC

```
Survey/
├── apps/
│   ├── accounts/          # Quản lý người dùng, tổ chức, đăng nhập
│   │   ├── models.py      # User, Organization
│   │   ├── views.py       # Login/Logout, survey dashboard, PDF export
│   │   └── urls.py
│   │
│   ├── analytics/         # Quản lý admin, tổng hợp, báo cáo
│   │   ├── models.py      # TargetGroup, ScoringConfig, AggregatedResult, ComparisonReport
│   │   ├── views.py       # Admin APIs (accounts, groups, surveys, orgs)
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   └── survey/            # Quản lý khảo sát (core)
│       ├── models.py      # Survey, Section, Question, Response, SurveyProgress, SurveyUnitStatus, SurveyAssignment, SurveyParticipant
│       ├── views.py       # Survey APIs, public survey portal
│       ├── serializers.py
│       ├── utils.py       # update_survey_unit_status()
│       └── urls.py
│
├── config/                # Django project config
│   ├── settings.py        # INSTALLED_APPS, REST_FRAMEWORK, AUTH_USER_MODEL
│   └── urls.py            # URL routing + root_redirect()
│
├── templates/
│   ├── base.html
│   └── components/
│
├── static/                # CSS, JS, images
└── docs/
    ├── PROJECT_REPORT.md  # Báo cáo chi tiết (531 dòng)
    └── AI_SUMMARY.md      # File này
```

---

## 3. MÔ HÌNH DỮ LIỆU CHI TIẾT

### 3.1. apps/accounts/models.py

| Model | Fields | Ghi chú |
|-------|--------|---------|
| **Organization** | `name`, `code` (unique), `level` (city/department/district/ward/unit), `parent` (FK self), `is_active` | Phân cấp 5 cấp, có parent-child |
| **User** (AbstractUser) | `phone_number`, `organization` (FK→Organization), `position`, `is_surveyor`, `last_active_at`, `target_groups` (M2M→TargetGroup) | Custom user model, có M2M với TargetGroup |

### 3.2. apps/survey/models.py

| Model | Fields | Ghi chú |
|-------|--------|---------|
| **SurveyCategory** | `name`, `description`, `icon` | Danh mục khảo sát |
| **Survey** | `title`, `slug` (unique), `description`, `category` (FK), `start_date`, `end_date`, `allow_after_deadline`, `status` (draft/active/closed/archived), `target_groups` (JSON), `settings` (JSON), `code` (auto BM-XXX) | **Đợt khảo sát** - tự sinh mã BM-XXX |
| **Section** | `survey` (FK), `code` (A,B,C...), `title`, `description`, `icon`, `order` | Phần trong khảo sát |
| **QuestionType** | `name`, `code`, `icon`, `has_options`, `has_validation` | Loại câu hỏi (text, choice, rating...) |
| **Question** | `section` (FK), `component_type` (question/title/paragraph/...), `title`, `description`, `question_type` (FK), `is_required`, `order`, `options` (JSON), `condition_logic` (JSON), `config` (JSON) | Câu hỏi, có JSON linh hoạt |
| **Blocklist** | `block_type` (ip/email/device/user), `value`, `reason`, `expires_at` | Chặn IP/email/device |
| **Response** | `survey` (FK), `respondent_ip`, `respondent_device_id`, `respondent_email`, `user_agent`, `started_at`, `submitted_at`, `time_taken`, `status` (draft/submitted), `answers` (JSON), `section_progress` (JSON), `is_verified`, `is_cleaned`, `is_duplicate`, `user` (FK) | **Phiếu trả lời** - lưu answers dạng JSON |
| **SurveyAssignment** | `survey` (FK), `form_code` (BM-XXX), `form_name`, `form_description`, `target_group_code`, `target_group_name`, `target_group_description`, `section` (FK), `is_active`, `order` | **Ánh xạ Nhóm ↔ Biểu mẫu** |
| **SurveyParticipant** | `survey` (FK), `agency`, `target_group_code`, `target_group_name`, `full_name`, `position`, `department`, `phone`, `email`, `notes`, `session_key`, `assigned_forms` (JSON), `response` (OneToOne→Response), `user` (FK), `ip_address`, `status` (draft/submitted/expired/cancelled), `submitted_at` | **Người tham gia** - thông tin từ cổng khảo sát |
| **SurveyProgress** | `participant` (FK), `survey` (FK), `form_code`, `response` (OneToOne), `status` (not_started/in_progress/completed/expired), `progress_percent`, `started_at`, `completed_at`, `last_accessed_at` | **Tiến độ từng biểu mẫu** |
| **SurveyUnitStatus** | `survey` (FK), `organization` (FK→Organization), `status` (pending/in_progress/completed/expired), `completed_count`, `total_assignees`, `completed_at` | **Trạng thái đơn vị** |

### 3.3. apps/analytics/models.py

| Model | Fields | Ghi chú |
|-------|--------|---------|
| **TargetGroup** | `code` (unique), `name`, `description`, `icon` (7 choices), `is_active`, `surveys` (M2M→Survey), `forms` (JSON) | **Nhóm đối tượng** - có icon, gán survey và forms |
| **ScoringConfig** | `name`, `survey` (FK), `criteria_mapping` (JSON), `is_active` | **Cấu hình chấm điểm** - chưa tích hợp scoring engine |
| **AggregatedResult** | `survey` (FK), `level` (6 levels), `entity_name`, `entity_code`, `total_responses`, `average_score`, `raw_data` (JSON), `year`, `quarter` | **Kết quả tổng hợp** - chưa có UI |
| **ComparisonReport** | `name`, `survey` (FK), `comparison_type` (units/years/groups), `report_data` (JSON), `export_file` | **Báo cáo so sánh** - chưa có UI |

---

## 4. LUỒNG NGHIỆP VỤ CHÍNH

### 4.1. Admin tạo khảo sát
```
1. Tạo Survey (đợt khảo sát) → tự sinh code BM-XXX
2. Tạo Section (Phần A, B, C...)
3. Tạo Question trong từng Section
4. Tạo SurveyAssignment (gán biểu mẫu cho nhóm đối tượng)
5. Phát hành (status = active)
```

### 4.2. User làm khảo sát
```
1. Đăng nhập → redirect tới /accounts/survey-dashboard/
2. Dashboard hiển thị danh sách biểu mẫu được gán (từ SurveyAssignment)
3. Click "Bắt đầu" → vào cổng khảo sát public
4. Tự động tạo SurveyParticipant + SurveyProgress
5. Trả lời từng section → lưu draft tự động
6. Nộp → tạo Response (status=submitted) → cập nhật SurveyUnitStatus
```

### 4.3. Xác thực & phân quyền
```
- 2 cổng login: /accounts/login/ (admin) và /accounts/user-login/ (user)
- root_redirect(): admin → /analytics/, user → /accounts/survey-dashboard/
- AUTH_USER_MODEL = 'accounts.User'
- REST Framework: SessionAuthentication + IsAuthenticated
```

---

## 5. API ENDPOINTS CHÍNH

### 5.1. Survey APIs (`/survey/`)
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET/POST | `/survey/api/surveys/` | Danh sách/Tạo survey |
| GET/PUT/DELETE | `/survey/api/surveys/{id}/` | Chi tiết/Cập nhật/Xóa survey |
| GET/POST | `/survey/api/surveys/{id}/sections/` | Danh sách/Tạo section |
| GET/PUT/DELETE | `/survey/api/sections/{id}/` | Chi tiết section |
| GET/POST | `/survey/api/sections/{id}/questions/` | Danh sách/Tạo question |
| GET/PUT/DELETE | `/survey/api/questions/{id}/` | Chi tiết question |
| GET/POST | `/survey/api/responses/` | Danh sách/Tạo response |
| GET | `/survey/api/responses/{id}/` | Chi tiết response |
| GET | `/survey/api/surveys/{id}/stats/` | Thống kê survey |
| GET | `/survey/api/categories/` | Danh mục |
| GET | `/survey/api/question-types/` | Loại câu hỏi |
| GET | `/survey/public/{id}/` | Trang public làm survey |
| POST | `/survey/public/submit/` | Submit response |
| GET | `/survey/public/{id}/response/` | Lấy response hiện tại |
| GET | `/survey/public/{id}/embed/` | Embed survey |
| GET | `/survey/public/{id}/preview/` | Xem trước |
| GET | `/survey/public/{id}/mapping/` | Lấy mapping nhóm-biểu mẫu |
| GET | `/survey/public/{id}/target-groups/` | Lấy danh sách nhóm |
| POST | `/survey/{id}/duplicate/` | Nhân bản |
| GET | `/survey/{id}/export/` | Xuất JSON |
| POST | `/survey/{id}/publish/` | Phát hành |

### 5.2. Analytics APIs (`/analytics/`)
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET/POST | `/analytics/api/target-groups/` | CRUD nhóm đối tượng |
| GET/PUT/DELETE | `/analytics/api/target-groups/{id}/` | |
| GET/POST | `/analytics/api/survey-forms/` | CRUD survey (admin) |
| GET/PUT/DELETE | `/analytics/api/survey-forms/{id}/` | |
| GET/POST | `/analytics/api/accounts/` | CRUD tài khoản |
| GET/PUT/DELETE | `/analytics/api/accounts/{id}/` | |
| POST | `/analytics/api/accounts/bulk-action/` | Thao tác hàng loạt |
| GET/POST | `/analytics/api/organizations/` | CRUD đơn vị |
| GET/PUT/DELETE | `/analytics/api/organizations/{id}/` | |
| GET/POST | `/analytics/api/assignments/` | CRUD phân công |
| GET/PUT/DELETE | `/analytics/api/assignments/{id}/` | |
| POST | `/analytics/api/assignments/remove-form/` | Gỡ biểu mẫu |
| GET | `/analytics/api/survey-dashboard/{id}/` | Dashboard survey |
| GET | `/analytics/api/organizations/status/` | Trạng thái đơn vị |
| GET | `/analytics/api/organizations/status/{id}/` | Chi tiết trạng thái |

### 5.3. Accounts APIs (`/accounts/`)
| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET/POST | `/accounts/login/` | Admin login |
| GET/POST | `/accounts/user-login/` | User login |
| POST | `/accounts/logout/` | Logout |
| GET | `/accounts/survey-dashboard/` | User dashboard |
| GET | `/accounts/survey-dashboard/continue/{id}/` | Tiếp tục khảo sát |
| GET | `/export/response/{id}/pdf/` | Xuất PDF phiếu trả lời |

---

## 6. TRẠNG THÁI HIỆN TẠI (TỔNG QUAN)

### ✅ ĐÃ HOÀN THÀNH (Core - ~60%)
- **Quản lý tài khoản & phân quyền** (85%): Login/logout, CRUD user, phân quyền admin/user/staff, gán organization + target_group
- **Survey Builder** (80%): Tạo survey, sections, questions (nhiều loại), categories, nhân bản, xuất JSON, phát hành
- **Cổng khảo sát public** (75%): Làm survey online, auto-save draft, theo dõi tiến độ, tự động điền thông tin user, chống trả lời nhiều lần
- **Dashboard Admin** (45%): Tổng quan thống kê, theo dõi tiến độ đơn vị, phân loại Sở/Phường, progress bar
- **Dashboard User** (75%): Danh sách biểu mẫu được gán, theo dõi tiến độ, bắt đầu/tiếp tục/làm lại, xuất PDF
- **Tổng hợp & báo cáo** (40%): SurveyUnitStatus tự động cập nhật, API tổng hợp theo cấp độ
- **Phân công biểu mẫu** (100%): SurveyAssignment (gán biểu mẫu cho nhóm đối tượng)

### ⚠️ CẦN CẢI THIỆN
- ScoringConfig chưa tích hợp scoring engine
- AggregatedResult, ComparisonReport chưa có UI
- Chưa có forgot password / reset password
- Chưa có export báo cáo tổng hợp Excel/PDF
- Chưa có biểu đồ dashboard
- Chưa có notification (email)

### ❌ CHƯA CÓ
- Logic điều kiện (jump/skip logic)
- Import Word/Excel câu hỏi
- Import/Export Excel đơn vị
- 2FA
- SSO/LDAP
- Mobile app
- Offline survey
- Phân tích dữ liệu tự động

---

## 7. VỀ VIỆC THÊM BIỂU MẪU BM-01 ĐẾN BM-10

### Câu hỏi: Có thêm được không?

**TRẢ LỜI: CÓ THỂ THÊM ĐƯỢC, và hệ thống đã được thiết kế để hỗ trợ việc này.**

### Giải thích chi tiết:

#### 7.1. Cơ chế hiện tại đã hỗ trợ

Hệ thống hiện tại đã có đầy đủ model để quản lý 10 biểu mẫu này:

1. **Survey model** - mỗi biểu mẫu là một `Survey` record với `code` tự sinh (BM-001, BM-002...)
2. **SurveyAssignment** - ánh xạ giữa biểu mẫu (form_code) và nhóm đối tượng (target_group_code)
3. **SurveyParticipant** - lưu thông tin người tham gia + `assigned_forms` (JSON list)
4. **SurveyProgress** - theo dõi tiến độ từng biểu mẫu cho từng người

#### 7.2. Cách triển khai 10 biểu mẫu

**Cách 1: Mỗi biểu mẫu là một Survey riêng (Khuyến nghị)**
```
- Tạo 10 Survey records: BM-01, BM-02, ..., BM-10
- Mỗi Survey có sections và questions riêng
- Dùng SurveyAssignment để gán:
  - BM-01, BM-02, BM-03 → Nhóm "Đoàn khảo sát"
  - BM-04 → Nhóm "Lãnh đạo quản lý"
  - BM-05 → Nhóm "Cán bộ chuyên môn"
  - BM-06 → Nhóm "Cán bộ CNTT"
  - BM-07, BM-08, BM-10 → Nhóm "Đoàn khảo sát"
  - BM-09 → Tất cả các nhóm
```

**Cách 2: Một Survey lớn chứa tất cả (Nếu muốn gom)**
```
- Tạo 1 Survey "Khảo sát CCHC"
- Tạo 10 Sections tương ứng 10 biểu mẫu
- Dùng target_groups trong Section/Question để phân quyền
```

#### 7.3. Những điều chỉnh cần thiết

| Hạng mục | Mô tả | Mức độ |
|----------|-------|--------|
| **Tạo dữ liệu** | Tạo 10 Survey + sections + questions qua admin UI hoặc API | Dễ |
| **Phân công** | Tạo SurveyAssignment để gán biểu mẫu cho nhóm | Dễ |
| **Tạo nhóm đối tượng** | Tạo TargetGroup: "Đoàn khảo sát", "Lãnh đạo quản lý", "Cán bộ chuyên môn", "Cán bộ CNTT" | Dễ |
| **Gán user vào nhóm** | Gán user vào TargetGroup tương ứng | Dễ |
| **Dashboard hiển thị** | Dashboard user đã tự động hiển thị các biểu mẫu được gán | Không cần sửa |
| **Tiến độ theo dõi** | SurveyProgress tự động theo dõi từng biểu mẫu | Không cần sửa |
| **Báo cáo tổng hợp** | Cần thêm UI cho AggregatedResult và ComparisonReport | Trung bình |
| **Scoring CCHC** | Cần tích hợp ScoringConfig với response pipeline | Trung bình |

#### 7.4. Lưu ý khi thêm

1. **Mã biểu mẫu**: Survey model tự sinh code BM-XXX, có thể set thủ công BM-01 → BM-10
2. **Nhóm biểu mẫu**: Có thể dùng SurveyCategory để phân nhóm (I, II, III)
3. **Phân quyền**: Dùng SurveyAssignment để kiểm soát ai được làm biểu mẫu nào
4. **Không cần code mới**: Toàn bộ logic CRUD, làm survey, theo dõi tiến độ đã có sẵn

---

## 8. HƯỚNG DẪN CHO AI KHÁC

### 8.1. Các file quan trọng nhất cần đọc

| File | Lý do |
|------|-------|
| `apps/survey/models.py` | Hiểu toàn bộ data model cốt lõi (510 dòng) |
| `apps/survey/views.py` | Hiểu luồng xử lý survey, public portal (1094 dòng) |
| `apps/survey/serializers.py` | Hiểu API serializers (163 dòng) |
| `apps/survey/utils.py` | Hiểu logic cập nhật trạng thái đơn vị (125 dòng) |
| `apps/accounts/models.py` | Hiểu User và Organization (62 dòng) |
| `apps/analytics/models.py` | Hiểu TargetGroup, Scoring, AggregatedResult (106 dòng) |
| `config/urls.py` | Hiểu routing tổng thể (29 dòng) |
| `config/settings.py` | Hiểu cấu hình Django (147 dòng) |
| `docs/PROJECT_REPORT.md` | Báo cáo chi tiết đầy đủ (531 dòng) |

### 8.2. Các lưu ý kỹ thuật

1. **Import alias**: Trong `survey/views.py`, các model được import với alias để tránh conflict (VD: `Survey as SurveyModel`, `Response as ResponseModel`)
2. **JSON fields**: Nhiều model dùng JSONField để lưu dữ liệu linh hoạt (answers, options, settings, criteria_mapping...)
3. **Session-based tracking**: Response được track qua session key `survey_response_{survey_id}`
4. **Auto code**: Survey model tự sinh code BM-XXX trong `save()` method
5. **2 cổng login**: Admin và user riêng biệt, phân biệt bằng `is_admin_user()` check
6. **Django 6.x**: Project dùng Django 6.0.6, cần lưu ý các API changes

### 8.3. Các lỗi / vấn đề tiềm ẩn

1. **Duplicate field**: `SurveyParticipant` có 2 field `session_key` (dòng 312 và 339)
2. **Dead code**: `utils.py` dòng 125 có `return summary` sau `return {...}` (unreachable)
3. **Thiếu validation**: Nhiều API chưa có validate dữ liệu đầu vào đầy đủ
4. **SQLite limitation**: Không phù hợp cho production, cần migrate lên PostgreSQL
5. **Thiếu unit test**: Hầu hết các file tests.py đều trống

---

## 9. KẾT LUẬN

Hệ thống đã có **nền tảng vững chắc** để triển khai 10 biểu mẫu khảo sát CCHC (BM-01 → BM-10). 

- **Phần core (tạo survey, làm survey, theo dõi tiến độ) đã hoàn chỉnh** - chỉ cần nhập liệu
- **Phần báo cáo, phân tích, xuất dữ liệu cần phát triển thêm**
- **Có thể mở rộng linh hoạt** nhờ thiết kế JSON fields và SurveyAssignment

**Để triển khai thực tế, cần ưu tiên:**
1. Nhập 10 biểu mẫu vào hệ thống (tạo Survey + sections + questions)
2. Tạo TargetGroup và gán user
3. Tạo SurveyAssignment để phân quyền
4. Phát triển giao diện báo cáo tổng hợp (AggregatedResult + ComparisonReport)
5. Tích hợp ScoringConfig để tự động tính điểm CCHC
6. Thêm chức năng xuất báo cáo Excel/PDF tổng hợp