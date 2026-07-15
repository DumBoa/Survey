import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def clean_draft_responses():
    try:
        django.setup()
        from apps.survey.models import Response
        
        # Đếm số lượng bài nháp trước khi xóa
        drafts = Response.objects.filter(status='draft')
        count = drafts.count()
        
        if count == 0:
            print("Không tìm thấy bài làm nào ở trạng thái 'draft'.")
            return
            
        print(f"Đang tiến hành xóa {count} bài làm (Response) có trạng thái 'draft'...")
        
        # Thực hiện xóa
        deleted_count, _ = drafts.delete()
        
        print(f"Thành công! Đã dọn dẹp {deleted_count} bài làm nháp.")
        
    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình dọn dẹp: {e}")

if __name__ == '__main__':
    # Yêu cầu xác nhận trước khi chạy để tránh lỡ tay
    confirm = input("Bạn có chắc chắn muốn xóa tất cả các bài làm đang ở trạng thái nháp (draft) không? (y/n): ")
    if confirm.lower() == 'y':
        clean_draft_responses()
    else:
        print("Đã hủy thao tác.")
