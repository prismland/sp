#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-03-01-v03.9 | Description: 별표 대신 하트(❤️) 기호 적용 및 name_en 포함 매칭 완성
# Functions: get_actor_hair_map(), format_actors_with_hair(), search_dvds(), main()

import sqlite3
import os
import sys
import subprocess

DB_PATH = "/home/bkim/2b/0/db/av_manager.db"
ID_OFF = 23
NOTE_OFF = 6    

def open_site(site_code, search_term):
    cmd = f"qutebrowser ':open -t {site_code} {search_term}'"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def update_subtitle(dvd_id, current_sub):
    new_sub = 0 if current_sub >= 1 else 1
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE dvds SET subtitle = ? WHERE dvd_id = ?", (new_sub, dvd_id))
    conn.commit()
    conn.close()
    return new_sub

def get_actor_hair_map():
    hair_map = {}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name_ko, name_jp, name_alter, hair, name_en FROM actors")
        for row in cur.fetchall():
            h_val = row[3] if row[3] and row[3] >= 1 else 0
            if h_val == 0: continue
            # ko, jp, alter, en 모든 컬럼을 매칭 대상으로 등록
            names = [row[0], row[1], row[2], row[4]]
            for name in names:
                if name:
                    hair_map[name.strip()] = h_val
    except:
        pass
    conn.close()
    return hair_map


# Version: 2026-03-01-v03.9.1 | Description: 이모지 너비로 인한 터미널 정렬 틀어짐 방지 보정
def format_actors_with_hair(actors_raw, hair_map):
    if not actors_raw: return ""
    actor_list = [a.strip() for a in actors_raw.replace(',', ' ').split() if a.strip()]
    formatted = []
    for name in actor_list:
        if name in hair_map:
            # ❤️ 뒤에 공백을 주어 터미널 글자 겹침을 방지
            formatted.append(f"{name}❤️ ") 
        else:
            formatted.append(name)
    return ", ".join(formatted)


def search_dvds(keyword=""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = """
        SELECT dvd_id, subtitle, topgirl, av123, highlight, note, actors_raw, code, title, release_date, id
        FROM dvds 
        WHERE dvd_id LIKE ? OR title LIKE ? OR actors_raw LIKE ? OR note LIKE ?
        ORDER BY release_date DESC, id DESC
    """
    term = f"%{keyword}%"
    cur.execute(query, (term, term, term, term))
    rows = cur.fetchall()
    conn.close()
    return rows

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else ""
    results = search_dvds(keyword)
    if not results:
        print(f"🔍 '{keyword}' 결과 없음.")
        return

    hair_map = get_actor_hair_map()
    
    page_size = 40
    current_start = 0

    while current_start < len(results):
        os.system('clear')
        total = len(results)
        page_end = min(current_start + page_size, total)
        print(f"🔎 Search: '{keyword}' | {current_start+1}-{page_end} / {total}")
        
        sep = "-" * 125
        print(sep)
        print(f"{'No':3} | {'ID':{ID_OFF}} | {'Notes':{NOTE_OFF}} | {'Actors'}")
        print(sep)

        page_rows = results[current_start:page_end]
        for i, r in enumerate(page_rows, current_start + 1):
            s_tag = f"[{'S' if r[1] >= 1 else ' '}]" if r[1] >= 1 else "   "
            t_tag = f"[{'T' if r[2] >= 1 else ' '}]" if r[2] >= 1 else "   "
            a_tag = f"[{'1' if r[3] >= 1 else ' '}]" if r[3] >= 1 else "   "
            h_tag = f"[{'H' if r[4] >= 1 else ' '}]" if r[4] >= 1 else "   "
            
            id_tags = f"{r[0][:10]:10} {s_tag}{t_tag}{a_tag}{h_tag}"
            note_val = f"{(r[5] if r[5] else ''):<{NOTE_OFF}}"[:NOTE_OFF]
            
            actor_display = format_actors_with_hair(r[6], hair_map)
            print(f"{i:>3} | {id_tags:{ID_OFF}} | {note_val:{NOTE_OFF}} | {actor_display}")

        print(sep)
        print(f"👉 [Number]: Details | [Enter]: Next | [b]: Back | [q]: Quit")
        
        choice = input("Select: ").strip().lower()
        if choice == 'q': break
        elif choice == 'b':
            current_start = max(0, current_start - page_size)
            continue
        elif choice == "":
            current_start += page_size
            if current_start >= total: current_start = 0
            continue
        
        try:
            idx = int(choice) - 1
            selected = list(results[idx])
            while True:
                os.system('clear')
                # 태그 고정폭 생성
                tags = ["[{}]".format(c if val >= 1 else " ") for c, val in zip("ST1H", selected[1:5])]
                hr_tag = "❤️" if any(n.strip() in hair_map for n in selected[6].replace(',', ' ').split()) else "  "
                
                print(f"📑 [DETAILS]  {''.join(tags)} {hr_tag}")
                print(f"ID: {selected[0]} | Date: {selected[9]}")
                print(f"Title: {selected[8]}")
                print(f"Actors: {format_actors_with_hair(selected[6], hair_map)}")
                print(f"Notes: {selected[5]}")
                print("-" * 60 + "\n🌐 [s]st [j]jd [1]123 [t]tg | 🛠️  [u]Toggle Sub | [any key]list")
                
                act = input("Action: ").lower()
                if act in ['s', 'j', '1', 't']:
                    code = 'jd' if act == 'j' else 'st' if act == 's' else '12' if act == '1' else 'tg'
                    term = selected[7] if act == 'j' else selected[0]
                    open_site(code, term)
                    break
                elif act == 'u':
                    selected[1] = update_subtitle(selected[0], selected[1])
                    results[idx] = tuple(selected)
                    continue 
                else: break 
        except: continue

if __name__ == "__main__":
    main()
