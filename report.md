# BÁO CÁO PHÂN TÍCH DỰ ÁN SURVEY

> **Ngày tạo:** 29/06/2026  
> **Phạm vi quét:** `apps/accounts`, `apps/analytics`, `apps/survey`

---

## 1. TỔNG QUAN KIẾN TRÚC

**Framework:** Django 6.0.6 + Django REST Framework  
**Database:** SQLite3  
**App đã có:** 3 app (`accounts`, `survey`, `analytics`)

### Sơ đồ luồng chính:

```
User → Login → Survey Edit (tạo/sửa khảo sát)
                     ↓
                Publish → Public Survey Link
                              ↓
                    Người dân làm khảo sát (public)
                              ↓
                     Analytics (thống kê, báo cáo)
```

---

## 2. CHI TIẾT TỪNG APP

### 2.1. apps/accounts

#### ✅ Đã làm được:

| Thành phần | Mức độ | Ghi chú |
|---|---|---|
| **Model `Organization`** | ✅ Hoàn chỉnh | Cây phân cấp 5 cấp (city → department → district → ward → unit), có parent self-FK |
| **Model `User`** | ✅ Hoàn chỉnh | Kế thừa `AbstractUser`, thêm organization, position, phone, is_surveyor. Đã fix groups/permissions conflict |
| **Admin** | ✅ Hoàn chỉnh | Cấu hình OrganizationAdmin + UserAdmin (kế thừa BaseUserAdmin để có đổi mật khẩu) |
| **Login (API)** | ✅ Hoàn chỉnh | POST login JSON, session management, remember-me, redirect |
| **Login (GET)** | ✅ Cơ bản | Render form login, redirect nếu đã đăng nhập |
| **Cổng khảo sát 3 bước** | ✅ Hoàn chỉnh | `congkhaosat_view`, `congkhaosat_init`, `congkhaosat_submit` - xử lý survey timing, draft resume, personal info |

#### ❌ Chưa làm / Thiếu:

| Thiếu | Mức độ ưu tiên | Ghi chú |
|---|---|---|
| 🚫 Đăng xuất (logout) | **Cao** | Không có URL/view logout nào |
| 🚫 Đăng ký tài khoản | **Cao** | Không có register form/API |
| 🚫 Quên mật khẩu | **Trung bình** | Không có password reset flow |
| 🚫 Trang `accounts_main.html` | **Thấp** | URL `/accounts/` render template này nhưng có thể chưa tồn tại |
| 🚫 Trang `congkhaosat_no_survey.html` | **Thấp** | View có render nhưng template chưa chắc tồn tại |
| 🚫 Profile management | **Trung bình** | Không có đổi thông tin cá nhân |

---

### 2.2. apps/survey

#### ✅ Đã làm được:

| Thành phần | Mức độ | Ghi chú |
|---|---|---|
| **Model `Survey`** | ✅ Hoàn chỉnh | 4 trạng thái (draft/active/closed/archived), JSON settings, target_groups |
| **Model `Section`** | ✅ Hoàn chỉnh | Phân khảo sát thành phần (A, B, C...), mỗi phần có code riêng |
| **Model `Question`** | ✅ Hoàn chỉnh | Hỗ trợ component_type (question/title/paragraph...), options JSON, config JSON cho rating-grid & data-table, condition_logic |
| **Model `QuestionType`** | ✅ Hoàn chỉnh | Seeded data, has_options, has_validation flags |
| **Model `Response`** | ✅ Hoàn chỉnh | Draft/submitted, answers JSON, section_progress JSON, is_cleaned, is_duplicate, IP/device tracking |
| **Model `Blocklist`** | ✅ Cơ bản | Chặn theo IP/Email/Device/User |
| **Survey CRUD APIs** | ✅ Hoàn chỉnh | DRF Class-based views: List, Detail, Create, Update, Delete |
| **Section CRUD APIs** | ✅ Hoàn chỉnh | Đầy đủ CRUD |
| **Question CRUD APIs** | ✅ Hoàn chỉnh | Đầy đủ CRUD |
| **Response APIs** | ✅ Hoàn chỉnh | Tạo/Cập nhật/Draft/Submit |
| **Public survey views** | ✅ Hoàn chỉnh | Làm khảo sát public, session-based, tự động resume draft |
| **Survey Stats API** | ✅ Cơ bản | Đếm responses, completion rate, section stats |
| **Duplicate/Export/Publish** | ✅ Cơ bản | Nhân bản khảo sát (kèm sections/questions), export JSON, publish |
| **Serializers** | ✅ Hoàn chỉnh | Đầy đủ các serializer: Survey, Section, Question, Response, Public variants, Submit validation |

#### ⚠️ Vấn đề / Thiếu:

| Vấn đề | Mức độ | Chi tiết |
|---|---|---|
| ⚠️ **Không có `created_by`** | **Cao** | Survey model không có ForeignKey tới User. analytics/views.py dùng `hasattr(survey, 'created_by')` sẽ luôn False |
| ⚠️ **Thiếu Embed template** | **Trung bình** | View `survey_public_embed` render `survey/survey_embed.html` nhưng file chưa tồn tại |
| ⚠️ **survey2_view chưa chắc có template** | **Trung bình** | Render `survey/survey2.html` - chưa rõ có tồn tại không |
| 🚫 **Không có permission granular** | **Trung bình** | Chỉ dùng `IsAuthenticated` - ai login cũng làm được tất cả |
| 🚫 **Không có test** | **Thấp** | tests.py trống |
| 🚫 **Không xử lý Blocklist trong view** | **Trung bình** | Model Blocklist đã tạo nhưng không được dùng trong bất kỳ view/public API nào |
| 🚫 **Không có email verification** | **Thấp** | Response.is_verified = True nhưng không có flow gửi email |

---

### 2.3. apps/analytics

#### ✅ Đã làm được:

| Thành phần | Mức độ | Ghi chú |
|---|---|---|
| **Model `ScoringConfig`** | ✅ Cơ bản | Cấu hình chấm điểm cho survey |
| **Model `AggregatedResult`** | ✅ Cơ bản | Lưu kết quả tổng hợp theo cấp (city/unit/group), theo năm/quý |
| **Model `ComparisonReport`** | ✅ Cơ bản | Lưu báo cáo so sánh |
| **Survey List API** | ✅ Hoàn chỉnh | Filter (status/category/search), pagination, kèm thống kê responses |
| **Survey Detail API** | ✅ Hoàn chỉnh | Sections/questions/stats chi tiết |
| **Survey CRUD (tạo/sửa/xóa)** | ✅ Cơ bản | JSON function-based views |
| **Bulk actions API** | ✅ Cơ bản | Archive/Publish/Close/Delete hàng loạt |
| **Categories API** | ✅ Cơ bản | Danh sách danh mục kèm count |
| **Dashboard Stats API** | ✅ Cơ bản | Tổng quan: total surveys active/draft/closed, recent surveys |

#### ❌ Chưa làm / Vấn đề:

| Vấn đề | Mức độ | Chi tiết |
|---|---|---|
| ⚠️ **Duplicate CRUD với survey app** | **Cao** | `analytics/views.py` tự implement CRUD survey (function-based, JsonResponse) TRONG KHI `survey/views.py` đã có CRUD (DRF). 2 luồng code khác nhau cho cùng nghiệp vụ → khó maintain, dễ bug |
| 🚫 **ScoringConfig không có view** | **Cao** | Model đã có nhưng không có view nào dùng tới - không thể cấu hình chấm điểm |
| 🚫 **AggregatedResult không có view** | **Cao** | Model đã có nhưng không có tính toán hay API - data rỗng |
| 🚫 **ComparisonReport không có view** | **Cao** | Model đã có nhưng không cho phép tạo/xem báo cáo so sánh |
| 🚫 **Không có chart/dashboard UI** | **Cao** | `analytics_main.html` chỉ là template render, không có dữ liệu/biểu đồ |
| 🚫 **Không có export (PDF/Excel)** | **Cao** | ComparisonReport có `export_file` field nhưng không có code export |

---

## 3. VẤN ĐỀ LIÊN KẾT GIỮA CÁC APP

| Vấn đề | Mô tả | Ảnh hưởng |
|---|---|---|
| 🔴 **CRUD Survey trùng lặp** | Survey CRUD trong `analytics/views.py` (function-based) và `survey/views.py` (DRF) | Hai luồng code riêng, cùng thao tác trên Survey/Section/Question - có thể gây inconsistent state, khó debug |
| 🔴 **Luồng congkhaosat tách biệt** | Cổng khảo sát 3 bước ở accounts tự tạo Response, không đi qua survey's submit flow | Thiếu đồng bộ, response không có `respondent_ip`/`user_agent` ở bước đầu |
| 🟡 **Survey.category không được đồng bộ** | SurveyCategory được tạo trong analytics/survey APIs nhưng không có seeding data ban đầu | Người dùng tự tạo category qua admin, không có mặc định |
| 🟡 **Không chia sẻ base template chung** | Base template quá minimal, mỗi app tự có layout riêng | Giao diện không đồng nhất, khó maintain |
| 🟡 **Public response flow: 2 cách** | `congkhaosat_submit` (accounts) vs `PublicResponseView` (survey) dùng 2 cách lưu session khác nhau | Có thể mất response khi chuyển trang |

---

## 4. THỐNG KÊ CODE

| App | Models | Views | URLs | Templates | Files |
|---|---|---|---|---|---|
| accounts | 2 (Organization, User) | 4 functions | 5 routes | 3 templates | ~7 files |
| survey | 6 models | ~15 views/classes | 18 routes | 4 templates | ~10 files |
| analytics | 3 models | 10 functions | 8 routes | 2 templates | ~7 files |
| **Tổng** | **11 models** | **~29 views** | **31 routes** | **9 templates** | **~24 files** |

---

## 5. KHUYẾN NGHỊ ƯU TIÊN

### Mức 1 - Critical (cần làm ngay):
1. **Survey model** thêm `created_by = ForeignKey(User)` - và cập nhật analytics code dùng chính xác field này
2. **Thống nhất CRUD survey**: Chỉ giữ 1 luồng (DRF ở survey app), analytics chỉ gọi API đó
3. **Thêm logout** và cơ chế session của accounts
4. **Đồng bộ luồng congkhaosat** với luồng survey public submit

### Mức 2 - High:
5. **Implement scoring engine** - view tính toán AggregatedResult từ Response answers
6. **Implement ComparisonReport** - tạo báo cáo so sánh
7. **Blocklist middleware** - kiểm tra IP/email trước khi cho phép submit
8. **Base template chung** với navbar, sidebar, breadcrumb

### Mức 3 - Medium:
9. Permission system chi tiết (quyền xem/sửa/xóa theo organization)
10. Export Excel/PDF
11. Tests cho các API

### Mức 4 - Low:
12. Email verification cho responses
13. Seed data cho SurveyCategory
14. Dashboard với biểu đồ (Chart.js)

---

## 6. FILE STRUCTURE HIỆN TẠI

```
Survey/
├── config/
│   ├── settings.py          # Django + DRF config
│   ├── urls.py              # Root URL, include 3 apps
│   ├── wsgi.py / asgi.py
│   └── __init__.py
├── apps/
│   ├── accounts/
│   │   ├── models.py        # Organization, User
│   │   ├── views.py         # Login, Congkhaosat (3 bước)
│   │   ├── urls.py          # 5 routes
│   │   ├── admin.py         # OrganizationAdmin, UserAdmin
│   │   ├── tests.py         # (trống)
│   │   └── templates/
│   │       └── accounts/
│   │           ├── login.html
│   │           ├── congkhaosat_main.html
│   │           └── congkhaosat_success.html
│   ├── survey/
│   │   ├── models.py        # Survey, Section, Question, QuestionType, Response, Blocklist
│   │   ├── views.py         # 15+ views/classes (CRUD, Public, Stats)
│   │   ├── serializers.py   # 10 serializers
│   │   ├── urls.py          # 18 routes
│   │   ├── admin.py         # (trống)
│   │   ├── tests.py         # (trống)
│   │   ├── management/      # seed_question_types command
│   │   └── templates/
│   │       └── survey/
│   │           ├── survey_main.html
│   │           ├── survey_public.html
│   │           └── survey-template.html
│   └── analytics/
│       ├── models.py        # ScoringConfig, AggregatedResult, ComparisonReport
│       ├── views.py         # 10 functions (CRUD survey, stats, categories)
│       ├── urls.py          # 8 routes
│       ├── tests.py         # (trống)
│       └── templates/
│           └── analytics/
│               ├── dashboard_base.html
                ├── ... .html
│               └── assignments.html
├── templates/
│   ├── base.html            # HTML cơ bản (tối thiểu)
│   ├── components/
│   └── layouts/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── libs/
├── db.sqlite3
├── manage.py
└── README.md