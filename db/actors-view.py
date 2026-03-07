#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-03-07-v68 | Description: dvds-view 기반 배우 관리 최종 (DB파일명 및 캐시경로 수정)
# Functions: search_actors(), update_actor_info(), get_thumbnail_lines(), edit_input(), get_key(), main()

import sqlite3
import os
import sys
import subprocess
import math
import pathlib
import time
import tty
import termios
import readline

# [설정] 사용자 환경에 맞춘 경로 수정
CACHE_DIR = pathlib.Path.home() / ".cache" / "dvds"  # dvb에서 dvd로 수정
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 보내주신 dvds-view.py의 DB명을 따라갑니다. (dvds.db가 아니라면 아래 파일명을 확인하세요)
DB_PATH = "/home/bkim/2b/0/db/av_manager.db" 
IMG_SUFFIX = "_l_0.jpg"

def search_actors(keyword=""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # name_ko 기준 최신 DVD 코드를 가져오는 서브쿼리
    # dvds 테이블의 actors_raw 컬럼을 참조합니다.
    query = """
        SELECT a.id, a.name_ko, a.name_jp, a.name_alter, a.name_en, a.hair, a.note,
               (SELECT d.code FROM dvds d 
                WHERE d.actors_raw LIKE '%' || a.name_ko || '%' 
                ORDER BY d.id DESC LIMIT 1) as rep_code
        FROM actors a
        WHERE a.name_ko LIKE ? OR a.name_jp LIKE ? OR a.name_alter LIKE ? OR a.note LIKE ?
        ORDER BY a.id DESC
    """
    term = f"%{keyword}%"
    try:
        cur.execute(query, (term, term, term, term))
        rows = cur.fetchall()
    except Exception as e:
        # 테이블이 없는 경우 에러 메시지 출력
        print(f"\n❌ DB Error: {e}")
        rows = []
    finally:
        conn.close()
    return rows

def update_actor_info(actor_id, field, new_value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(f"UPDATE actors SET {field} = ? WHERE id = ?", (new_value, actor_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_thumbnail_lines(code, width=20, height=10):
    if not code: return False
    prefix = code[:2].lower()
    url = f"https://c0.jdbstatic.com/samples/{prefix}/{code}{IMG_SUFFIX}"
    cache_path = CACHE_DIR / f"{code}{IMG_SUFFIX}"

    if not cache_path.exists():
        time.sleep(0.1)
        subprocess.run(f"curl -sfL '{url}' -o '{cache_path}'", shell=True, stderr=subprocess.DEVNULL)

    # dvds-view.py의 핵심: 위치 저장(\033[s) 및 커서 복구 로직
    sys.stdout.write("\033[s") 
    cmd = f"chafa --format sixel --size {width}x{height} --stretch '{cache_path}'"
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
    # 이미지 출력 후 텍스트를 적기 위해 위로 10줄, 오른쪽으로 22칸 이동
    sys.stdout.write(f"\033[{height}A\033[22C") 
    sys.stdout.flush()
    return True

def edit_input(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try: return input(prompt)
    finally: readline.set_startup_hook()

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else ""
    results = search_actors(keyword)
    
    page_size = 5 
    current_page = 1

    while True:
        os.system('clear')
        total_results = len(results)
        total_pages = math.ceil(total_results / page_size) if total_results > 0 else 1
        start_idx = (current_page - 1) * page_size
        page_rows = results[start_idx : start_idx + page_size]

        print(f"👤 Actor Manager | Search: '{keyword}' | Page: {current_page}/{total_pages} ({total_results} items)")
        print("=" * 110)

        if not page_rows:
            print("\n   [!] 검색 결과가 없습니다. DB 파일명과 테이블명을 확인하세요.")
            print(f"   (현재 설정된 DB 경로: {DB_PATH})")

        for i, r in enumerate(page_rows, start_idx + 1):
            img_h = 10
            # 썸네일 출력 (r[7]은 서브쿼리로 가져온 rep_code)
            get_thumbnail_lines(r[7], width=20, height=img_h)
            
            padding_size = 22
            n_alt = (r[3] or "").replace(';', ' ').strip()
            
            # 배우 정보 레이아웃
            info_lines = [
                f"{i:>2}. \033[1m[{r[1]}]\033[0m {r[2] or ''}",
                f"    EN: {r[4] or ''}",
                f"    Alias: {n_alt[:60]}",
                f"    Hair: \033[33m{r[5] or '0'}\033[0m",
                f"    Notes: {r[6] or ''}"
            ]
            
            for idx, line in enumerate(info_lines):
                if idx < len(info_lines) - 1:
                    sys.stdout.write(f"{line}\033[K\n\033[{padding_size}C")
                else:
                    sys.stdout.write(f"{line}\033[K")
            
            # 다음 항목과의 간격 조정
            rem_lines = max(1, img_h - len(info_lines))
            sys.stdout.write("\n" * (rem_lines + 1))
            sys.stdout.write("-" * 110 + "\n")
            sys.stdout.flush()

        print(f"\n👉 [L/.] Next | [H/,] Prev | [R] Refresh | [1-5] Detail | [Q] Quit")
        key = get_key().lower()

        if key == 'q': break
        elif key == 'r':
            results = search_actors(keyword)
            continue
        elif key in ['l', '.', ' ']:
            if current_page < total_pages: current_page += 1
        elif key in ['h', ',']:
            if current_page > 1: current_page -= 1
        elif key in ['1', '2', '3', '4', '5']:
            rel_idx = int(key) - 1
            if rel_idx >= len(page_rows): continue
            
            abs_idx = start_idx + rel_idx
            selected = list(results[abs_idx])
            
            while True:
                os.system('clear')
                get_thumbnail_lines(selected[7], width=40, height=20)
                sys.stdout.write("\n" * 21) 

                print(f"📑 [DETAILS] {selected[1]} ({selected[2]})")
                print(f"ID: {selected[0]} | EN: {selected[4]}")
                print(f"Alias: {selected[3]}")
                print(f"Hair: {selected[5]} | Notes: {selected[6]}")
                print("-" * 110)
                print("🛠️  [h]Edit Hair | [n]Edit Note | [v]View Movies | [any key] Return")
                
                act = input("Action: ").lower()
                if act == 'h':
                    new_val = edit_input(" ▶ New Hair: ", str(selected[5] or ""))
                    if update_actor_info(selected[0], 'hair', new_val):
                        selected[5] = new_val
                        results[abs_idx] = tuple(selected)
                elif act == 'n':
                    new_val = edit_input(" ▶ New Note: ", str(selected[6] or ""))
                    if update_actor_info(selected[0], 'note', new_val):
                        selected[6] = new_val
                        results[abs_idx] = tuple(selected)
                elif act == 'v':
                    os.system(f"python3 dvds-view.py '{selected[1]}'")
                else:
                    break

if __name__ == "__main__":
    main()
