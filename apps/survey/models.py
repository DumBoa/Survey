# apps/survey/models.py
from django.db import models
from django.utils import timezone

class SurveyCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Icon")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Danh mục khảo sát"
        verbose_name_plural = "Danh mục khảo sát"


class Survey(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('active', 'Đang hoạt động'),
        ('closed', 'Đã đóng'),
        ('archived', 'Đã lưu trữ'),
    ]
    title = models.CharField(max_length=255, verbose_name="Tiêu đề khảo sát")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug (URL thân thiện)")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    category = models.ForeignKey(SurveyCategory, on_delete=models.SET_NULL, null=True, verbose_name="Danh mục")

    start_date = models.DateTimeField(verbose_name="Ngày bắt đầu")
    end_date = models.DateTimeField(verbose_name="Ngày kết thúc")
    allow_after_deadline = models.BooleanField(default=False, verbose_name="Cho phép trả lời sau hạn?")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    target_groups = models.JSONField(default=list, blank=True, verbose_name="Nhóm đối tượng mục tiêu")
    settings = models.JSONField(default=dict, blank=True, verbose_name="Cài đặt nâng cao")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    code = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Mã biểu mẫu"
    )
    def save(self, *args, **kwargs):
        # Tự động tạo code nếu chưa có
        if not self.code:
            count = Survey.objects.count() + 1
            self.code = f"BM-{str(count).zfill(3)}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Đợt khảo sát"
        verbose_name_plural = "Đợt khảo sát"
        indexes = [models.Index(fields=['slug', 'status'])]


class Section(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='sections',
        verbose_name="Thuộc khảo sát"
    )

    code = models.CharField(
        max_length=10, verbose_name="Mã phần",
        help_text="VD: A, B, C... dùng để hiển thị nhãn 'PHẦN A'"
    )
    title = models.CharField(max_length=255, verbose_name="Tên phần")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả phần")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Icon")

    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.survey.title} - Phần {self.code}: {self.title}"

    class Meta:
        ordering = ['order']
        verbose_name = "Phần khảo sát"
        verbose_name_plural = "Danh sách phần"
        unique_together = ('survey', 'code')


class QuestionType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên loại")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã code")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Icon")
    has_options = models.BooleanField(default=True, verbose_name="Có options?")
    has_validation = models.BooleanField(default=False, verbose_name="Có validation?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Loại câu hỏi"
        verbose_name_plural = "Loại câu hỏi"


class Question(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='questions',
        verbose_name="Thuộc phần"
    )
    component_type = models.CharField(
        max_length=50,
        default='question',
        verbose_name="Loại thành phần",
        help_text="question, title, paragraph, section_break, personal_info"
    )
    title = models.CharField(max_length=500, verbose_name="Tiêu đề câu hỏi")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả/Hướng dẫn")

    question_type = models.ForeignKey(QuestionType, on_delete=models.PROTECT, verbose_name="Loại câu hỏi")

    is_required = models.BooleanField(default=True, verbose_name="Bắt buộc trả lời")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")

    options = models.JSONField(default=list, blank=True, verbose_name="Danh sách lựa chọn (JSON)")
    condition_logic = models.JSONField(default=dict, blank=True, verbose_name="Logic điều kiện")
    config = models.JSONField(default=dict, blank=True, verbose_name="Cấu hình nâng cao")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.section} - Q{self.order}: {self.title[:50]}..."

    class Meta:
        ordering = ['order']
        verbose_name = "Câu hỏi"
        verbose_name_plural = "Danh sách câu hỏi"
        indexes = [
            models.Index(fields=['component_type']),
        ]


class Blocklist(models.Model):
    TYPE_CHOICES = [
        ('ip', 'IP Address'),
        ('email', 'Email'),
        ('device', 'Device ID'),
        ('user', 'User ID'),
    ]
    block_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Loại chặn")
    value = models.CharField(max_length=255, verbose_name="Giá trị bị chặn")
    reason = models.TextField(blank=True, null=True, verbose_name="Lý do chặn")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name="Hết hạn chặn")

    def __str__(self):
        return f"{self.get_block_type_display()}: {self.value}"

    class Meta:
        verbose_name = "Danh sách đen"
        verbose_name_plural = "Danh sách đen"
        unique_together = ('block_type', 'value')


class Response(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('submitted', 'Đã nộp'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses', verbose_name="Khảo sát")

    respondent_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP người trả lời")
    respondent_device_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID thiết bị")
    respondent_email = models.EmailField(blank=True, null=True, verbose_name="Email người trả lời")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User-Agent (Trình duyệt)")

    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Bắt đầu lúc")
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name="Nộp lúc")
    time_taken = models.PositiveIntegerField(default=0, verbose_name="Thời gian làm bài (giây)")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft',
        verbose_name="Trạng thái phiếu"
    )

    answers = models.JSONField(default=dict, verbose_name="Dữ liệu trả lời (JSON)")
    section_progress = models.JSONField(default=dict, blank=True, verbose_name="Tiến độ từng phần (%)")

    is_verified = models.BooleanField(default=False, verbose_name="Đã xác thực")
    verification_token = models.CharField(max_length=64, blank=True, null=True, verbose_name="Token xác thực")

    is_cleaned = models.BooleanField(default=False, verbose_name="Đã làm sạch")
    is_duplicate = models.BooleanField(default=False, verbose_name="Là phiếu trùng")

    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người dùng")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response #{self.id} - {self.survey.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Phiếu trả lời"
        verbose_name_plural = "Phiếu trả lời"
        indexes = [
            models.Index(fields=['survey', 'submitted_at']),
            models.Index(fields=['respondent_ip', 'respondent_device_id']),
            models.Index(fields=['is_cleaned', 'is_duplicate']),
            models.Index(fields=['survey', 'status']),
        ]


# ============================================================
# MỚI: SurveyAssignment - Ánh xạ Nhóm đối tượng ↔ Biểu mẫu
# ============================================================
class SurveyAssignment(models.Model):
    """
    Ánh xạ giữa Nhóm đối tượng và Biểu mẫu khảo sát
    Cho phép admin cấu hình: nhóm nào được làm biểu mẫu nào
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="Khảo sát"
    )
    form_code = models.CharField(
        max_length=20,
        verbose_name="Mã biểu mẫu (BM-03, BM-04, BM-05...)"
    )
    form_name = models.CharField(
        max_length=255,
        verbose_name="Tên biểu mẫu"
    )
    form_description = models.TextField(
        blank=True, null=True,
        verbose_name="Mô tả biểu mẫu"
    )
    target_group_code = models.CharField(
        max_length=50,
        verbose_name="Mã nhóm đối tượng"
    )
    target_group_name = models.CharField(
        max_length=255,
        verbose_name="Tên nhóm đối tượng"
    )
    target_group_description = models.TextField(
        blank=True, null=True,
        verbose_name="Mô tả nhóm đối tượng"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        verbose_name="Phần khảo sát tương ứng"
    )
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.form_code} - {self.target_group_code}"

    class Meta:
        verbose_name = "Phân công khảo sát"
        verbose_name_plural = "Phân công khảo sát"
        unique_together = ('survey', 'form_code', 'target_group_code')
        ordering = ['order']


# ============================================================
# MỚI: SurveyParticipant - Lưu thông tin người tham gia
# ============================================================
class SurveyParticipant(models.Model):
    """
    Lưu thông tin người tham gia khảo sát (từ cổng khảo sát)
    """
    STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('submitted', 'Đã nộp'),
        ('expired', 'Hết hạn'),
        ('cancelled', 'Đã hủy'),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name="Khảo sát"
    )

    # Thông tin từ bước 1 - Xác minh
    agency = models.CharField(max_length=255, verbose_name="Đơn vị công tác")
    target_group_code = models.CharField(max_length=50, verbose_name="Mã nhóm đối tượng")
    target_group_name = models.CharField(max_length=255, verbose_name="Tên nhóm đối tượng")

    # Thông tin từ bước 2 - Cá nhân
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    position = models.CharField(max_length=255, verbose_name="Chức vụ")
    department = models.CharField(max_length=255, verbose_name="Bộ phận công tác")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(verbose_name="Email")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    # Biểu mẫu được gán
    assigned_forms = models.JSONField(default=list, verbose_name="Biểu mẫu được gán")

    # Liên kết với Response - SỬA: dùng related_name khác để tránh xung đột
    response = models.OneToOneField(
        Response,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='participant_info',  # Đổi tên để tránh xung đột
        verbose_name="Phiếu trả lời"
    )

    # Liên kết với User nếu đã đăng nhập
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_participations',
        verbose_name="Người dùng"
    )

    # Thông tin kỹ thuật
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    session_key = models.CharField(max_length=64, blank=True, null=True, verbose_name="Session Key")

    # Trạng thái
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Trạng thái"
    )
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name="Thời gian nộp")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.survey.title}"

    class Meta:
        verbose_name = "Người tham gia khảo sát"
        verbose_name_plural = "Người tham gia khảo sát"
        indexes = [
            models.Index(fields=['survey', 'email']),
            models.Index(fields=['survey', 'session_key']),
            models.Index(fields=['survey', 'target_group_code']),
        ]