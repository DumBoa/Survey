# apps/accounts/context_processors.py
from django.urls import reverse

def logout_url_processor(request):
    """
    Trả về URL đăng xuất động có kèm theo tham số next 
    để điều hướng về đúng trang (cchc hoặc sipas).
    """
    # Lấy login_url từ session, mặc định là /accounts/cchc/
    login_url = request.session.get('login_url', '/accounts/cchc/')
    
    # Tạo URL logout kèm tham số next
    # Tuy logout_view đã xử lý redirect dựa trên session,
    # nhưng truyền ?next cũng là một cách dự phòng tốt.
    logout_url = reverse('accounts:logout')
    
    return {
        'logout_url': f"{logout_url}?next={login_url}"
    }
