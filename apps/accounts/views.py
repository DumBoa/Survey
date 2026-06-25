# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt  # Thêm import này
from django.contrib.auth.decorators import login_required
import json

def accounts_main_render(request):
    return render(request, 'accounts/accounts_main.html')

def get_user_role_from_db(user):
    return 'admin'

def get_role_display_name(role):
    return 'Quản trị viên'

@require_http_methods(["GET", "POST"])
@csrf_exempt  # Thêm decorator này để tạm thời bỏ qua CSRF
def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/survey/survey-edit/')
        return render(request, 'accounts/login.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)
        except:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ!'
            }, status=400)
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng không để trống thông tin!'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if not remember:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            
            return JsonResponse({
                'success': True,
                'message': 'Đăng nhập thành công!',
                'redirect_url': '/survey/survey-edit/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Sai tên đăng nhập hoặc mật khẩu!'
            }, status=401)