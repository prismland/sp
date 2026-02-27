#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-27-v02.0 | Description: 실행 시 터미널 화면 초기화(clear) 및 정렬 보정 유지
# Functions: get_width(), pad_text(), main()

import sqlite3
import os
import unicodedata
import readline
import sys

# --- 화살표 키 및 편집 기능 활성화 ---
readline.parse_and_bind("set editing-mode emacs")
readline.parse_and_bind("bind ^[[D backward-char")
readline.parse_and_bind("bind ^[[C forward-char")

def get_width(text):
    """문자열의 실제 터미널 출력 너비를 계산"""
    width = 0
    for char in text:
        if char in '·・': 
            width += 2
        elif unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
            width += 2
        else:
            width += 1
    return width

def pad_text(text, target_width):
    """너비에 맞춰 오른쪽 공백을 채워줌 (가운뎃점 치환 포함)"""
    if text and isinstance(text, str):
        text = text.replace('·', '・')
    
    text = str(text) if text is not None else ""
    current_width = get_width(text)
    padding = max(0, target_width - current_width)
    return text + (" " * padding)

def main():
    db_path = '/home/bkim/2b/0/db/av_manager.db'
    if not os.path.exists(db_path):
        print("❌ DB 파일을 찾을 수 없습니다.")
        return

    # [수정] 실행 즉시 화면을 지웁니다.
    os.system('clear')

    # 인자가 있으면 키워드로 사용, 없으면 입력 받음
    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:]).strip()
    else:
        keyword = input("🔍 검색어 입력 (숫자=데뷔연월 / 문자=이름·이명): ").strip()

    if not keyword:
        print("검색어를 입력하지 않았습니다.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    if keyword.isdigit():
        query = """
            SELECT id, name_ko, name_jp, name_en, birth, name_alter, height, debut, cup, hair, note 
            FROM actors 
            WHERE debut = ?
            ORDER BY id DESC
        """
        params = (keyword,)
    else:
        query = """
            SELECT id, name_ko, name_jp, name_en, birth, name_alter, height, debut, cup, hair, note 
            FROM actors 
            WHERE name_ko LIKE ? OR name_en LIKE ? OR name_jp LIKE ? OR name_alter LIKE ?
            ORDER BY id DESC
        """
        search_param = f"%{keyword}%"
        params = (search_param, search_param, search_param, search_param)
    
    cur.execute(query, params)
    rows = cur.fetchall()

    if not rows:
        print(f" '[{keyword}]' 검색 결과가 없습니다.")
        conn.close()
        return

    # 컬럼 너비 설정
    w = {
        "id": 4, "ko": 26, "jp": 26, "en": 20, 
        "birth": 5, "h": 4, "c": 3, "ph": 3, "debut": 5,
        "alter": 95, "note": 15
    }

    line_width = 220
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

    for i, row in enumerate(rows, 1):
        r = [str(item) if item is not None else "" for item in row]
        print(f"{pad_text(r[0], w['id'])}| {pad_text(r[1], w['ko'])}| "
              f"{pad_text(r[2], w['jp'])}| {pad_text(r[3], w['en'])}| "
              f"{pad_text(r[4], w['birth'])}| {pad_text(r[6] if r[6]!='0' else '', w['h'])}| "
              f"{pad_text(r[8], w['c'])}| {pad_text(r[9], w['ph'])}| "
              f"{pad_text(r[7], w['debut'])}| {pad_text(r[5], w['alter'])}| {r[10]}")
        
        if i % 10 == 0 and i < len(rows):
            print("-" * line_width)

    print("-" * line_width)
    search_type = "데뷔" if keyword.isdigit() else "이름/이명"
    print(f"🔎 [{search_type}] '{keyword}' 검색 결과: 총 {len(rows)}건")
    print("=" * line_width + "\n")

    conn.close()

if __name__ == "__main__":
    main()
