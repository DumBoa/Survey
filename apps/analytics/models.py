from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ScoringConfig(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên bộ chỉ số")
    survey = models.ForeignKey('survey.Survey', on_delete=models.CASCADE, verbose_name="Áp dụng cho khảo sát") # Đã sửa
    criteria_mapping = models.JSONField(verbose_name="Ánh xạ điểm (JSON)")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Đang áp dụng")

    def __str__(self):
        return f"{self.name} ({self.survey.title})"

    class Meta:
        verbose_name = "Cấu hình chấm điểm"
        verbose_name_plural = "Cấu hình chấm điểm"


class AggregatedResult(models.Model):
    LEVEL_CHOICES = [
        ('city', 'Thành phố'),
        ('department', 'Sở/Ngành'),
        ('district', 'Quận/Huyện'),
        ('ward', 'Xã/Phường'),
        ('unit', 'Đơn vị sự nghiệp'),
        ('group', 'Nhóm đối tượng'),
    ]
    survey = models.ForeignKey('survey.Survey', on_delete=models.CASCADE, verbose_name="Khảo sát") # Đã sửa
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Cấp độ phân tích")
    entity_name = models.CharField(max_length=255, verbose_name="Tên thực thể")
    entity_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã thực thể")
    total_responses = models.PositiveIntegerField(default=0, verbose_name="Số phiếu hợp lệ")
    average_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Điểm trung bình")
    raw_data = models.JSONField(default=dict, verbose_name="Dữ liệu chi tiết")
    calculated_at = models.DateTimeField(auto_now=True, verbose_name="Thời gian tính toán")
    
    year = models.PositiveIntegerField(verbose_name="Năm")
    quarter = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(4)], verbose_name="Quý")

    def __str__(self):
        return f"{self.survey.title} - {self.entity_name} ({self.level})"

    class Meta:
        verbose_name = "Kết quả tổng hợp"
        verbose_name_plural = "Kết quả tổng hợp"
        indexes = [
            models.Index(fields=['survey', 'level', 'entity_name']),
        ]
        unique_together = (('survey', 'level', 'entity_name', 'year', 'quarter'),)


class ComparisonReport(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên báo cáo")
    survey = models.ForeignKey('survey.Survey', on_delete=models.CASCADE, verbose_name="Khảo sát gốc") # Đã sửa
    comparison_type = models.CharField(max_length=50, choices=[('units', 'Giữa các đơn vị'), ('years', 'Giữa các năm'), ('groups', 'Giữa nhóm đối tượng')], verbose_name="Kiểu so sánh")
    report_data = models.JSONField(verbose_name="Dữ liệu báo cáo")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    export_file = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name="File xuất (PDF/Excel)")

    def __str__(self):
        return f"{self.name} - {self.generated_at.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Báo cáo so sánh"
        verbose_name_plural = "Báo cáo so sánh"