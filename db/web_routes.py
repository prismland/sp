# Version: 2026-03-03-v212 | Date: 2026-03-03 | Description: Emergency fix for route syntax errors to prevent plain text exposure.
# Functions: init_routes(), index(), dvd_detail(), actor_detail(), update_actor(), update_dvd(), get_image()

from flask import request, render_template, send_from_directory, jsonify
import os, math
from models import get_db_conn

IMAGE_DIR = '/home/bkim/2b/b/8/images/covers'
PER_PAGE = 24

def init_routes(app):
    @app.route('/')
    def index():
        q = request.args.get('search', '').strip()
        sub_only = request.args.get('sub_only') == '1'
        hair_only = request.args.get('hair_only') == '1'
        exclude_noteworthy_actors = request.args.get('exclude_noteworthy_actors') == '1'
        page = request.args.get('page', 1, type=int)

        # 정렬 추가
        sort = request.args.get('sort', 'release_date')
        # 정렬 필드 검증 (허용된 값만 쿼리에 넣기 위함)
        sort_field = "d.release_date" if sort == "release_date" else "d.id"
        
        conn = get_db_conn()
        where_clauses, params = [], []
        if q:
            keywords = q.split()
            for kw in keywords:
                p = f"%{kw}%"
                where_clauses.append(f"(d.dvd_id LIKE ? OR d.title LIKE ? OR d.actors_raw LIKE ? OR d.id IN (SELECT da.dvd_id_ref FROM dvd_actors da JOIN actors a ON da.actor_id = a.id WHERE a.name_ko LIKE ? OR a.name_jp LIKE ? OR a.name_en LIKE ? OR a.name_alter LIKE ?))")
                params.extend([p, p, p, p, p, p, p])
        if sub_only:
            where_clauses.append("(d.subtitle != '0' AND d.subtitle IS NOT NULL AND d.subtitle != '')")
        if hair_only:
            where_clauses.append("d.id IN (SELECT da.dvd_id_ref FROM dvd_actors da JOIN actors a ON da.actor_id = a.id WHERE CAST(NULLIF(TRIM(a.hair), '') AS INTEGER) > 0)")
        
        if exclude_noteworthy_actors:
            # 배우의 note 컬럼에 '점' 또는 '의슴'이 포함된 DVD 제외
            where_clauses.append("""
                d.id NOT IN (
                    SELECT da.dvd_id_ref
                    FROM dvd_actors da
                    JOIN actors a ON da.actor_id = a.id
                    WHERE a.note LIKE '%점%' OR a.note LIKE '%의슴%'
                )
            """)
        
        ws = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        total_count = conn.execute(f"SELECT COUNT(DISTINCT d.id) FROM dvds d {ws}", params).fetchone()[0]
        total_pages = math.ceil(total_count / PER_PAGE)
        offset = (page - 1) * PER_PAGE

        # 쿼리 실행 (동적으로 sort_field 적용)
        # 기존 코드의 ORDER BY 부분을 수정합니다.
        query = f"""
            SELECT DISTINCT d.* FROM dvds d {ws} 
            ORDER BY {sort_field} DESC, d.id DESC 
            LIMIT ? OFFSET ?
        """
        
        rows = conn.execute(query, params + [PER_PAGE, offset]).fetchall()
        #rows = conn.execute(f"SELECT DISTINCT d.* FROM dvds d {ws} ORDER BY d.release_date DESC, d.id DESC LIMIT ? OFFSET ?", params + [PER_PAGE, offset]).fetchall()
        
        items = []
        for r in rows:
            di = dict(r)
            di['actors'] = conn.execute("SELECT a.id, a.name_ko, a.hair FROM actors a JOIN dvd_actors da ON a.id = da.actor_id WHERE da.dvd_id_ref = ?", (r['id'],)).fetchall()
            items.append(di)
        conn.close()
        #return render_template('index.html', items=items, q=q, sub_only=sub_only, hair_only=hair_only, exclude_noteworthy_actors=exclude_noteworthy_actors, page=page, total_pages=total_pages)
        return render_template('index.html', sort=sort, items=items, q=q, sub_only=sub_only, hair_only=hair_only, exclude_noteworthy_actors=exclude_noteworthy_actors, page=page, total_pages=total_pages)

    @app.route('/dvd/<int:dvd_id_ref>')
    def dvd_detail(dvd_id_ref):
        conn = get_db_conn()
        dvd = conn.execute("SELECT * FROM dvds WHERE id = ?", (dvd_id_ref,)).fetchone()
        actors = conn.execute("SELECT a.id, a.name_ko, a.hair FROM actors a JOIN dvd_actors da ON a.id = da.actor_id WHERE da.dvd_id_ref = ?", (dvd_id_ref,)).fetchall()
        conn.close()
        return render_template('dvd_detail.html', dvd=dvd, actors=actors)

    @app.route('/actor/<int:actor_id>')
    def actor_detail(actor_id):
        conn = get_db_conn()
        actor = conn.execute("SELECT * FROM actors WHERE id = ?", (actor_id,)).fetchone()
        
        # 해당 배우의 이름을 가져와서 actors_raw 검색에도 사용 (매핑 전 이름도 고려)
        a_names = [actor['name_ko']]
        if actor['name_jp']: a_names.append(actor['name_jp'])
        
        # 검색 조건 생성: dvd_actors 관계 또는 actors_raw 텍스트 매칭
        # actor_detail 페이지에서는 필터링 조건 없이 해당 배우의 모든 출연작을 무조건 출력
        dvds = conn.execute(f"""
            SELECT DISTINCT d.* 
            FROM dvds d 
            LEFT JOIN dvd_actors da ON d.id = da.dvd_id_ref 
            WHERE (da.actor_id = ? OR {" OR ".join(["d.actors_raw LIKE ?" for _ in a_names])})
            ORDER BY d.release_date DESC, d.id DESC
        """, [actor_id] + [f"%{n}%" for n in a_names]).fetchall()
        
        conn.close()
        return render_template('actor_detail.html', actor=actor, dvds=dvds)

    @app.route('/update_actor', methods=['POST'])
    def update_actor():
        data = request.json
        try:
            conn = get_db_conn()
            conn.execute("UPDATE actors SET hair = ?, note = ? WHERE id = ?", (data.get('hair'), data.get('note'), data.get('id')))
            conn.commit()
            conn.close()
            return jsonify({"status": "success"})
        except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/update_dvd', methods=['POST'])
    def update_dvd():
        data = request.json
        try:
            conn = get_db_conn()
            conn.execute("UPDATE dvds SET note = ? WHERE id = ?", (data.get('note'), data.get('id')))
            conn.commit()
            conn.close()
            return jsonify({"status": "success"})
        except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/images/covers/<path:filename>')
    def get_image(filename):
        target = filename.upper()
        try:
            files = os.listdir(IMAGE_DIR)
            match = next((f for f in files if f.upper().startswith(target)), None)
            if match: return send_from_directory(IMAGE_DIR, match)
            return "404", 404
        except: return "500", 500
