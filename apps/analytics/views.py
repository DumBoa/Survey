from django.shortcuts import render

def analytics_main_render(request):
    return render(request, 'analytics/analytics_main.html')
