#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-26-v04.2 | Description: 2중 루프, 페이지네이션, 가이드 재출력 기능 통합 및 코드 최적화
# Functions: get_width(), pad_text(), open_qute_search(), show_guide(), main()

import sqlite3
import unicodedata
import sys
import subprocess
import os

DB_PATH = '/home/bkim/2b/0/db/av_manager.db'
PAGE_SIZE = 20

def get_width(text):
    """문자열의 실제 출력 폭 계산 (한글/일어 2칸)"""
    if text is None: return 0
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in str(text))

def pad_text(text, length):
    """출력 폭에 맞춘 공백 패딩"""
    text = str(text) if text is not None else ""
    return text + ' ' * (length - get_width(text))

def open_qute_search(engine, keyword):
    """qutebrowser 새 탭 강제 실행"""
    if not keyword: return
    try:
        cmd = f":open -t {engine} {keyword}"
        subprocess.Popen(['qutebrowser', cmd], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

def show_guide():
    """가이드 출력"""
    print("\n" + "="*60)
    print(" 📖 AV 매니저 뷰어 가이드")
    print("="*60)
    print(" 1. 실행 방법 (검색 단계):")
    print("    - [검색어] : 배우명, 원문배우, 품번 검색")
    print("    - nosub    : 자막 없는 리스트만 출력")
    print("    - all      : 전체 리스트 출력 (Enter와 동일)")
    print("    - q        : 프로그램 최종 종료")
    print("-" * 60)
    print(" 2. 결과 화면 조작 (번호 입력 단계):")
    print("    - [번호]          : 해당 작품을 'tg' 엔진으로 검색")
    print("    - [번호] [단축어] : 특정 엔진(sg, jd, 12 등)으로 검색")
    print("    - [Enter]         : 다음 페이지 보기 또는 검색 단계로 복귀")
    print("="*60)

def main():
    while True:
        show_guide()
        
        # 인자 처리 (첫 실행 시 인자가 있으면 사용)
        if len(sys.argv) > 1:
            initial_input = sys.argv[1]
            sys.argv = [sys.argv[0]]
        else:
            initial_input = input("\n👉 검색어, nosub, all (종료: q): ").strip()
        
        if initial_input.lower() == 'q':
            print("👋 프로그램을 완전히 종료합니다.")
            break
            
        search_keyword = initial_input

        if not os.path.exists(DB_PATH):
            print(f"❌ DB 파일을 찾을 수 없습니다: {DB_PATH}")
            break

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            query = """
            SELECT d.dvd_id, 
                   COALESCE(GROUP_CONCAT(a.name_ko, ', '), '정보없음') as actors_ko, 
                   d.actors_raw,
                   d.highlight_path, d.subtitle_path
            FROM dvds d
            LEFT JOIN dvd_actors da ON d.dvd_id = da.dvd_id
            LEFT JOIN actors a ON da.actor_id = a.id
            GROUP BY d.dvd_id
            """

            if search_keyword.lower() == "nosub":
                query += " HAVING (d.subtitle_path IS NULL OR d.subtitle_path = '')"
            elif search_keyword.lower() == "all" or not search_keyword:
                pass
            else:
                query += f" HAVING (actors_ko LIKE '%{search_keyword}%' OR d.actors_raw LIKE '%{search_keyword}%' OR d.dvd_id LIKE '%{search_keyword}%')"
            
            query += " ORDER BY d.dvd_id DESC"
            cur.execute(query)
            rows = cur.fetchall()

            if not rows:
                print(f"\nℹ️ '{search_keyword}'에 대한 결과가 없습니다.")
                conn.close()
                continue

            total_rows = len(rows)
            current_idx = 0
            id_map = {}

            print(f"\n🔎 검색 결과: 총 {total_rows}건")

            # 리스트 확인 루프
            while True:
                w_idx, w_id_full, w_act_ko, w_act_raw = 4, 18, 25, 25
                header = f"{pad_text('번호', w_idx)} | {pad_text('품번/파일', w_id_full)} | {pad_text('배우(KO)', w_act_ko)} | {pad_text('actors_raw', w_act_raw)}"
                print("\n" + header)
                print("-" * 110)

                page_end = min(current_idx + PAGE_SIZE, total_rows)
                for i in range(current_idx, page_end):
                    idx = i + 1
                    row = rows[i]
                    dvid, act_ko, act_raw, hl, sub = row
                    h_tag, s_tag = ("[H]" if hl else "   "), ("[S]" if sub else "   ")
                    id_display = f"{dvid} {h_tag}{s_tag}"
                    disp_ko = (act_ko[:22] + "..") if get_width(act_ko) > w_act_ko else act_ko
                    disp_raw = (act_raw[:22] + "..") if get_width(act_raw or "") > w_act_raw else (act_raw or "")
                    id_map[idx] = dvid
                    print(f"{str(idx).ljust(w_idx)} | {pad_text(id_display, w_id_full)} | {pad_text(disp_ko, w_act_ko)} | {pad_text(disp_raw, w_act_raw)}")

                print("-" * 110)
                status_msg = f" (현재 {page_end}/{total_rows})" if page_end < total_rows else " (마지막 페이지)"
                print(status_msg)

                prompt = "\n👉 입력 ([번호] [단축어] / Enter:다음or복귀 / q:중단): "
                user_input = input(prompt).strip().split()
                
                if not user_input:
                    if page_end < total_rows:
                        current_idx += PAGE_SIZE
                        continue
                    else:
                        print("🔄 검색 단계로 돌아갑니다.")
                        break
                
                if user_input[0].lower() == 'q':
                    print("🔄 리스트 확인 중단.")
                    break
                    
                if user_input[0].isdigit():
                    num = int(user_input[0])
                    if num in id_map:
                        engine = user_input[1] if len(user_input) > 1 else 'tg'
                        open_qute_search(engine, id_map[num])
                        print(f"🚀 {id_map[num]} ({engine}) 검색 중...")
                    else:
                        print(f"❌ {num}번은 현재 리스트에 없습니다.")
                else:
                    print("❌ 번호 혹은 명령어를 입력하세요.")

            conn.close()

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            break

if __name__ == "__main__":
    main()
