#!/home/bkim/2b/0/db/db/bin/python3
# Version: 2026-02-26-v01 | Description: 새로운 시스템 이식을 위한 DB 초기 구조 통합 생성 (actors & dvds)
# Functions: create_tables(), main()

import sqlite3
import os

# 이식할 시스템의 경로에 맞게 수정 가능
DB_PATH = '/home/bkim/2b/0/db/av_manager.db'

def create_tables(cur):
    """현재까지 확정된 모든 테이블 구조를 한 번에 생성"""
    
    # 1. actors 테이블 (배우 정보 상세화 버전)
    print("📋 Creating 'actors' table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ko TEXT,
            name_jp TEXT,
            name_en TEXT,
            birth TEXT,
            name_alter TEXT,
            height INTEGER,
            debut TEXT,
            cup TEXT,
            hair TEXT,
            note TEXT
        )
    """)

    # 2. dvds 테이블 (파일 경로 및 태그 포함 버전)
    print("📋 Creating 'dvds' table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dvds (
            dvd_id TEXT PRIMARY KEY,
            release_date TEXT,
            duration INTEGER,
            actors_raw TEXT,
            highlight_path TEXT,
            subtitle_path TEXT,
            note TEXT
        )
    """)

    # 3. dvd_actors 연결 테이블 (N:M 관계)
    print("📋 Creating 'dvd_actors' table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dvd_actors (
            dvd_id TEXT,
            actor_id INTEGER,
            FOREIGN KEY(dvd_id) REFERENCES dvds(dvd_id),
            FOREIGN KEY(actor_id) REFERENCES actors(id),
            PRIMARY KEY (dvd_id, actor_id)
        )
    """)

def main():
    # 경로 디렉토리가 없다면 생성
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"📁 Created directory: {db_dir}")

    if os.path.exists(DB_PATH):
        confirm = input(f"⚠️ {DB_PATH}가 이미 존재합니다. 삭제 후 새로 만드시겠습니까? (y/N): ")
        if confirm.lower() == 'y':
            os.remove(DB_PATH)
            print("🗑️ Existing DB removed.")
        else:
            print("🚫 Operation cancelled.")
            return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        create_tables(cur)
        
        conn.commit()
        print(f"\n✅ Database setup complete: {DB_PATH}")
        print("이제 다른 시스템에서 관리 도구(db_edit.py 등)를 즉시 사용할 수 있습니다.")

    except Exception as e:
        print(f"❌ Error during setup: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
