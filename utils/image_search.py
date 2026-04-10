from __future__ import annotations

from database.db import get_connection

KEYWORD_MAP = {
    "아들": "son.jpg",
    "딸": "daughter.jpg",
    "손자": "grandson.jpg",
    "손녀": "granddaughter.jpg",
    "아내": "wife.jpg",
    "남편": "husband.jpg",
    "가족": "family.jpg",
    "봄": "spring.jpg",
    "여름": "summer.jpg",
    "가을": "autumn.jpg",
    "겨울": "winter.jpg",
    "고향": "hometown.jpg",
    "학교": "school.jpg",
    "결혼": "wedding.jpg",
}


def get_image_by_keyword(text: str, user_id: int = None) -> str | None:
    # 1순위: 사용자 개인 사진 DB 조회
    if user_id:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT filename FROM user_images WHERE user_id = ?",
            (user_id,),
        )
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            keyword = row["filename"].rsplit(".", 1)[0]  # 파일명 앞부분을 키워드로 사용
            if keyword in text:
                return f"/static/images/users/{user_id}/{row['filename']}"

        # keyword 컬럼으로도 검색
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT keyword, filename FROM user_images WHERE user_id = ?",
            (user_id,),
        )
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            if row["keyword"] in text:
                return f"/static/images/users/{user_id}/{row['filename']}"

    # 2순위: 기본 키워드 맵
    for keyword, filename in KEYWORD_MAP.items():
        if keyword in text:
            return f"/static/images/{filename}"

    return None


def save_user_image(user_id: int, keyword: str, filename: str, description: str = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_images (user_id, keyword, filename, description) VALUES (?, ?, ?, ?)",
        (user_id, keyword, filename, description),
    )
    conn.commit()
    conn.close()


def get_user_images(user_id: int) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM user_images WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
