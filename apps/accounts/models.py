# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    LEVEL_CHOICES = [
        ('city', 'Thành phố'),
        ('department', 'Sở/Ngành'),
        ('district', 'Quận/Huyện'),
        ('ward', 'Xã/Phường'),
        ('unit', 'Đơn vị sự nghiệp'),
    ]
    name = models.CharField(max_length=255, verbose_name="Tên đơn vị")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã đơn vị")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Cấp độ")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name="Đơn vị cấp trên")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")

    def __str__(self):
        return f"[{self.code}] {self.name}"

    class Meta:
        verbose_name = "Tổ chức/Đơn vị"
        verbose_name_plural = "Tổ chức/Đơn vị"


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Đơn vị công tác")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chức vụ")
    is_surveyor = models.BooleanField(default=False, verbose_name="Là điều tra viên")
    last_active_at = models.DateTimeField(auto_now=True, verbose_name="Lần hoạt động cuối")
    
    # THÊM TRƯỜNG NÀY - Liên kết user với nhóm đối tượng
    target_groups = models.ManyToManyField(
        'analytics.TargetGroup',
        blank=True,
        related_name='users',
        verbose_name="Nhóm đối tượng"
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} - {self.organization.name if self.organization else 'Chưa có đơn vị'}"

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"