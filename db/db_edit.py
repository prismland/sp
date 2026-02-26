#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-26-v02.5.1 | Description: Syntax Error 수정 및 검색 결과 표 형식 적용
# Functions: get_width(), pad_text(), input_with_prefill(), search_actors(), main()

import sqlite3
import os
import readline
import unicodedata

DB_PATH = '/home/bkim/2b/0/db/av_manager.db'

def get_width(text):
    """한글/일어 등 와이드 문자를 고려한 문자열 폭 계산"""
    if text is None: return 0
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in str(text))

def pad_text(text, length):
    """폭에 맞춰 공백을 채워주는 함수"""
    text = str(text) if text is not None else ""
    return text + ' ' * (length - get_width(text))

def input_with_prefill(prompt, text):
    """입력창에 기존값을 미리 띄워주는 기능"""
    def hook():
        readline.insert_text(str(text if text is not None else ""))
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    try:
        return input(prompt)
    finally:
        readline.set_pre_input_hook(None)

def search_actors(cur):
    """수정 전 상세 정보를 포함한 검색 결과 출력"""
    print("\n🔍 [1단계] 수정할 배우 검색")
    name = input("검색어 입력 (한글/일어/영어/기타): ").strip()
    if not name: return

    query = """
    SELECT id, name_ko, name_jp, name_en, birth, height, cup, hair, debut, name_alter, note 
    FROM actors 
    WHERE name_ko LIKE ? OR name_jp LIKE ? OR name_en LIKE ? OR name_alter LIKE ?
    """
    pattern = f"%{name}%"
    cur.execute(query, (pattern, pattern, pattern, pattern))
    rows = cur.fetchall()

    if not rows:
        print("❌ 일치하는 배우가 없습니다.")
        return

    # 헤더 출력
    header = (f"{pad_text('ID', 4)} | {pad_text('한글음독', 12)} | {pad_text('한자가나음독', 16)} | "
              f"{pad_text('로마자', 16)} | {pad_text('생년', 4)} | {pad_text('신장', 4)} | "
              f"{pad_text('컵', 2)} | {pad_text('PH', 2)} | {pad_text('데뷔', 4)} | "
              f"{pad_text('이명', 20)} | 메모")
    print("\n" + header)
    print("-" * 140)

    for r in rows:
        # 0:id, 1:ko, 2:jp, 3:en, 4:birth, 5:height, 6:cup, 7:hair, 8:debut, 9:alter, 10:note
        line = (f"{pad_text(r[0], 4)} | {pad_text(r[1], 12)} | {pad_text(r[2], 16)} | "
                f"{pad_text(r[3], 16)} | {pad_text(r[4], 4)} | {pad_text(r[5], 4)} | "
                f"{pad_text(r[6], 2)} | {pad_text(r[7], 2)} | {pad_text(r[8], 4)} | "
                f"{pad_text(r[9], 20)} | {r[10] if r[10] else ''}")
        print(line)
    print("-" * 140)

def main():
    if not os.path.exists(DB_PATH):
        print("❌ DB 파일을 찾을 수 없습니다.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    search_actors(cur)

    target_id = input("\n📝 수정할 배우의 ID를 입력하세요 (종료: Enter): ").strip()
    if not target_id:
        conn.close()
        return

    # 백업 파일의 컬럼 순서 유지 [cite: 3]
    cur.execute("""
        SELECT id, name_ko, name_jp, name_en, birth, name_alter, 
               height, debut, cup, hair, note 
        FROM actors WHERE id = ?
    """, (target_id,))
    row = cur.fetchone()

    if not row:
        print(f"❌ ID {target_id}에 해당하는 데이터가 없습니다.")
        conn.close()
        return

    print(f"\n--- [ID: {target_id}] 배우 정보 수정 (내용 수정 후 Enter) ---")
    
    # input_with_prefill을 통한 기존값 채우기 기능 
    new_ko    = input_with_prefill("한글음독: ", row[1])
    new_jp    = input_with_prefill("한자가나음독: ", row[2])
    new_en    = input_with_prefill("로마자: ", row[3])
    new_birth = input_with_prefill("생년(YYYY): ", row[4])
    new_alter = input_with_prefill("이명(기타): ", row[5])
    new_h     = input_with_prefill("신장(키): ", row[6])
    new_debut = input_with_prefill("데뷔(YYMM): ", row[7])
    new_cup   = input_with_prefill("컵: ", row[8])
    new_ph    = input_with_prefill("PH(Hair): ", row[9])
    new_note  = input_with_prefill("메모: ", row[10])

    try:
        cur.execute("""
            UPDATE actors SET 
                name_ko=?, name_jp=?, name_en=?, birth=?, name_alter=?, 
                height=?, debut=?, cup=?, hair=?, note=?
            WHERE id=?
        """, (new_ko, new_jp, new_en, new_birth, new_alter, 
              new_h, new_debut, new_cup, new_ph, new_note, target_id))
        
        conn.commit()
        print(f"\n✅ ID {target_id} ({new_ko}) 정보가 업데이트되었습니다.")
    except Exception as e:
        print(f"❌ 업데이트 중 오류 발생: {e}")
    
    conn.close()

if __name__ == "__main__":
    main()
