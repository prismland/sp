#!/home/bkim/2b/0/db/db/bin/python3
import sqlite3
import os
import sys
import subprocess
import math
import pathlib
import time
import tty
import termios

# 캐시 경로 설정
CACHE_DIR = pathlib.Path.home() / ".cache" / "dvds"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

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
            names = [row[0], row[1], row[2], row[4]]
            for name in names:
                if name:
                    hair_map[name.strip()] = h_val
    except: pass
    conn.close()
    return hair_map

def format_actors_with_hair(actors_raw, hair_map):
    if not actors_raw: return ""
    actor_list = [a.strip() for a in actors_raw.replace(',', ' ').split() if a.strip()]
    formatted = []
    for name in actor_list:
        if name in hair_map:
            formatted.append(f"{name}❤️ ") 
        else:
            formatted.append(name)
    return ", ".join(formatted)

def search_dvds(keyword="", order_by="date"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 정렬 조건 문자열 생성
    if order_by == "date":
        order_clause = "release_date DESC, id DESC"
    else:
        order_clause = "id DESC"

    query = """
        SELECT dvd_id, subtitle, topgirl, av123, highlight, note, actors_raw, code, title, release_date, id
        FROM dvds 
        WHERE dvd_id LIKE ? OR actors_raw LIKE ? OR note LIKE ?
        ORDER BY """ + order_clause
    
    term = f"%{keyword}%"
    try:
        cur.execute(query, (term, term, term))
        rows = cur.fetchall()
    except Exception as e:
        print(f"\n❌ DB Query Error: {e}")
        rows = []
    finally:
        conn.close()

    return rows

    cmd = f"curl -sL '{url}' | chafa --format sixel --size {width}x{height} --stretch -"
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)

def show_cover(code):
    if not code: return
    prefix = code[:2].lower()
    url = f"https://c0.jdbstatic.com/samples/{prefix}/{code}_l_0.jpg"
    cmd = f"curl -sL '{url}' | chafa --format sixel -"
    try:
        subprocess.run(cmd, shell=True)
    except Exception: pass

# 썸네일 전용 함수: 이미지를 가져와서 문자열 배열(줄 단위)로 반환
def get_thumbnail_lines(code, width=20, height=10):
    if not code: return False
    
    prefix = code[:2].lower()
    url = f"https://c0.jdbstatic.com/samples/{prefix}/{code}_l_0.jpg"
    cache_path = CACHE_DIR / f"{code}_l_0.jpg"

    # 1. 캐시 확인 및 다운로드
    if not cache_path.exists():
        time.sleep(0.2)
        try:
            # -f 옵션으로 실패 시 에러 반환, -s로 조용히 다운로드
            subprocess.run(f"curl -sfL '{url}' -o '{cache_path}'", shell=True)
        except:
            return False

    # 2. 이미지 출력 전 위치 저장
    sys.stdout.write("\033[s") 

    # 3. 로컬 파일에서 Sixel 출력 (네트워크 딜레이 없음)
    # 벽돌 방지를 위해 --format sixel 유지
    cmd = f"chafa --format sixel --size {width}x{height} --stretch '{cache_path}'"
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
    
    # 3. [핵심] 커서를 이미지 시작 행으로 올리고, 우측으로 20칸 이동
    # \033[{height}A : height만큼 위로
    # \033[20C : 오른쪽으로 20칸 이동 (이미지 너비만큼)
    sys.stdout.write(f"\033[{height}A\033[20C")
    sys.stdout.flush()
    return True

def get_key():
    # [수정] 터미널 설정을 미리 저장해둡니다.
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    # [수정] fd와 old_settings를 함수 시작 시점에 정의합니다.
    # 0은 표준 입력(sys.stdin)의 파일 디스크립터 번호입니다.
    fd = sys.stdin.fileno()
    try:
        old_settings = termios.tcgetattr(fd)
    except termios.error:
        # 터미널 환경이 아닐 경우를 대비한 방어 코드
        old_settings = None

    keyword = sys.argv[1] if len(sys.argv) > 1 else ""
    #sort_mode = "date"  # <--- 루프 밖에서 미리 선언해야 합니다.
    sort_mode = "id"  # <--- 루프 밖에서 미리 선언해야 합니다.

    results = search_dvds(keyword, sort_mode)

    if not results:
        print(f"🔍 '{keyword}' 결과 없음.")
        return

    hair_map = get_actor_hair_map()
    
    # --- 페이지네이션 설정 (5개로 변경) ---
    page_size = 5 
    current_page = 1

    while True:
        os.system('clear')
        total_results = len(results)
        total_pages = math.ceil(total_results / page_size)

        # [해결] 현재 페이지에 따른 데이터 인덱스 계산
        # 이 부분이 results[start_idx:end_idx] 보다 위에 있어야 합니다.
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_rows = results[start_idx:end_idx]

        # 상단 바에 현재 정렬 모드 표시
        sort_label = "📅 Date" if sort_mode == "date" else "🆔 ID"
        print(f"🔎 '{keyword}' | {sort_label} | Page: {current_page}/{total_pages} ({total_results} items)")
        print("=" * 110)

        for i, r in enumerate(page_rows, start_idx + 1):
            img_h = 10
            # 1. 이미지 출력 및 커서 위치를 이미지 우측 상단으로 이동
            # get_thumbnail_lines 내부에서 이미지를 출력하고 커서를 위+오른쪽으로 보냅니다.
            get_thumbnail_lines(r[7], width=20, height=img_h)
            
            # 2. [오류 해결] padding 변수 정의
            padding_size = 20
            padding = " " * padding_size
            
            s_tag = f"[S]" if r[1] >= 1 else "[ ]"
            t_tag = f"[T]" if r[2] >= 1 else "[ ]"
            actor_display = format_actors_with_hair(r[6], hair_map)
            
            # 3. 텍스트 정보 구성
            info_lines = [
                f"{i:>2}. {r[0]} {s_tag}{t_tag}",
               # f"    {r[9]}",
                f"    {r[8][:40]}",
                f"    {r[8][40:80]}",
                f"",
                f"    {actor_display[:50]}",
                f"    {actor_display[50:100]}",
                f"    {actor_display[100:150]}",
                f"    {actor_display[150:200]}",
                f"    {r[9]}\tNotes: {r[5] if r[5] else ''}"
            ]
            
            # 4. 텍스트 출력 로직
            # 각 줄을 출력한 후 다음 줄로 넘어가서 다시 오른쪽으로 padding_size만큼 이동합니다.
            for idx, line in enumerate(info_lines):
                if idx < len(info_lines) - 1:
                    sys.stdout.write(f"{line}\033[K\n\033[{padding_size}C")
                else:
                    sys.stdout.write(f"{line}\033[K") # 마지막 줄은 줄바꿈만
            
            # 5. 다음 항목과의 간격 확보
            # 이미지 높이(10)에서 출력한 줄 수(6)를 뺀 만큼 내려가서 구분선을 긋습니다.
            rem_lines = max(1, img_h - len(info_lines))
            sys.stdout.write("\n" * (rem_lines + 1))
            sys.stdout.write("-" * 150 + "\n")
            sys.stdout.flush()


        # --- 하단 페이지네이션 바 ---
        nav = []
        if current_page > 1: nav.extend(["[F]irst", "[P]rev"])
        num_start = max(1, current_page - 2)
        num_end = min(total_pages, current_page + 2)
        for n in range(num_start, num_end + 1):
            nav.append(f"<{n}>" if n == current_page else str(n))
        if current_page < total_pages: nav.extend(["[N]ext", "[L]ast"])

        print("\n" + "  ".join(nav))
        # 하단 안내 문구에 [O]rder 추가
        prompt = f"\n👉 [L/.] Next | [H/,] Prev | [R] Refresh | [O] Sort Toggle | [0] Jump | [1-5] Detail | [Q] Quit\nSelect: "
        sys.stdout.write(prompt)
        sys.stdout.flush()

        key = get_key().lower()

        if key == 'q':
            break
        
        # [신규] 새로고침 기능 (R 키)
        elif key == 'r':
            # 현재 키워드와 정렬 모드를 유지한 채로 DB 다시 읽기
            results = search_dvds(keyword, sort_mode)
            # (옵션) 새로고침 시 1페이지로 돌아가고 싶다면 아래 주석 해제
            # current_page = 1
            continue

        # [핵심] 정렬 토글 기능 (O 키)
        elif key == 'o':
            # 정렬 모드 전환
            sort_mode = "id" if sort_mode == "date" else "date"
            # 데이터 재로딩
            results = search_dvds(keyword, sort_mode)
            current_page = 1  # 정렬이 바뀌면 첫 페이지로 이동하는 것이 편리함
            continue

        # 1. 페이지 이동 (즉시 반응)
        elif key in ['l', '.', 'n', ' ']:
            if current_page < total_pages: current_page += 1
        elif key in ['h', ',', 'p']:
            if current_page > 1: current_page -= 1

        # 3. 특정 페이지로 점프 (0번 누른 후 숫자 입력)
        elif key == '0':
            sys.stdout.write("\r🚀 Jump to Page #: ")
            sys.stdout.flush()
            
            # [수정] 위에서 정의한 fd와 old_settings를 사용합니다.
            if old_settings:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            try:
                # 이제 키보드 타이핑이 가능합니다.
                page_input = sys.stdin.readline().strip()
                if page_input.isdigit():
                    target = int(page_input)
                    if 1 <= target <= total_pages:
                        current_page = target
            except Exception:
                pass
            # 입력이 끝나면 다시 Raw Mode로 돌아갈 준비는 루프 처음의 get_key가 알아서 합니다.

        # 2. 상세보기 (화면상의 1~5번째 항목)
        # 현재 화면에 떠 있는 항목 수(len(page_rows))까지만 입력 허용
        elif key in ['1', '2', '3', '4', '5']:
            # 1. 현재 화면의 상대 번호를 전체 리스트의 절대 인덱스로 변환
            rel_idx = int(key) - 1
            if rel_idx >= len(page_rows): # 현재 페이지에 항목이 5개 미만일 때 방어 코드
                continue
                
            abs_idx = start_idx + rel_idx  # 전체 results에서의 위치 계산
            selected = list(results[abs_idx])
            
            while True:
                os.system('clear')
                # 큰 이미지를 보여주는 show_cover 함수 (기존 구현 사용)
                show_cover(selected[7])
                
                tags = ["[{}]".format(c if val >= 1 else " ") for c, val in zip("ST1H", selected[1:5])]
                # 하트 태그 로직
                is_hair = any(n.strip() in hair_map for n in selected[6].replace(',', ' ').split())
                hr_tag = "❤️" if is_hair else "  "
                
                print(f"📑 [DETAILS]  {''.join(tags)} {hr_tag}")
                print(f"ID: {selected[0]} | Date: {selected[9]}")
                print(f"Title: {selected[8]}")
                print(f"Actors: {format_actors_with_hair(selected[6], hair_map)}")
                print(f"Notes: {selected[5]}")
                print("-" * 150)
                print("🌐 [s]st [j]jd [1]123 [t]tg | 🛠️  [u]Toggle Sub | [any key] Return to List")
                
                # 상세 보기 내부에서도 get_key()를 쓰면 Enter 없이 조작 가능합니다
                # 만약 입력을 직접 타이핑하고 싶으시면 기존처럼 input()을 쓰셔도 됩니다.
                act = input("Action: ").lower()
                
                if act in ['s', 'j', '1', 't']:
                    site_code = 'jd' if act == 'j' else 'st' if act == 's' else '12' if act == '1' else 'tg'
                    open_site(site_code, selected[0])
                    # 사이트 열고 보통 돌아오므로 break 하거나 continue 선택
                    continue 
                
                elif act == 'u':
                    # 자막 상태 업데이트 및 원본 리스트 반영
                    new_sub_status = update_subtitle(selected[0], selected[1])
                    selected[1] = new_sub_status
                    # [중요] 원본 results 리스트의 해당 위치 데이터를 업데이트
                    results[abs_idx] = tuple(selected)
                    continue 
                
                else: 
                    # 아무 키나 누르면 상세 보기 종료 후 목록으로
                    break

if __name__ == "__main__":
    main()
