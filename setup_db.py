#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-28-v03.0 | Description: 품번 최우선 배치 및 javdb 고유코드(code) 필드 분리
# Functions: backup_existing_db(), create_tables(), main()

import sqlite3
import os
import time

DB_PATH = "/home/bkim/2b/0/db/av_manager.db"

def create_tables():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH) # 기존 파일 삭제 요청 반영
        print("🗑️ 기존 DB 파일을 삭제했습니다.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 배우 테이블 (name_alter는 비워둠, name_ko는 변환용)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS actors (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name_ko     TEXT NOT NULL,
        name_jp     TEXT,
        name_alter  TEXT,
        hair        INTEGER DEFAULT 0,
        height      INTEGER DEFAULT 0,
        cup         TEXT,
        note        TEXT,
        name_en     TEXT,
        birth       TEXT,
        debut       TEXT
    )
    """)

    # 2. 작품 테이블 (필드 순서: dvd_id(품번) 최우선, code는 고유식별값)
    # id, dvd_id, actors_raw, subtitle, note, release_date, title, code, topgirl, av123, highlight
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dvds (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        dvd_id       TEXT UNIQUE NOT NULL, -- 품번 (예: SNOS-161)
        actors_raw   TEXT,
        subtitle     INTEGER DEFAULT 0,
        note         TEXT,
        release_date TEXT,
        title        TEXT,
        code         TEXT,                 -- javdb 고유코드 (예: BzPp5O)
        topgirl      INTEGER DEFAULT 0,
        av123        INTEGER DEFAULT 0,
        highlight    INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dvd_actors (
        dvd_id_ref INTEGER,
        actor_id   INTEGER,
        FOREIGN KEY(dvd_id_ref) REFERENCES dvds(id),
        FOREIGN KEY(actor_id) REFERENCES actors(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ 품번(dvd_id) 중심의 신규 스키마 생성이 완료되었습니다.")

if __name__ == "__main__":
    create_tables()
