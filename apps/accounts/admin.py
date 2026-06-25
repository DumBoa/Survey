from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Organization, User

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'parent')
    list_filter = ('level',)
    search_fields = ('name', 'code')

# Cấu hình trang quản lý User (Kế thừa UserAdmin mặc định của Django để có đủ chức năng đổi mật khẩu)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Thêm các trường mới vào danh sách hiển thị
    list_display = ('username', 'email', 'organization', 'is_surveyor', 'is_staff')
    list_filter = ('is_surveyor', 'organization', 'is_staff', 'is_superuser')
    
    # Cấu hình form thêm/sửa User (Thêm các trường mở rộng)
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('organization', 'position', 'phone_number', 'is_surveyor')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('organization', 'position', 'phone_number', 'is_surveyor')}),
    )