# Version: 2026-03-03-v171 | Date: 2026-03-03 | Description: Core data logic. Strictly filters Hanja and handles DB persistence for both movies and actors.
# Functions: load_mapping(), get_db_conn(), to_ko(), get_aid(), add_movie_logic()

import sqlite3, os, json

DB_PATH = '/home/bkim/2b/0/db/av_manager.db'
MAP_PATH = '/home/bkim/2b/0/db/mapping.json'

GLOBAL_MAP = {}
def load_mapping():
    global GLOBAL_MAP
    if os.path.exists(MAP_PATH):
        try:
            with open(MAP_PATH, 'r', encoding='utf-8') as f:
                GLOBAL_MAP = json.load(f)
        except: GLOBAL_MAP = {}
load_mapping()

def get_db_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def to_ko(jp_text):
    """매핑 테이블 기반 고속 한글 변환 및 한자 제거"""
    if not jp_text: return ""
    res = "".join([GLOBAL_MAP.get(c, c if c in ", " else "") for c in jp_text]).strip()
    return res if res else "미분류"

def get_aid(conn, jp_name):
    cur = conn.cursor()
    ko_name = to_ko(jp_name)
    cur.execute("SELECT id FROM actors WHERE name_ko = ?", (ko_name,))
    row = cur.fetchone()
    if row: return row[0]
    cur.execute("INSERT INTO actors (name_ko, name_jp, hair, height, note) VALUES (?, ?, '0', 0, '')", (ko_name, jp_name))
    return cur.lastrowid

def add_movie_logic(data):
    """dvd_id=품번, code=사이트ID 고정 저장 로직"""
    dvd_id = data.get('dvd_id', '').strip()
    code = data.get('code', '').strip()
    if not dvd_id: return False, "DVD ID Missing"
    
    clean_actors_raw = to_ko(data.get('actors_raw', ''))
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM dvds WHERE dvd_id = ?", (dvd_id,))
        exists = cur.fetchone()
        t, r, sub = data.get('title',''), data.get('release_date',''), int(data.get('subtitle',0))
        
        if exists:
            cur.execute("UPDATE dvds SET code=?, title=?, release_date=?, actors_raw=?, subtitle=? WHERE id=?", 
                        (code, t, r, clean_actors_raw, sub, exists[0]))
            d_ref = exists[0]
        else:
            cur.execute("INSERT INTO dvds (dvd_id, code, title, release_date, actors_raw, subtitle, note) VALUES (?, ?, ?, ?, ?, ?, '')", 
                        (dvd_id, code, t, r, clean_actors_raw, sub))
            d_ref = cur.lastrowid
            
        if data.get('actors_raw'):
            for name in [n.strip() for n in data['actors_raw'].split(',') if n.strip()]:
                a_id = get_aid(conn, name)
                cur.execute("INSERT OR IGNORE INTO dvd_actors (dvd_id_ref, actor_id) VALUES (?, ?)", (d_ref, a_id))
        conn.commit()
        return True, dvd_id
    except: return False, "DB Error"
    finally: conn.close()
