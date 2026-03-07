#!/home/bkim/2b/0/db/db/bin/python3
import os
import sqlite3
import re

DB_PATH = "/home/bkim/2b/0/db/av_manager.db"
SUB_DIR = "/home/bkim/2b/b/8/subtitles"

def sync_subtitles():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 파일 목록 가져오기
    all_files = [f for f in os.listdir(SUB_DIR) if f.endswith('.srt')]
    
    sub_counts = {}
    for f in all_files:
        # 확장자 제거
        name_only = f.replace('.srt', '')
        # 품번 추출: 알파벳-숫자 조합만 남기고 뒤의 특수문자(_ 등)는 모두 제거
        # 예: 'SNOS-003____' -> 'SNOS-003'
        match = re.match(r'([a-zA-Z0-9]+-[0-9]+)', name_only)
        if match:
            base_id = match.group(1)
            sub_counts[base_id] = sub_counts.get(base_id, 0) + 1
            # 잘 매칭되는지 터미널에 출력해서 확인
            # print(f"File: {f} -> Detected as: {base_id}") 

    # 2. 업데이트 전 초기화
    cur.execute("UPDATE dvds SET subtitle = 0")
    
    # 3. DB 업데이트 및 결과 출력
    updated_count = 0
    for dvd_id, count in sub_counts.items():
        cur.execute("UPDATE dvds SET subtitle = ? WHERE dvd_id = ?", (count, dvd_id))
        if cur.rowcount > 0:
            updated_count += 1
            if count > 1:
                print(f"Match Found: {dvd_id} has {count} versions.")

    conn.commit()
    conn.close()
    print(f"Finished! Updated {updated_count} records in DB.")

if __name__ == "__main__":
    sync_subtitles()
