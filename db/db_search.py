#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-25-v01.2 | Description: 4개 필드 검색 및 화살표 키 커서 이동 지원
# Functions: get_width(), pad_text(), main()

import sqlite3
import os
import unicodedata
import readline

# --- 화살표 키 및 편집 기능 활성화 (커서 이동 문제 해결) ---
readline.parse_and_bind("set editing-mode emacs")
readline.parse_and_bind("bind ^[[D backward-char")
readline.parse_and_bind("bind ^[[C forward-char")

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

def main():
    db_path = '/home/bkim/2b/0/db/av_manager.db'
    if not os.path.exists(db_path):
        print("❌ DB 파일을 찾을 수 없습니다.")
        return

    # 이제 여기서 왼쪽 화살표를 눌러도 ^[[D 대신 커서가 이동합니다.
    keyword = input("🔍 검색어 입력 (한글음독/한자가나/로마자/이명): ").strip()
    if not keyword:
        print("검색어를 입력하지 않았습니다.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # name_jp를 포함한 4개 필드 통합 검색 로직
    query = """
        SELECT id, name_ko, name_jp, name_en, birth, name_alter, height, debut, cup, hair, note 
        FROM actors 
        WHERE name_ko LIKE ? OR name_en LIKE ? OR name_jp LIKE ? OR name_alter LIKE ?
        ORDER BY id DESC
    """
    search_param = f"%{keyword}%"
    
    # 4개의 물음표에 맞춰 파라미터 4개 전달 (Incorrect number of bindings 해결)
    cur.execute(query, (search_param, search_param, search_param, search_param))
    rows = cur.fetchall()

    if not rows:
        print(f" '[{keyword}]' 검색 결과가 없습니다.")
        conn.close()
        return

    # 출력 포맷 설정
    w = {
        "id": 3, "ko": 11, "jp": 12, "en": 16, 
        "birth": 5, "h": 4, "c": 3, "ph": 3, "debut": 5,
        "alter": 40, "note": 12
    }

    line_width = 165
    print("\n" + "=" * line_width)
    header = (
        f"{pad_text('ID', w['id'])}| {pad_text('한글음독', w['ko'])}| "
        f"{pad_text('한자가나', w['jp'])}| {pad_text('로마자', w['en'])}| "
        f"{pad_text('생년', w['birth'])}| {pad_text('신장', w['h'])}| "
        f"{pad_text('컵', w['c'])}| {pad_text('PH', w['ph'])}| "
        f"{pad_text('데뷔', w['debut'])}| "
        f"{pad_text('이명', w['alter'])}| 메모"
    )
    print(header)
    print("-" * line_width)

    for row in rows:
        r = [str(item) if item is not None else "" for item in row]
        print(f"{pad_text(r[0], w['id'])}| {pad_text(r[1], w['ko'])}| "
              f"{pad_text(r[2], w['jp'])}| {pad_text(r[3], w['en'])}| "
              f"{pad_text(r[4], w['birth'])}| {pad_text(r[6] if r[6]!='0' else '', w['h'])}| "
              f"{pad_text(r[8], w['c'])}| {pad_text(r[9], w['ph'])}| "
              f"{pad_text(r[7], w['debut'])}| {pad_text(r[5], w['alter'])}| {r[10]}")

    print("-" * line_width)
    print(f"🔎 '{keyword}' 검색 결과: 총 {len(rows)}건")
    print("=" * line_width + "\n")

    conn.close()

if __name__ == "__main__":
    main()