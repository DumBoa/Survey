import os
import sys
import re
import json

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.survey.models import Response, Question

def fix_all_surveys():
    print("--- BẮT ĐẦU FIX DỮ LIỆU TỪ FILE BACKUP ---")
    
    if not os.path.exists('sipas_backup.sql'):
        print("LỖI: Không tìm thấy file sipas_backup.sql. Hãy copy file này vào cùng thư mục.")
        return

    with open('sipas_backup.sql', encoding='utf-8') as f:
        data = f.read()
    
    block_match = re.search(r'COPY public\.survey_response .*?FROM stdin;\n(.*?)\n\\\.', data, re.DOTALL)
    if not block_match:
        print("Không tìm thấy block COPY public.survey_response trong backup!")
        return
        
    lines = block_match.group(1).strip().split('\n')
    
    # Gom nhóm backup theo survey_id
    backup_by_survey = {}
    for line in lines:
        parts = line.split('\t')
        if len(parts) > 15:
            resp_id = int(parts[0])
            survey_id = int(parts[15])
            answers_json = parts[8]
            
            try:
                clean_json = answers_json.replace('\\\\', '\\')
                old_answers = json.loads(clean_json)
                
                if survey_id not in backup_by_survey:
                    backup_by_survey[survey_id] = {}
                backup_by_survey[survey_id][resp_id] = old_answers
            except:
                pass

    total_fixed = 0
    for survey_id, backup_answers_map in backup_by_survey.items():
        print(f"\n>>> Đang xử lý Survey {survey_id}...")
        
        # Lấy danh sách ID câu hỏi SỐNG hiện tại, sắp xếp theo ĐÚNG TRẬT TỰ LOGIC
        active_questions = list(Question.objects.filter(section__survey_id=survey_id).order_by('section__order', 'order', 'id'))
        active_ids = [str(q.id) for q in active_questions if q.component_type not in ['title', 'section_break', 'paragraph']]
        
        if not active_ids:
            print(f"  -> Survey {survey_id} không có câu hỏi active nào, bỏ qua.")
            continue
            
        responses = Response.objects.filter(survey_id=survey_id)
        fixed_count = 0
        
        for r in responses:
            if r.id not in backup_answers_map:
                continue
                
            old_answers = backup_answers_map[r.id]
            if not old_answers:
                continue
                
            # Các key là số trong backup (ID câu hỏi cũ)
            numeric_keys_in_backup = [k for k in old_answers.keys() if str(k).isdigit()]
            if not numeric_keys_in_backup:
                continue
                
            # TÌM LẠI thứ tự logic của các câu hỏi cũ (bao gồm cả câu đã bị ẩn is_active=False)
            old_questions = list(Question.objects.filter(id__in=numeric_keys_in_backup).order_by('section__order', 'order', 'id'))
            old_ids_sorted = [str(q.id) for q in old_questions]
            
            new_answers = {}
            # 1. Bảo lưu các trường chữ (email, full_name, v.v...)
            for k, v in old_answers.items():
                if not str(k).isdigit():
                    new_answers[k] = v
                    
            # 2. Map các trường ID dựa trên đúng thứ tự logic (trên xuống dưới)
            for i, old_id in enumerate(old_ids_sorted):
                val = old_answers.get(old_id)
                # Bắt và fix luôn lỗi mảng 3D của Bảng Dữ Liệu (data-table)
                if isinstance(val, list) and len(val) == 1 and isinstance(val[0], list) and len(val[0]) > 0 and isinstance(val[0][0], list):
                    val = val[0]

                if i < len(active_ids):
                    new_id = active_ids[i]
                    new_answers[new_id] = val
                else:
                    new_answers[old_id] = val
                    
            r.answers = new_answers
            r.save(update_fields=['answers'])
            fixed_count += 1
            
        print(f"  -> Fix thành công {fixed_count} phiếu cho Survey {survey_id}.")
        total_fixed += fixed_count

    print(f"\n--- HOÀN TẤT: Tổng cộng đã fix chuẩn xác {total_fixed} phiếu trả lời! ---")

if __name__ == '__main__':
    fix_all_surveys()
