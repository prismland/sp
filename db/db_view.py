#!/home/bkim/2b/0/db/db/bin/python3
# [get_width, pad_text, main]
# 버전 정보: 2026-02-25-v08 | 날짜: 2026-02-25
# 기능: 전체 필드 출력, 기타이름 너비 확장, PH 표기 및 남배우(-) 대응 정렬

import sqlite3
import os
import unicodedata

def get_width(text):
    """문자열의 실제 터미널 출력 너비를 계산 (한글/일어는 2칸, 영문/숫자는 1칸)"""
    width = 0
    for char in text:
        # 한글, 일본어(한자/가나) 등 전각 문자는 2칸으로 계산
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
        print(f"❌ DB 파일을 찾을 수 없습니다: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # 모든 필드 조회 (ID 역순)
        cur.execute("SELECT id, name_ko, name_jp, name_en, birth, name_alter, height, debut, cup, hair, note FROM actors ORDER BY id DESC")
        rows = cur.fetchall()
    except Exception as e:
        print(f"❌ DB 조회 오류: {e}")
        return

    # 컬럼별 고정 너비 설정
    # 기타이름(alter)을 40칸으로 설정하여 긴 데이터에 대응
    w = {
        "id": 3, "ko": 11, "jp": 12, "en": 16, 
        "birth": 5, "h": 4, "c": 3, "ph": 3, "debut": 5,
        "alter": 40, "note": 12
    }

    # 헤더 구성 (Hair -> PH)
    header = (
        f"{pad_text('ID', w['id'])}| {pad_text('한글음독', w['ko'])}| "
        f"{pad_text('한자가나음독', w['jp'])}| {pad_text('로마자', w['en'])}| "
        f"{pad_text('생년', w['birth'])}| {pad_text('신장', w['h'])}| "
        f"{pad_text('컵', w['c'])}| {pad_text('PH', w['ph'])}| "
        f"{pad_text('데뷔', w['debut'])}| "
        f"{pad_text('이명', w['alter'])}| 메모"
    )
    
    line_width = 165 # 전체 출력 폭
    print("\n" + "=" * line_width)
    print(header)
    print("-" * line_width)

    for row in rows:
        # 0:id, 1:ko, 2:jp, 3:en, 4:birth, 5:alter, 6:height, 7:debut, 8:cup, 9:hair, 10:note
        r = [str(item) if item is not None else "" for item in row]
        
        id_v    = pad_text(r[0], w['id'])
        ko_v    = pad_text(r[1], w['ko'])
        jp_v    = pad_text(r[2], w['jp'])
        en_v    = pad_text(r[3], w['en'])
        birth_v = pad_text(r[4], w['birth'])
        h_v     = pad_text(r[6] if r[6] != "0" else "", w['h'])
        cup_v   = pad_text(r[8], w['c'])   # 남배우의 경우 '-' 가 출력됨
        ph_v    = pad_text(r[9], w['ph'])
        debut_v = pad_text(r[7], w['debut'])
        alter_v = pad_text(r[5], w['alter'])
        note_v  = r[10]

        print(f"{id_v}| {ko_v}| {jp_v}| {en_v}| {birth_v}| {h_v}| {cup_v}| {ph_v}| {debut_v}| {alter_v}| {note_v}")

    print("-" * line_width)
    print(f"📊 총 {len(rows)}명의 배우 정보가 등록되어 있습니다.")
    print("=" * line_width + "\n")
    
    conn.close()

if __name__ == "__main__":
    main()