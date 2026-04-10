"""
유닛 테스트 - OpenAI API 없이 실행 가능 (mock 사용)
실행: venv\\Scripts\\python -m pytest tests/ -v
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Config.DB_PATH를 테스트용 임시 파일로 교체 (모듈 import 전에 설정)
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["DB_PATH"] = _tmp_db.name  # config.py가 env 변수를 읽으므로 적용됨

import unittest
from unittest.mock import patch, MagicMock

# DB 초기화 (테스트 시작 전 한 번만)
from database.init_db import init_db
init_db()


class TestUserService(unittest.TestCase):

    def setUp(self):
        # 각 테스트 전 테이블 초기화
        import sqlite3
        from config import Config
        conn = sqlite3.connect(Config.DB_PATH)
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM memories")
        conn.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()

    def test_create_and_get_user(self):
        from services.user_service import create_user, get_user
        uid = create_user("홍길동", 72)
        self.assertIsNotNone(uid)
        user = get_user(uid)
        self.assertEqual(user["name"], "홍길동")
        self.assertEqual(user["age"], 72)

    def test_get_nonexistent_user(self):
        from services.user_service import get_user
        self.assertIsNone(get_user(9999))

    def test_get_all_users(self):
        from services.user_service import create_user, get_all_users
        create_user("김철수", 68)
        create_user("이영희", 75)
        users = get_all_users()
        self.assertEqual(len(users), 2)


class TestMemoryService(unittest.TestCase):

    def setUp(self):
        import sqlite3
        from config import Config
        from services.user_service import create_user
        conn = sqlite3.connect(Config.DB_PATH)
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM memories")
        conn.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()
        self.user_id = create_user("테스트", 70)

    def test_save_and_get_memory(self):
        from services.memory_service import save_memory, get_memories
        save_memory(self.user_id, "아들이 서울에 산다", "행복", "아들")
        memories = get_memories(self.user_id)
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]["content"], "아들이 서울에 산다")
        self.assertEqual(memories[0]["emotion"], "행복")

    def test_memory_context_empty(self):
        from services.memory_service import get_memory_context
        context = get_memory_context(self.user_id)
        self.assertEqual(context, "등록된 기억이 없습니다.")

    def test_memory_context_with_data(self):
        from services.memory_service import save_memory, get_memory_context
        save_memory(self.user_id, "고향은 부산이다", "그리움")
        context = get_memory_context(self.user_id)
        self.assertIn("부산", context)
        self.assertIn("그리움", context)

    def test_conversation_count(self):
        from services.memory_service import save_conversation, get_conversation_count
        save_conversation(self.user_id, "user", "안녕하세요")
        save_conversation(self.user_id, "assistant", "안녕하세요!")
        save_conversation(self.user_id, "user", "오늘 날씨가 좋네요")
        count = get_conversation_count(self.user_id)
        self.assertEqual(count, 2)  # user 발화만 카운트

    def test_multiple_memories(self):
        from services.memory_service import save_memory, get_memories
        save_memory(self.user_id, "딸이 부산에 산다", "평온")
        save_memory(self.user_id, "결혼은 1975년이다", "설렘")
        memories = get_memories(self.user_id)
        self.assertEqual(len(memories), 2)


class TestEmotionAnalysis(unittest.TestCase):

    def test_analyze_emotion_valid(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "행복"
        with patch("services.ai_service._get_client") as mock_get:
            mock_get.return_value.chat.completions.create.return_value = mock_response
            from services.ai_service import analyze_emotion
            self.assertEqual(analyze_emotion("오늘 아들이 와서 너무 좋았어요"), "행복")

    def test_analyze_emotion_fallback(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "모름"  # EMOTIONS에 없는 값
        with patch("services.ai_service._get_client") as mock_get:
            mock_get.return_value.chat.completions.create.return_value = mock_response
            from services.ai_service import analyze_emotion
            self.assertEqual(analyze_emotion("그냥 그래요"), "평온")

    def test_generate_response(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "네, 잘 기억하고 있어요!"
        with patch("services.ai_service._get_client") as mock_get:
            mock_get.return_value.chat.completions.create.return_value = mock_response
            from services.ai_service import generate_response
            result = generate_response("아들 이야기 해줘", "- 아들이 서울에 산다", "김철수")
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)


class TestImageSearch(unittest.TestCase):

    def test_keyword_match(self):
        from utils.image_search import get_image_by_keyword
        self.assertEqual(get_image_by_keyword("아들이 왔어요"), "/static/images/son.jpg")

    def test_no_match(self):
        from utils.image_search import get_image_by_keyword
        self.assertIsNone(get_image_by_keyword("오늘 밥을 먹었어요"))

    def test_season_keyword(self):
        from utils.image_search import get_image_by_keyword
        self.assertEqual(get_image_by_keyword("봄날이 너무 좋아요"), "/static/images/spring.jpg")

    def test_wedding_keyword(self):
        from utils.image_search import get_image_by_keyword
        self.assertEqual(get_image_by_keyword("결혼식 때 기억나요"), "/static/images/wedding.jpg")


def teardown_module(_):
    os.unlink(_tmp_db.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
