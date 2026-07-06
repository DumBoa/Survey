# BÁO CÁO TỔNG KẾT DỰ ÁN
## Hệ thống Khảo sát Trực tuyến (Survey Online)

**Ngày báo cáo:** 05/07/2026  
**Phiên bản hệ thống:** 1.0.0  
**Ngôn ngữ:** Python (Django)  
**Cơ sở dữ liệu:** SQLite (phát triển) / PostgreSQL (dự kiến production)

---

## MỤC LỤC

1. [Giới thiệu tổng quan hệ thống](#1-giới-thiệu-tổng-quan-hệ-thống)
2. [Bảng tổng hợp mức độ đáp ứng](#2-bảng-tổng-hợp-mức-độ-đáp-ứng)
   - 2.1. [Quản lý tài khoản](#21-quản-lý-tài-khoản)
   - 2.2. [Quản lý đơn vị (Organization)](#22-quản-lý-đơn-vị-organization)
   - 2.3. [Quản lý nhóm đối tượng (TargetGroup)](#23-quản-lý-nhóm-đối-tượng-targetgroup)
   - 2.4. [Quản lý biểu mẫu (Survey Form)](#24-quản-lý-biểu-mẫu-survey-form)
   - 2.5. [Gán biểu mẫu cho nhóm (Assignment)](#25-gán-biểu-mẫu-cho-nhóm-assignment)
   - 2.6. [Cổng khảo sát (Public Survey Portal)](#26-cổng-khảo-sát-public-survey-portal)
   - 2.7. [Dashboard Admin](#27-dashboard-admin)
   - 2.8. [Dashboard User](#28-dashboard-user)
   - 2.9. [Tổng hợp và báo cáo](#29-tổng-hợp-và-báo-cáo)
   - 2.10. [Cấu hình chấm điểm (ScoringConfig)](#210-cấu-hình-chấm-điểm-scoringconfig)
   - 2.11. [Kết quả tổng hợp (AggregatedResult)](#211-kết-quả-tổng-hợp-aggregatedresult)
   - 2.12. [Báo cáo so sánh (ComparisonReport)](#212-báo-cáo-so-sánh-comparisonreport)
3. [Đánh giá yêu cầu 3.3: Công cụ thu thập, tổng hợp và phân tích dữ liệu khảo sát](#3-đánh-giá-yêu-cầu-33-công-cụ-thu-thập-tổng-hợp-và-phân-tích-dữ-liệu-khảo-sát)
   - 3.1. [A. Mô tả công cụ](#31-a-mô-tả-công-cụ)
   - 3.2. [B. Chức năng thu thập, tổng hợp dữ liệu khảo sát](#32-b-chức-năng-thu-thập-tổng-hợp-dữ-liệu-khảo-sát)
   - 3.3. [C. Xử lý, phân tích và báo cáo kết quả](#33-c-xử-lý-phân-tích-và-báo-cáo-kết-quả)
   - 3.4. [D. Kết quả mong đợi](#34-d-kết-quả-mong-đợi)
4. [Phân tích khoảng trống (Gap Analysis)](#4-phân-tích-khoảng-trống-gap-analysis)
5. [Đề xuất cải thiện theo giai đoạn](#5-đề-xuất-cải-thiện-theo-giai-đoạn)
   - 5.1. [Giai đoạn 1: Ngay lập tức (Critical)](#51-giai-đoạn-1-ngay-lập-tức-critical)
   - 5.2. [Giai đoạn 2: Ngắn hạn (Short-term)](#52-giai-đoạn-2-ngắn-hạn-short-term)
   - 5.3. [Giai đoạn 3: Dài hạn (Long-term)](#53-giai-đoạn-3-dài-hạn-long-term)
6. [Danh sách file/template cần tạo thêm](#6-danh-sách-filetemplate-cần-tạo-thêm)
7. [Đánh giá tổng thể](#7-đánh-giá-tổng-thể)
8. [Phụ lục: Kiến trúc hệ thống](#8-phụ-lục-kiến-trúc-hệ-thống)

---

## 1. Giới thiệu tổng quan hệ thống

Hệ thống Khảo sát Trực tuyến (Survey Online) là một ứng dụng web được xây dựng trên nền tảng Django, phục vụ công tác khảo sát, thu thập và tổng hợp dữ liệu đánh giá Chỉ số Cải cách Hành chính (CCHC). Hệ thống hỗ trợ đa cấp độ quản lý từ Thành phố đến Sở/Ngành, Quận/Huyện, Xã/Phường và các đơn vị sự nghiệp.

**Cấu trúc phân hệ chính:**
- **accounts** (`apps/accounts/`): Quản lý người dùng, tổ chức, đăng nhập, dashboard user
- **analytics** (`apps/analytics/`): Quản lý admin, nhóm đối tượng, tổng hợp dữ liệu, dashboard admin
- **survey** (`apps/survey/`): Quản lý biểu mẫu, câu hỏi, phiếu trả lời, cổng khảo sát công khai

**Công nghệ sử dụng:**
- Backend: Django 5.x + Django REST Framework
- Frontend: HTML/CSS/JS (vanilla) với Bootstrap
- PDF: ReportLab
- Database: SQLite (dev) → PostgreSQL (production)

**Tổng số file nguồn:** 49 files (không kể thư viện, migrations, venv)
- Models: 12 models chính
- Views: 20+ views/API endpoints
- Templates: 15 templates HTML
- Static: 5 files (CSS, JS, images)

---

## 2. Bảng tổng hợp mức độ đáp ứng

### 2.1. Quản lý tài khoản

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Đăng nhập/Đăng xuất (phân biệt Admin và User) | ✅ Đã có | 2 cổng login riêng: `/accounts/login/` (admin), `/accounts/user-login/` (user) |
| Tạo, sửa, xóa, khóa/mở khóa tài khoản | ✅ Đã có | API CRUD trong `analytics/views.py` (lines 1007-1442) |
| Phân quyền: Admin (superuser), Manager (staff), Staff (user thường) | ✅ Đã có | Dựa trên `is_superuser`, `is_staff` của Django User model |
| Gán user vào đơn vị (Organization) và nhóm đối tượng (TargetGroup) | ✅ Đã có | `User.organization` (FK), `User.target_groups` (M2M) |
| Thao tác hàng loạt (kích hoạt, khóa, xóa) | ✅ Đã có | API `account_bulk_action_api` hỗ trợ activate/deactivate/delete hàng loạt |
| Xác thực 2FA | ❌ Chưa có | Chưa triển khai bất kỳ cơ chế 2FA nào |
| Quên mật khẩu | ❌ Chưa có | Không có flow reset/quên mật khẩu |
| Đăng nhập bằng SSO | ❌ Chưa có | Chưa tích hợp LDAP/OAuth/Google SSO |

### 2.2. Quản lý đơn vị (Organization)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| CRUD đơn vị với phân cấp 5 cấp | ✅ Đã có | 5 levels: city/department/district/ward/unit; có parent-child |
| Mã đơn vị unique | ✅ Đã có | `code` field được validate unique |
| Import Excel danh sách đơn vị | ❌ Chưa có | Chưa có chức năng import từ Excel/CSV |
| Export Excel danh sách đơn vị | ❌ Chưa có | Chưa có chức năng export |

### 2.3. Quản lý nhóm đối tượng (TargetGroup)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| CRUD nhóm đối tượng | ✅ Đã có | API đầy đủ trong `analytics/views.py` (lines 90-337) |
| Gán biểu mẫu (forms) cho nhóm | ✅ Đã có | `TargetGroup.forms` là JSONField chứa list mã biểu mẫu |
| Icon và mô tả cho từng nhóm | ✅ Đã có | `ICON_CHOICES` với 7 icon khác nhau, có `description` field |
| Kích hoạt/vô hiệu hóa nhóm | ✅ Đã có | `is_active` boolean field |

### 2.4. Quản lý biểu mẫu (Survey Form)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Tạo biểu mẫu với tiêu đề, mô tả, thời gian | ✅ Đã có | `Survey` model đầy đủ |
| Mã biểu mẫu tự động (BM-001, BM-002,...) | ✅ Đã có | `save()` method tự sinh code |
| Builder tạo câu hỏi nhiều loại | ✅ Đã có | Hỗ trợ: short-text, long-text, single-choice, multi-choice, rating-grid, data-table |
| Sections (A, B, C...) | ✅ Đã có | `Section` model với code, title, order |
| Nhân bản biểu mẫu | ✅ Đã có | API `duplicate_survey` trong `survey/views.py` |
| Xuất JSON biểu mẫu | ✅ Đã có | API `survey_form_detail_api` trả về JSON chi tiết |
| Phát hành khảo sát | ✅ Đã có | Chuyển status từ draft → active |
| Xóa biểu mẫu (archived nếu có response) | ✅ Đã có | API xóa kiểm tra response và tự động archived |
| Danh mục (category) cho biểu mẫu | ✅ Đã có | `SurveyCategory` model |
| Logic điều kiện (jump logic) | ❌ Chưa có | Mới có `condition_logic` JSONField nhưng chưa implement xử lý |
| Import Word/Excel câu hỏi | ❌ Chưa có | Chưa có chức năng import từ file |

### 2.5. Gán biểu mẫu cho nhóm (Assignment)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Gán một hoặc nhiều biểu mẫu cho nhóm đối tượng | ✅ Đã có | API `assignment_create_api` |
| Gỡ biểu mẫu khỏi nhóm | ✅ Đã có | API `assignment_remove_form_api` |
| Kích hoạt/vô hiệu hóa gán | ✅ Đã có | API `assignment_update_api` |

### 2.6. Cổng khảo sát (Public Survey Portal)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Làm khảo sát trực tuyến qua website | ✅ Đã có | Template `survey_public.html` |
| Tự động lưu draft khi làm dở | ✅ Đã có | `Response.status='draft'` + `SurveyProgress` tracking |
| Theo dõi tiến độ từng section | ✅ Đã có | `Response.section_progress` JSONField |
| Xác thực quyền truy cập (phải đăng nhập) | ✅ Đã có | `@login_required` decorator |
| Tự động điền thông tin user vào phiếu | ✅ Đã có | `SurveyParticipant` tự động tạo từ User info |
| Chống trả lời nhiều lần (mỗi user 1 response) | ✅ Đã có | Check `SurveyParticipant + SurveyProgress` |
| Ứng dụng di động (mobile app) | ❌ Chưa có | Chưa có native app |
| Khảo sát offline | ❌ Chưa có | Chưa hỗ trợ chế độ offline |

### 2.7. Dashboard Admin

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Tổng quan thống kê | ✅ Đã có | `dashboard_home` view |
| Theo dõi tiến độ đơn vị | ✅ Đã có | `survey_unit_dashboard_api` + `organization_with_status_api` |
| Phân loại Sở/Phường | ✅ Đã có | Tách riêng department list và ward list |
| Progress bar tiến độ | ✅ Đã có | Tính `progress_percent` + hiển thị dạng done/total |
| Biểu đồ chi tiết | ❌ Chưa có | Chưa có chart/biểu đồ trực quan |
| Lọc theo thời gian | ❌ Chưa có | Chưa có filter theo ngày/quý/năm trên dashboard |

### 2.8. Dashboard User

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Danh sách biểu mẫu được gán | ✅ Đã có | `survey_dashboard` view hiển thị assigned forms |
| Theo dõi tiến độ từng bài | ✅ Đã có | `SurveyProgress` model |
| Bắt đầu/Tiếp tục/Làm lại khảo sát | ✅ Đã có | `survey_dashboard_continue` view |
| Xuất PDF phiếu đã hoàn thành | ✅ Đã có | `export_response_pdf` view (ReportLab) |
| Thống kê tổng quan | ✅ Đã có | `overall_progress` + completed/in_progress/not_started counts |
| Thông báo khi có khảo sát mới | ❌ Chưa có | Chưa có notification/email khi có survey mới |

### 2.9. Tổng hợp và báo cáo

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Tổng hợp tiến độ theo đơn vị (SurveyUnitStatus) | ✅ Đã có | Model + API cập nhật tự động |
| Tính số lượng khảo sát đã hoàn thành | ✅ Đã có | `completed_count`, `total_assignees` |
| Hiển thị dạng done/total (VD: 3/4) | ✅ Đã có | `progress_display` field |
| API tổng hợp theo cấp độ (Sở/Phường) | ✅ Đã có | `organization_with_status_api` |
| Xuất PDF phiếu trả lời cá nhân | ✅ Đã có | `export_response_pdf` |
| Xuất báo cáo tổng hợp Excel/PDF | ❌ Chưa có | Chưa có export tổng hợp nhiều phiếu |
| Phân tích dữ liệu tự động | ❌ Chưa có | Chưa có analytics tự động |
| So sánh giữa các đơn vị, các năm | ❌ Chưa có | Chưa có giao diện so sánh |

### 2.10. Cấu hình chấm điểm (ScoringConfig)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Tạo cấu hình chấm điểm | ✅ Đã có | `ScoringConfig` model với `criteria_mapping` JSON |
| Ánh xạ điểm (criteria_mapping JSON) | ✅ Đã có | JSONField lưu mapping câu hỏi ↔ điểm |
| Tự động tính điểm từ response | ❌ Chưa có | Chưa có engine tính điểm tự động |

### 2.11. Kết quả tổng hợp (AggregatedResult)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| Lưu kết quả theo cấp độ | ✅ Đã có | 6 levels: city/department/district/ward/unit/group |
| Tính điểm trung bình | ✅ Đã có | `average_score` field |
| Lưu theo năm, quý | ✅ Đã có | `year`, `quarter` fields |
| Giao diện hiển thị kết quả | ❌ Chưa có | Chưa có template/UI để xem aggregated results |

### 2.12. Báo cáo so sánh (ComparisonReport)

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|-----------|------------------|
| So sánh giữa đơn vị, giữa năm, giữa nhóm | ✅ Đã có | `comparison_type` field với 3 options |
| Lưu dữ liệu báo cáo (JSON) | ✅ Đã có | `report_data` JSONField |
| Giao diện xem báo cáo | ❌ Chưa có | Chưa có template/UI cho so sánh |

---

## 3. Đánh giá yêu cầu 3.3: Công cụ thu thập, tổng hợp và phân tích dữ liệu khảo sát

### 3.1. A. Mô tả công cụ

| Yêu cầu | Trạng thái | Ghi chú chi tiết |
|---------|------------|------------------|
| Hỗ trợ khảo sát trực tuyến qua website | ✅ Đã có | Template `survey_public.html`, đầy đủ chức năng làm survey |
| Hỗ trợ khảo sát qua ứng dụng di động | ❌ Chưa có | Chưa có mobile app (React Native/Flutter) |
| Kết hợp khảo sát trực tiếp qua thiết bị điện tử | ⚠️ Cơ bản | Web responsive, có thể dùng trên tablet/điện thoại |
| Thay thế phiếu giấy truyền thống | ✅ Có | Hoàn toàn trực tuyến, lưu database |
| Giảm thiểu nhập liệu thủ công | ✅ Có | Tự động mapping User→Participant→Response |
| Cơ chế xác thực | ✅ Có | 2 cổng đăng nhập (Admin + User) |
| Chống gian lận (trả lời hộ, trả lời nhiều lần) | ⚠️ Cơ bản | Chặn bằng User + Session. Chưa có IP/Device fingerprint |

### 3.2. B. Chức năng thu thập, tổng hợp dữ liệu khảo sát

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|------------|------------------|
| Quản lý danh mục khảo sát | ✅ Có | `SurveyCategory` CRUD |
| Quản lý biểu mẫu khảo sát | ✅ Có | Survey builder với sections, questions đa dạng |
| Thu thập thông tin khảo sát | ✅ Có | Response model với answers JSON, tracking IP, device |
| Theo dõi tiến độ khảo sát | ✅ Có | `SurveyProgress` + `SurveyUnitStatus` |
| Tổng hợp và phân tích dữ liệu | ⚠️ Cơ bản | Đã có tổng hợp đơn vị, chưa có phân tích chi tiết từng câu hỏi |
| Dashboard khảo sát | ⚠️ Cơ bản | Có dashboard đơn vị (Sở/Phường), chưa có dashboard phân tích dữ liệu |
| Xuất báo cáo và dữ liệu | ⚠️ Cơ bản | Chỉ có xuất PDF cá nhân, chưa có xuất tổng hợp Excel/PDF |
| Quản trị và bảo mật | ✅ Có | Phân quyền admin/user, decorator kiểm tra role |

### 3.3. C. Xử lý, phân tích và báo cáo kết quả

| Chức năng | Trạng thái | Ghi chú chi tiết |
|-----------|------------|------------------|
| Tự động tổng hợp kết quả | ⚠️ Cơ bản | `organization_with_status_api` tự động tính, chưa tổng hợp chi tiết câu hỏi |
| Làm sạch dữ liệu | ⚠️ Cơ bản | Có `is_cleaned`, `is_duplicate` flags. Chưa có auto-clean |
| Tính toán theo bộ chỉ số CCHC | ❌ Chưa có | `ScoringConfig` đã có model nhưng chưa tích hợp vào response pipeline |
| Phân tích theo cấp độ (TP, Sở/Ngành, Xã/Phường) | ⚠️ Cơ bản | `AggregatedResult` đã có model, chưa có giao diện |
| So sánh giữa các đơn vị | ⚠️ Cơ bản | `ComparisonReport` đã có model, chưa có giao diện |
| So sánh giữa các năm | ⚠️ Cơ bản | Có year field, chưa có giao diện |
| So sánh giữa các nhóm đối tượng | ❌ Chưa có | Chưa có chức năng so sánh cross-group |

### 3.4. D. Kết quả mong đợi

| Kết quả | Trạng thái | Ghi chú chi tiết |
|---------|------------|------------------|
| Bộ dữ liệu khảo sát chuẩn hóa theo từng nhóm | ⚠️ Cơ bản | Dữ liệu có trong DB nhưng chưa xuất được thành file |
| Báo cáo thống kê hiện trạng CCHC | ❌ Chưa có | Chưa có báo cáo tổng hợp |
| Báo cáo đánh giá hiện trạng ứng dụng CNTT | ❌ Chưa có | Chưa có |
| Danh sách khó khăn, bất cập | ❌ Chưa có | Chưa có cơ chế trích xuất từ câu trả lời |
| Danh mục yêu cầu nghiệp vụ | ❌ Chưa có | Chưa tổng hợp |
| Danh mục yêu cầu chức năng | ❌ Chưa có | Chưa tổng hợp |
| Danh mục yêu cầu kỹ thuật | ❌ Chưa có | Chưa tổng hợp |
| Cơ sở dữ liệu AS-IS, TO-BE | ❌ Chưa có | Chưa có |
| Tài liệu BRS | ❌ Chưa có | Chưa có |
| Đề xuất phương án đầu tư | ❌ Chưa có | Chưa có |

---

## 4. Phân tích khoảng trống (Gap Analysis)

### 4.1. Tổng quan tỷ lệ đáp ứng

| Mức độ | Số lượng | Tỷ lệ |
|--------|---------|-------|
| ✅ Đã có đầy đủ | 23 | 48.9% |
| ⚠️ Cơ bản (cần cải thiện) | 13 | 27.7% |
| ❌ Chưa có | 11 | 23.4% |
| **Tổng cộng** | **47** | **100%** |

### 4.2. Các chức năng thiếu - Phân tích ưu tiên

| # | Chức năng thiếu | Mức ảnh hưởng | Ưu tiên | Lý do |
|---|-----------------|--------------|---------|-------|
| 1 | **Quên mật khẩu / Reset mật khẩu** | Cao | P0 - Ngay | Người dùng không thể tự khôi phục tài khoản |
| 2 | **Xuất báo cáo tổng hợp Excel/PDF** | Cao | P0 - Ngay | Yêu cầu cốt lõi của nghiệp vụ báo cáo CCHC |
| 3 | **Giao diện hiển thị kết quả tổng hợp (AggregatedResult)** | Cao | P0 - Ngay | Admin cần xem được kết quả chấm điểm |
| 4 | **Giao diện xem báo cáo so sánh (ComparisonReport)** | Cao | P0 - Ngay | Nghiệp vụ so sánh giữa các đơn vị |
| 5 | **Tự động tính điểm từ ScoringConfig** | Cao | P0 - Ngay | Cốt lõi cho tính năng chấm điểm CCHC |
| 6 | **Logic điều kiện (jump/skip logic)** | Trung bình | P1 - Ngắn hạn | Tăng tính linh hoạt cho biểu mẫu |
| 7 | **Biểu đồ chi tiết trên dashboard** | Trung bình | P1 - Ngắn hạn | Trực quan hóa dữ liệu |
| 8 | **Lọc theo thời gian trên dashboard** | Trung bình | P1 - Ngắn hạn | Quản lý theo quý/năm |
| 9 | **Import/Export Excel đơn vị** | Thấp | P1 - Ngắn hạn | Tiện ích nhập liệu |
| 10 | **Import Word/Excel câu hỏi** | Trung bình | P1 - Ngắn hạn | Tăng năng suất tạo biểu mẫu |
| 11 | **Xác thực 2FA** | Trung bình | P1 - Ngắn hạn | Bảo mật tài khoản admin |
| 12 | **Thông báo khi có khảo sát mới** | Trung bình | P1 - Ngắn hạn | Tăng tương tác người dùng |
| 13 | **Phân tích dữ liệu tự động** | Cao | P2 - Dài hạn | Yêu cầu nâng cao |
| 14 | **Chống gian lận nâng cao (IP/Device fingerprint)** | Trung bình | P2 - Dài hạn | Cải thiện bảo mật |
| 15 | **So sánh giữa các nhóm đối tượng** | Trung bình | P2 - Dài hạn | Yêu cầu nâng cao |
| 16 | **Ứng dụng di động** | Thấp | P3 - Dài hạn | Mở rộng kênh tiếp cận |
| 17 | **Khảo sát offline** | Thấp | P3 - Dài hạn | Yêu cầu đặc thù |
| 18 | **SSO/Đăng nhập tập trung** | Thấp | P3 - Dài hạn | Tích hợp hệ thống khác |

### 4.3. Khoảng trống kiến trúc

1. **Thiếu module xác thực (auth):** Không có forgot password, 2FA, SSO
2. **Thiếu module báo cáo (reporting):** Chưa có export engine tổng hợp
3. **Thiếu module phân tích (analytics engine):** ScoringConfig chưa được tích hợp với response pipeline
4. **Thiếu giao diện hiển thị (visualization):** AggregatedResult, ComparisonReport chưa có UI
5. **Thiếu notification:** Không email/SMS notification

---

## 5. Đề xuất cải thiện theo giai đoạn

### 5.1. Giai đoạn 1: Ngay lập tức (Critical) - 2-4 tuần

Các chức năng cần thiết để vận hành hệ thống ổn định:

| STT | Chức năng | Mô tả | File cần tạo/sửa | Độ phức tạp |
|-----|----------|-------|-----------------|-------------|
| 1 | **Quên mật khẩu** | Form yêu cầu reset, gửi email link, đặt lại mật khẩu | `apps/accounts/views.py`, `templates/accounts/forgot_password.html`, `templates/accounts/reset_password.html` | Trung bình |
| 2 | **API tính điểm từ ScoringConfig** | Engine tự động đọc criteria_mapping, tính điểm từ answers JSON | `apps/analytics/views.py` (scoring engine), `apps/survey/utils.py` | Trung bình |
| 3 | **Giao diện AggregatedResult** | Trang hiển thị kết quả tổng hợp theo cấp độ, có filter năm/quý | `apps/analytics/templates/analytics/aggregated_results.html`, `apps/analytics/views.py` | Trung bình |
| 4 | **Giao diện ComparisonReport** | Trang so sánh đơn vị/năm/nhóm, hiển thị bảng so sánh | `apps/analytics/templates/analytics/comparison_report.html`, `apps/analytics/views.py` | Trung bình |
| 5 | **Xuất báo cáo tổng hợp Excel** | Export danh sách đơn vị kèm tiến độ ra Excel (openpyxl) | `apps/analytics/views.py` (export function), thêm `openpyxl` vào requirements | Trung bình |

### 5.2. Giai đoạn 2: Ngắn hạn (Short-term) - 1-2 tháng

| STT | Chức năng | Mô tả | File cần tạo/sửa | Độ phức tạp |
|-----|----------|-------|-----------------|-------------|
| 6 | **Logic điều kiện (jump logic)** | Cho phép câu hỏi có điều kiện hiển thị dựa trên câu trả lời trước | `apps/survey/views.py`, `apps/survey/templates/survey/survey_public.html` | Cao |
| 7 | **Import/Export Excel đơn vị** | Upload Excel để import hàng loạt đơn vị, export danh sách | `apps/analytics/views.py`, thêm xử lý file upload | Thấp |
| 8 | **Import Word/Excel câu hỏi** | Import câu hỏi từ file Word/Excel vào builder | `apps/survey/views.py`, thêm template import | Trung bình |
| 9 | **Biểu đồ dashboard Admin** | Thêm biểu đồ (Chart.js) cho dashboard tổng quan | `apps/analytics/templates/analytics/dashboard.html`, thêm Chart.js | Trung bình |
| 10 | **Lọc thời gian trên dashboard** | Thêm filter ngày/quý/năm cho dashboard và tổng hợp | `apps/analytics/views.py`, cập nhật API filter | Thấp |
| 11 | **Xác thực 2FA** | Mã OTP qua email/SMS cho tài khoản admin | `apps/accounts/views.py`, thêm OTP library | Trung bình |
| 12 | **Thông báo khảo sát mới** | Gửi email thông báo khi có survey mới cho user trong target group | `apps/accounts/utils.py`, thêm email notification | Trung bình |
| 13 | **Chống gian lận IP/Device** | Ghi log IP + device fingerprint, chặn nếu phát hiện trùng | `apps/survey/views.py`, middleware | Thấp |

### 5.3. Giai đoạn 3: Dài hạn (Long-term) - 3-6 tháng

| STT | Chức năng | Mô tả | Độ phức tạp |
|-----|----------|-------|-------------|
| 14 | **Phân tích dữ liệu tự động** | Hệ thống phân tích câu trả lời dạng text (NLP), thống kê chi tiết từng câu hỏi | Cao |
| 15 | **So sánh giữa các nhóm đối tượng** | Cross-group analysis để so sánh kết quả giữa các nhóm | Trung bình |
| 16 | **Dashboard phân tích nâng cao** | Dashboard với nhiều loại biểu đồ, drill-down từ tổng thể đến chi tiết | Cao |
| 17 | **Ứng dụng di động (PWA/Mobile App)** | Xây dựng PWA hoặc React Native app cho khảo sát di động | Cao |
| 18 | **Khảo sát offline** | Cho phép tải survey, làm offline, sync khi có mạng | Cao |
| 19 | **SSO/LDAP Integration** | Đăng nhập tập trung qua LDAP/Azure AD/Google Workspace | Trung bình |
| 20 | **Tài liệu BRS và AS-IS/TO-BE** | Xây dựng tài liệu phân tích nghiệp vụ đầy đủ | Trung bình |

---

## 6. Danh sách file/template cần tạo thêm

### 6.1. Giai đoạn 1

| File | Chức năng | Mô tả |
|------|----------|-------|
| `apps/accounts/templates/accounts/forgot_password.html` | Quên mật khẩu | Form yêu cầu reset mật khẩu qua email |
| `apps/accounts/templates/accounts/reset_password.html` | Đặt lại mật khẩu | Form đặt mật khẩu mới sau khi xác thực email |
| `apps/accounts/templates/accounts/password_reset_email.html` | Email reset | Template email chứa link reset password |
| `apps/analytics/templates/analytics/aggregated_results.html` | Kết quả tổng hợp | Trang hiển thị bảng kết quả tổng hợp theo cấp độ, năm, quý |
| `apps/analytics/templates/analytics/comparison_report.html` | Báo cáo so sánh | Trang hiển thị so sánh giữa đơn vị/năm/nhóm |
| `apps/analytics/templates/analytics/export_preview.html` | Xuất báo cáo | Trang preview và tùy chọn xuất báo cáo tổng hợp |
| `apps/survey/utils.py` (mở rộng) | Scoring engine | Thêm hàm tính điểm tự động từ ScoringConfig |

### 6.2. Giai đoạn 2

| File | Chức năng | Mô tả |
|------|----------|-------|
| `apps/survey/templates/survey/import_questions.html` | Import câu hỏi | Trang upload file Word/Excel để import câu hỏi |
| `apps/analytics/templates/analytics/import_organizations.html` | Import đơn vị | Trang upload Excel để import đơn vị hàng loạt |
| `apps/accounts/utils.py` (mới) | Email notification | Module gửi email thông báo survey mới |
| `apps/accounts/services.py` (mới) | 2FA service | Module xác thực 2FA (OTP) |
| `apps/survey/middleware.py` (mới) | Anti-fraud middleware | Middleware chống gian lận IP/device |

### 6.3. Giai đoạn 3

| File | Chức năng | Mô tả |
|------|----------|-------|
| `mobile/` (thư mục mới) | Ứng dụng di động | Dự án React Native hoặc Flutter |
| `apps/analytics/services/` (thư mục mới) | Analytics engine | Module phân tích dữ liệu tự động |
| `apps/analytics/templates/analytics/advanced_dashboard.html` | Dashboard nâng cao | Dashboard với Chart.js/Recharts |
| `apps/accounts/sso.py` (mới) | SSO integration | Module tích hợp LDAP/OAuth |
| `templates/emails/` (thư mục mới) | Email templates | Thư mục chứa các template email |

---

## 7. Đánh giá tổng thể

### 7.1. Mức độ hoàn thiện

```
Tổng thể hệ thống: 60% hoàn thiện
├── Core (Quản lý tài khoản, đơn vị, nhóm):   85% ✅
├── Survey Builder (Biểu mẫu, câu hỏi):       80% ✅
├── Cổng khảo sát (User):                     75% ✅
├── Dashboard & Thống kê:                     45% ⚠️
├── Báo cáo & Phân tích:                      20% ❌
└── Bảo mật & Xác thực:                       40% ⚠️
```

### 7.2. Điểm mạnh

1. **Kiến trúc rõ ràng:** 3 phân tách rõ ràng (accounts/analytics/survey), dễ bảo trì
2. **Phân quyền linh hoạt:** Admin/Manager/Staff và nhóm đối tượng riêng biệt
3. **Builder mạnh mẽ:** Nhiều loại câu hỏi, sections, categories
4. **Tự động hóa tốt:** Auto code, auto mapping user→participant, auto draft lưu
5. **Hỗ trợ font Tiếng Việt:** Export PDF có Unicode font fallback
6. **API đầy đủ:** Hầu hết chức năng đều có REST API endpoints
7. **Cấu trúc đơn vị đa cấp:** 5 cấp hierarchy, phù hợp với mô hình hành chính

### 7.3. Điểm yếu

1. **Thiếu báo cáo tổng hợp:** Chưa thể xuất báo cáo Excel/PDF tổng thể
2. **Thiếu phân tích dữ liệu:** Chưa có cơ chế phân tích câu trả lời chi tiết
3. **Scoring chưa tích hợp:** ScoringConfig tồn tại riêng rẽ, chưa kết nối với response
4. **Không có forgot password:** Người dùng không thể tự reset mật khẩu
5. **Giao diện báo cáo còn thiếu:** AggregatedResult, ComparisonReport chỉ là model
6. **Thiếu notification:** Không có email/SMS thông báo
7. **Frontend chưa tối ưu:** Sử dụng vanilla JS, chưa có framework frontend

### 7.4. Rủi ro

| Rủi ro | Mức độ | Khả năng xảy ra | Giảm thiểu |
|--------|--------|----------------|------------|
| Mất dữ liệu nếu không có backup tự động | Cao | Trung bình | Cấu hình backup database định kỳ |
| SQLite không phù hợp production | Cao | Trung bình | Chuyển sang PostgreSQL, đã có config sẵn |
| Bảo mật yếu (không 2FA, không forgot password) | Cao | Thấp | Triển khai Giai đoạn 1 ngay |
| Hiệu năng khi nhiều user truy cập cùng lúc | Trung bình | Thấp | Tối ưu query, thêm caching (Redis) |
| Lỗi font khi xuất PDF trên server khác | Trung bình | Trung bình | Bundle font DejaVu Sans vào project |
| Thiếu kiểm thử tự động | Cao | Cao | Viết unit test cho models và APIs |

### 7.5. Khuyến nghị

1. **Ưu tiên Giai đoạn 1 ngay lập tức:** 
   - Triển khai forgot password (rủi ro bảo mật)
   - Tích hợp scoring engine để có thể tính điểm
   - Xây dựng giao diện kết quả tổng hợp và báo cáo so sánh
   - Thêm chức năng xuất Excel tổng hợp

2. **Trong 1 tháng tới:**
   - Chuyển từ SQLite sang PostgreSQL
   - Cấu hình backup tự động
   - Viết unit test cho các API chính
   - Triển khai CI/CD

3. **Trong 3 tháng tới:**
   - Hoàn thiện Giai đoạn 2 (logic điều kiện, import/export, biểu đồ, 2FA)
   - Xây dựng tài liệu BRS và hướng dẫn sử dụng
   - Đào tạo người dùng

4. **Dài hạn (6-12 tháng):**
   - Mobile app + offline survey
   - Phân tích dữ liệu tự động
   - SSO/LDAP

---

## 8. Phụ lục: Kiến trúc hệ thống

### 8.1. Cấu trúc thư mục

```
Survey/
├── apps/
│   ├── accounts/              # Quản lý người dùng & tổ chức
│   │   ├── models.py           # User, Organization
│   │   ├── views.py            # Login/Logout, survey dashboard, PDF export
│   │   ├── urls.py             # URL routing
│   │   └── templates/accounts/ # Login, dashboard templates
│   │
│   ├── analytics/              # Quản lý admin & tổng hợp
│   │   ├── models.py           # TargetGroup, ScoringConfig, AggregatedResult, ComparisonReport
│   │   ├── views.py            # Admin APIs (accounts, groups, surveys, organizations)
│   │   ├── serializers.py      # REST serializers
│   │   └── templates/analytics/ # Admin dashboard templates
│   │
│   └── survey/                 # Quản lý khảo sát
│       ├── models.py           # Survey, Section, Question, Response, SurveyProgress, SurveyUnitStatus
│       ├── views.py            # Survey APIs, public survey portal
│       ├── serializers.py      # REST serializers
│       └── templates/survey/   # Survey builder & public portal templates
│
├── config/                     # Django project configuration
│   ├── settings.py
│   └── urls.py
│
├── static/                     # Static files (CSS, JS, images)
│
├── templates/                  # Base templates
│   ├── base.html
│   └── components/
│
└── docs/                       # Documentation
    └── PROJECT_REPORT.md       # This file
```

### 8.2. Mô hình dữ liệu chính

```
User ──── Organization (5 cấp hierarchy)
  │
  ├── TargetGroup (M2M)
  │     └── forms (JSON: [BM-001, BM-002, ...])
  │
  └── SurveyParticipant
        └── SurveyProgress (per form_code)
              └── Response (answers JSON)
                    └── Survey (code, sections, questions)

Survey ──── Section ──── Question
  │                         └── options JSON, condition_logic JSON
  └── SurveyUnitStatus (per organization)
  
ScoringConfig ── Survey
  └── criteria_mapping JSON
  
AggregatedResult (per level/year/quarter)
ComparisonReport (per type: units/years/groups)
```

### 8.3. API Endpoints chính

| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET/POST | `/accounts/login/` | Admin login |
| GET/POST | `/accounts/user-login/` | User login |
| GET | `/accounts/survey-dashboard/` | User dashboard |
| POST | `/accounts/logout/` | Logout |
| GET/POST/PUT/DELETE | `/api/analytics/target-groups/` | TargetGroup CRUD |
| GET/POST/PUT/DELETE | `/api/analytics/survey-forms/` | Survey CRUD |
| GET/POST/PUT/DELETE | `/api/analytics/accounts/` | Account management |
| GET/POST/PUT/DELETE | `/api/analytics/organizations/` | Organization CRUD |
| GET/POST/PUT/DELETE | `/api/analytics/assignments/` | Assignment CRUD |
| GET | `/api/analytics/survey-dashboard/{id}/` | Dashboard API |
| GET | `/api/analytics/organizations/status/` | Organization status |
| GET/POST | `/api/survey/...` | Survey CRUD APIs |
| GET | `/survey/public/{id}/` | Public survey portal |
| GET | `/export/response/{id}/pdf/` | Export PDF |

---

*Báo cáo được tạo ngày 05/07/2026. Phiên bản 1.0.*
*Dựa trên mã nguồn tại commit 3cba5d799ed5db0d7e0fbfa1e8b2871c5b43712f*