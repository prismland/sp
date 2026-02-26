#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-25-v01 | Description: 작품 커버 이미지를 배우 ID 기반 프로필로 복사/연결
# Functions: get_width(), pad_text(), search_actor(), main()

import sqlite3
import os
import shutil
import readline
import unicodedata

# --- 터미널 입력 설정 (화살표 키 지원) ---
readline.parse_and_bind("set editing-mode emacs")
readline.parse_and_bind("bind ^[[D backward-char")
readline.parse_and_bind("bind ^[[C forward-char")

# 이미지 경로 설정 (실제 경로에 맞춰 수정 가능)
COVER_DIR = "/home/bkim/2b/0/db/images/covers/"
ACTOR_DIR = "/home/bkim/2b/0/db/images/actors/"

def get_width(text):
    """문자열의 실제 터미널 출력 너비를 계산"""
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
            width += 2
        else:
            width += 1
    return width

def pad_text(text, target_width):
    """너비에 맞춰 오른쪽 공백을 채워줌"""
    text = str(text) if text is not None else ""
    current_width = get_width(text)
    padding = max(0, target_width - current_width)
    return text + (" " * padding)

def search_actor(cur, keyword):
    """이름으로 배우를 검색하여 리스트 출력"""
    query = """
        SELECT id, name_ko, name_jp, name_en, name_alter 
        FROM actors 
        WHERE name_ko LIKE ? OR name_en LIKE ? OR name_jp LIKE ? OR name_alter LIKE ?
        ORDER BY id DESC
    """
    param = f"%{keyword}%"
    cur.execute(query, (param, param, param, param))
    return cur.fetchall()

def main():
    db_path = '/home/bkim/2b/0/db/av_manager.db'
    if not os.path.exists(db_path):
        print("❌ DB 파일을 찾을 수 없습니다.")
        return

    # 디렉토리가 없으면 생성
    os.makedirs(ACTOR_DIR, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n--- [이미지 연결 도구] ---")
    keyword = input("🔍 대상 배우 검색 (이름 등): ").strip()
    if not keyword: return

    actors = search_actor(cur, keyword)
    if not actors:
        print("결과가 없습니다.")
        return

    print("-" * 60)
    for a in actors:
        info = f"ID: {pad_text(a[0], 4)} | {pad_text(a[1], 12)} | {a[2]}"
        print(info)
    print("-" * 60)

    target_id = input("📌 연결할 배우의 ID를 입력하세요: ").strip()
    if not target_id: return

    dvd_id = input("💿 원본 이미지 품번(파일명) 입력: ").strip().upper()
    if not dvd_id: return

    # 확장자는 .jpg로 고정 (필요시 수정)
    src_file = os.path.join(COVER_DIR, f"{dvd_id}.jpg")
    dst_file = os.path.join(ACTOR_DIR, f"{target_id}.jpg")

    if not os.path.exists(src_file):
        print(f"❌ 원본 파일을 찾을 수 없습니다: {src_file}")
    else:
        try:
            shutil.copy2(src_file, dst_file)
            print(f"✅ 연결 완료: [{dvd_id}.jpg] -> [배우ID {target_id}.jpg]")
        except Exception as e:
            print(f"❌ 복사 중 오류 발생: {e}")

    conn.close()

if __name__ == "__main__":
    main()
