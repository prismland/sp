#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-26-v01 | Description: 하이라이트 및 다중 자막 파일 DB 동기화
# Functions: get_dvd_ids(), scan_highlights(), scan_subtitles(), main()

import os
import re
import sqlite3

# --- 설정 ---
DB_PATH = '/home/bkim/2b/0/db/av_manager.db'
HL_DIR = '/home/bkim/2b/0/db/highlights'
SUB_DIR = '/home/bkim/2b/0/db/subtitles'

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. DB에 등록된 모든 품번 가져오기
    cur.execute("SELECT dvd_id FROM dvds")
    dvd_ids = [row[0] for row in cur.fetchall()]

    print(f"🔍 총 {len(dvd_ids)}개의 품번 스캔 시작...")

    for d_id in dvd_ids:
        # 하이라이트 체크 (품번_edit.mp4)
        hl_file = f"{d_id}_edit.mp4"
        hl_path = hl_file if os.path.exists(os.path.join(HL_DIR, hl_file)) else None

        # 자막 체크 (품번.srt, 품번_.srt 등 여러 버전 검색)
        # 정규식: 품번으로 시작하고 .srt로 끝나는 모든 파일
        sub_files = [f for f in os.listdir(SUB_DIR) if f.startswith(d_id) and f.endswith('.srt')]
        sub_path = ",".join(sub_files) if sub_files else None

        # DB 업데이트
        cur.execute("""
            UPDATE dvds 
            SET highlight_path = ?, subtitle_path = ? 
            WHERE dvd_id = ?
        """, (hl_path, sub_path, d_id))

    conn.commit()
    conn.close()
    print("✅ 파일 동기화 완료!")

if __name__ == "__main__":
    main()
