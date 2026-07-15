import os
import sys

def clean_sql_backup(input_file, output_file):
    try:
        if not os.path.exists(input_file):
            print(f"Lỗi: Không tìm thấy file {input_file}")
            return
            
        print(f"Đang đọc file {input_file}...")
        
        in_copy_block = False
        removed_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as fin, \
             open(output_file, 'w', encoding='utf-8') as fout:
             
            for line in fin:
                # Kiểm tra bắt đầu khối COPY của bảng survey_response
                if line.startswith('COPY public.survey_response '):
                    in_copy_block = True
                    fout.write(line)
                    continue
                
                # Kiểm tra kết thúc khối COPY
                if in_copy_block and line.strip() == '\\.':
                    in_copy_block = False
                    fout.write(line)
                    continue
                
                # Xử lý các dòng dữ liệu bên trong khối COPY
                if in_copy_block:
                    # Các cột cách nhau bằng dấu Tab (\t)
                    # Cột cuối cùng là 'status'
                    columns = line.split('\t')
                    if len(columns) > 0:
                        status = columns[-1].strip()
                        if status == 'draft':
                            removed_count += 1
                            continue # Bỏ qua dòng này (không ghi vào file mới)
                
                # Ghi các dòng bình thường (hoặc không phải draft) vào file mới
                fout.write(line)
                
        print(f"Thành công! Đã loại bỏ {removed_count} bài làm nháp (draft) khỏi file backup.")
        print(f"File mới đã được lưu tại: {output_file}")
        
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == '__main__':
    # File đầu vào và đầu ra
    INPUT_SQL = 'sipas_backup.sql'
    OUTPUT_SQL = 'sipas_backup_cleaned.sql'
    
    clean_sql_backup(INPUT_SQL, OUTPUT_SQL)
