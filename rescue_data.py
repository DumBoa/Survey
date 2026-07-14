import os
import sys

# Khởi tạo Django (bạn cần chạy script này tại thư mục chứa file manage.py)
# Ví dụ: python scripts/rescue_data.py
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.survey.models import Response, Question

def rescue_survey_data(survey_id=21):
    print(f"--- BẮT ĐẦU CỨU DỮ LIỆU SURVEY {survey_id} ---")
    
    # 1. Lấy danh sách ID câu hỏi "SỐNG" (hiện tại đang có trong hệ thống)
    # Loại bỏ các component không chứa dữ liệu nhập (như tiêu đề, xuống dòng...)
    active_questions = list(Question.objects.filter(section__survey_id=survey_id).order_by('order', 'id'))
    active_ids = [str(q.id) for q in active_questions if q.component_type not in ['title', 'section_break', 'paragraph']]
    
    if not active_ids:
        print(f"Không tìm thấy câu hỏi nào hợp lệ cho Survey {survey_id}.")
        return

    # 2. Lấy tất cả các phiếu trả lời của Survey này
    responses = Response.objects.filter(survey_id=survey_id)
    
    fixed_count = 0
    for r in responses:
        answers = r.answers
        if not answers:
            continue
            
        old_keys = list(answers.keys())
        
        # Lọc ra các ID "MỒ CÔI" (những ID dạng số không nằm trong danh sách đang sống)
        orphan_keys = [k for k in old_keys if k.isdigit() and k not in active_ids]
        
        if not orphan_keys:
            continue # Phiếu này bình thường, không bị lỗi
            
        print(f"\n[+] Phát hiện phiếu #{r.id} bị mồ côi {len(orphan_keys)} câu trả lời.")
        
        # Sắp xếp các key cũ từ bé đến lớn. 
        # (Vì Admin tạo lại các câu theo thứ tự, ID cũ tăng dần sẽ map chuẩn với ID mới tăng dần)
        orphan_keys.sort(key=lambda x: int(x))
        
        new_answers = {}
        for key in old_keys:
            if key in orphan_keys:
                idx = orphan_keys.index(key)
                # Map 1-1 theo vị trí (index)
                if idx < len(active_ids):
                    new_key = active_ids[idx]
                    new_answers[new_key] = answers[key]
                    print(f"  --> Map dữ liệu: ID cũ [{key}] chuyển sang ID mới [{new_key}]")
                else:
                    # Nếu dư thừa không map được thì giữ nguyên
                    new_answers[key] = answers[key]
            else:
                new_answers[key] = answers[key]
                
        # LƯU Ý: Đã mở comment để ghi đè vào DB
        r.answers = new_answers
        r.save(update_fields=['answers'])
        
        fixed_count += 1
        
    print(f"\n--- HOÀN TẤT: Đã quét và map xong cho {fixed_count} phiếu trả lời! ---")
    print("Mở file code, bỏ comment dòng r.save() để dữ liệu thực sự được ghi vào Database.")

def rescue_all_surveys():
    surveys = Question.objects.values_list('section__survey_id', flat=True).distinct()
    for sid in surveys:
        if sid:
            rescue_survey_data(survey_id=sid)

if __name__ == '__main__':
    # Quét và cứu toàn bộ các Survey có trong Database
    rescue_all_surveys()
