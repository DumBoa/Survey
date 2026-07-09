# apps/accounts/middleware.py
class LoginPathMiddleware:
    """
    Middleware ghi nhận đường dẫn đăng nhập vào session.
    Nếu người dùng truy cập /accounts/cchc/ hoặc /accounts/sipas/, 
    lưu login_type và login_url vào session.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # Chỉ xét khi truy cập vào trang login cụ thể
        if path == '/accounts/cchc/' or path == '/accounts/cchc':
            request.session['login_type'] = 'cchc'
            request.session['login_url'] = '/accounts/cchc/'
        elif path == '/accounts/sipas/' or path == '/accounts/sipas':
            request.session['login_type'] = 'sipas'
            request.session['login_url'] = '/accounts/sipas/'
        
        response = self.get_response(request)
        return response
