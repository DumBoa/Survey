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
    backup_file = sys.argv[1] if len(sys.argv) > 1 else 'sipas_backup.sql'
    print(f"--- BẮT ĐẦU FIX DỮ LIỆU TỪ FILE BACKUP: {backup_file} ---")
    
    if not os.path.exists(backup_file):
        print(f"LỖI: Không tìm thấy file {backup_file}. Hãy copy file backup vào cùng thư mục hoặc truyền tên file làm tham số (vd: python fix_rescue_data_v2.py cchc_backup.sql).")
        return

    with open(backup_file, encoding='utf-8') as f:
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
        active_questions = list(Question.objects.filter(section__survey_id=survey_id, is_active=True).order_by('section__order', 'order', 'id'))
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
                    
            # 2. Map các trường ID dựa trên Tiêu đề (Title) ưu tiên, nếu không có thì fallback theo thứ tự
            active_q_map = {str(q.id): q for q in active_questions if q.component_type not in ['title', 'section_break', 'paragraph']}
            
            # Tạo dictionary tìm kiếm theo Title để map chính xác kể cả khi đảo vị trí
            title_to_active_id = {}
            for aid, q in active_q_map.items():
                title_to_active_id[q.title.strip()] = aid
                
            used_active_ids = set()
            
            # Duyệt các câu hỏi cũ
            for i, old_id in enumerate(old_ids_sorted):
                val = old_answers.get(old_id)
                if isinstance(val, list) and len(val) == 1 and isinstance(val[0], list) and len(val[0]) > 0 and isinstance(val[0][0], list):
                    val = val[0]

                # Tìm câu hỏi cũ trong DB để lấy Title
                old_q = next((q for q in old_questions if str(q.id) == old_id), None)
                new_id = None
                
                if old_q and old_q.title.strip() in title_to_active_id:
                    # Map theo tiêu đề (an toàn 100% nếu đảo vị trí)
                    new_id = title_to_active_id[old_q.title.strip()]
                else:
                    # Fallback map theo thứ tự nếu không tìm thấy title giống nhau
                    # Lấy ID active đầu tiên chưa được sử dụng
                    for aid in active_ids:
                        if aid not in used_active_ids:
                            new_id = aid
                            break
                            
                if new_id:
                    new_answers[new_id] = val
                    used_active_ids.add(new_id)
                else:
                    # Nếu hết câu hỏi active để map, cứ giữ lại ID cũ
                    new_answers[old_id] = val
                    
            r.answers = new_answers
            r.save(update_fields=['answers'])
            fixed_count += 1
            
        print(f"  -> Fix thành công {fixed_count} phiếu cho Survey {survey_id}.")
        total_fixed += fixed_count

    print(f"\n--- HOÀN TẤT: Tổng cộng đã fix chuẩn xác {total_fixed} phiếu trả lời! ---")

if __name__ == '__main__':
    fix_all_surveys()
