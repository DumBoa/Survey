from django.db import models

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

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Đợt khảo sát"
        verbose_name_plural = "Đợt khảo sát"
        indexes = [models.Index(fields=['slug', 'status'])]


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
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions', verbose_name="Thuộc khảo sát")
    
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
        return f"{self.survey.title} - Q{self.order}: {self.title[:50]}..."

    class Meta:
        ordering = ['order']
        verbose_name = "Câu hỏi"
        verbose_name_plural = "Danh sách câu hỏi"


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
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses', verbose_name="Khảo sát")
    
    respondent_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP người trả lời")
    respondent_device_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID thiết bị")
    respondent_email = models.EmailField(blank=True, null=True, verbose_name="Email người trả lời")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User-Agent (Trình duyệt)")
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Bắt đầu lúc")
    submitted_at = models.DateTimeField(auto_now=True, verbose_name="Nộp lúc")
    time_taken = models.PositiveIntegerField(default=0, verbose_name="Thời gian làm bài (giây)")
    
    answers = models.JSONField(verbose_name="Dữ liệu trả lời (JSON)")
    
    is_verified = models.BooleanField(default=False, verbose_name="Đã xác thực")
    verification_token = models.CharField(max_length=64, blank=True, null=True, verbose_name="Token xác thực")
    
    is_cleaned = models.BooleanField(default=False, verbose_name="Đã làm sạch")
    is_duplicate = models.BooleanField(default=False, verbose_name="Là phiếu trùng")
    
    # Đã sửa thành 'accounts.User'
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người dùng")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response #{self.id} - {self.survey.title}"

    class Meta:
        verbose_name = "Phiếu trả lời"
        verbose_name_plural = "Phiếu trả lời"
        indexes = [
            models.Index(fields=['survey', 'submitted_at']),
            models.Index(fields=['respondent_ip', 'respondent_device_id']),
            models.Index(fields=['is_cleaned', 'is_duplicate']),
        ]