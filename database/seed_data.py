"""
테스트용 시드 데이터 삽입
실행: venv\\Scripts\\python database/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.user_service import create_user
from services.rag_service import save_memory_with_embedding
from services.memory_service import save_conversation
from database.db import get_connection


def clear_test_data():
    conn = get_connection()
    conn.execute("DELETE FROM conversations")
    conn.execute("DELETE FROM memories")
    conn.execute("DELETE FROM users")
    conn.execute("DELETE FROM sqlite_sequence")  # auto increment 리셋
    conn.commit()
    conn.close()
    print("기존 데이터 삭제 완료")


def seed():
    clear_test_data()

    # ── 사용자 1: 김영자 (75세, 서울 거주, 전업주부 출신) ──────────────
    uid1 = create_user("김영자", 75)
    memories1 = [
        ("아들 민준이는 서울 강남구 역삼동에 살고 있다",          "그리움",  "아들"),
        ("딸 수진이는 부산에서 초등학교 교사를 하고 있다",         "행복",   "딸"),
        ("손자 지호는 8살이고 태권도를 배우고 있다",              "행복",   "손자"),
        ("남편은 2018년에 세상을 떠났다. 40년을 함께 살았다",      "슬픔",   "남편"),
        ("고향은 경상남도 진주시 망경동이다",                     "그리움",  "고향"),
        ("1975년 봄에 진주 시내 한복집에서 남편을 처음 만났다",     "설렘",   "결혼"),
        ("1977년 10월 결혼식을 진주 중앙예식장에서 올렸다",        "행복",   "결혼"),
        ("젊었을 때 김치찌개와 된장찌개를 특히 잘 만들었다",        "행복",   "음식"),
        ("요즘 무릎이 아파서 계단 오르기가 힘들다",               "불안",   "건강"),
        ("매주 화요일에 복지관에서 노래교실을 다닌다",             "평온",   "취미"),
        ("남편과 제주도로 신혼여행을 갔다. 한라산이 아름다웠다",    "그리움",  "여행"),
        ("아들 민준이가 어릴 때 열이 심하게 나서 밤새 간호했던 기억이 있다", "그리움", "아들"),
    ]
    for content, emotion, keyword in memories1:
        save_memory_with_embedding(uid1, content, emotion, keyword)
        print(f"  [김영자] {content[:30]}...")

    # 대화 샘플
    convs1 = [
        ("user",      "오늘 아들한테서 전화가 왔어요"),
        ("assistant", "아, 민준이씨한테서요! 반가우셨겠네요. 무슨 이야기를 하셨어요?"),
        ("user",      "주말에 온다고 하더라고요. 오랜만이에요"),
        ("assistant", "정말 기쁘시겠어요. 오시면 좋아하시는 음식 해드릴 건가요?"),
        ("user",      "김치찌개 끓여줘야죠"),
    ]
    for role, msg in convs1:
        save_conversation(uid1, role, msg)

    # ── 사용자 2: 박철수 (72세, 부산 거주, 은퇴 교사) ────────────────
    uid2 = create_user("박철수", 72)
    memories2 = [
        ("부산 해운대구 좌동에 산다",                            "평온",   "집"),
        ("40년간 중학교 수학 교사로 근무하다 2019년에 퇴직했다",   "행복",   "직업"),
        ("아내 이름은 최순희이고 올해 70세다",                    "행복",   "아내"),
        ("아들 박성민은 대전에서 IT 회사를 다닌다",               "행복",   "아들"),
        ("딸 박지연은 결혼해서 캐나다 토론토에 살고 있다",         "그리움",  "딸"),
        ("손녀 박하은이 5살인데 캐나다에 있어서 자주 못 본다",     "그리움",  "손녀"),
        ("고향은 경남 통영이다. 바다가 아름다운 곳이다",           "그리움",  "고향"),
        ("젊었을 때 낚시를 즐겼다. 통영 앞바다에서 자주 낚시했다", "그리움",  "취미"),
        ("요즘 혈압이 높아 약을 매일 먹고 있다",                  "불안",   "건강"),
        ("매일 아침 6시에 일어나 해운대 해변을 30분 산책한다",     "평온",   "운동"),
        ("가장 기억에 남는 제자는 1989년 담임 맡은 3학년 학생들이다", "행복", "직업"),
        ("퇴직 후 아내와 유럽 여행을 다녀왔다. 파리가 제일 좋았다", "행복",  "여행"),
    ]
    for content, emotion, keyword in memories2:
        save_memory_with_embedding(uid2, content, emotion, keyword)
        print(f"  [박철수] {content[:30]}...")

    convs2 = [
        ("user",      "오늘 아침에 바다 산책했어요"),
        ("assistant", "해운대 바다 공기는 참 좋죠. 오늘은 날씨가 어땠나요?"),
        ("user",      "바람이 좀 불었는데 상쾌했어요. 고향 통영 생각이 나더라고"),
        ("assistant", "통영 바다도 그리우시겠네요. 통영에서 낚시하실 때 어떤 물고기를 잡으셨어요?"),
        ("user",      "감성돔을 제일 좋아했지. 손맛이 달랐어"),
    ]
    for role, msg in convs2:
        save_conversation(uid2, role, msg)

    # ── 사용자 3: 이순례 (80세, 대구 거주, 농사 출신) ────────────────
    uid3 = create_user("이순례", 80)
    memories3 = [
        ("대구 달서구 본리동에 아들 내외와 함께 살고 있다",        "평온",   "집"),
        ("경북 안동 하회마을 근처 작은 마을에서 태어났다",         "그리움",  "고향"),
        ("젊었을 때 20년간 논농사와 밭농사를 지었다",             "그리움",  "직업"),
        ("남편은 건설 현장 일을 했고 지금도 건강하게 살고 있다",    "행복",   "남편"),
        ("아들 이재호는 대구에서 식당을 운영한다",                 "행복",   "아들"),
        ("며느리가 음식 솜씨가 좋아 잘 챙겨준다",                 "행복",   "가족"),
        ("손자가 둘인데 중학생과 고등학생이다",                    "행복",   "손자"),
        ("젊었을 때 직접 기른 고추로 고추장을 담갔다",             "그리움",  "음식"),
        ("최근 허리가 많이 아프고 귀도 잘 안 들린다",             "불안",   "건강"),
        ("안동 하회마을 탈춤 축제를 어릴 때 자주 구경했다",        "그리움",  "고향"),
        ("6남매 중 셋째로 태어났다. 오빠 둘, 남동생 셋이 있었다",  "그리움",  "가족"),
        ("1990년대에 아들 재호가 대학에 합격했을 때 너무 기뻤다",  "행복",   "아들"),
    ]
    for content, emotion, keyword in memories3:
        save_memory_with_embedding(uid3, content, emotion, keyword)
        print(f"  [이순례] {content[:30]}...")

    convs3 = [
        ("user",      "오늘 며느리가 미역국을 끓여줬어요"),
        ("assistant", "따뜻하게 챙겨줘서 좋으셨겠어요. 무슨 날이었나요?"),
        ("user",      "내 생일이에요. 여든이 됐어"),
        ("assistant", "생신 축하드려요! 여든 생신이라니 정말 뜻깊으시겠어요. 가족들이랑 함께 드셨어요?"),
        ("user",      "아들이랑 손자들이랑 다같이 먹었지요. 오랜만에 다들 모였어"),
    ]
    for role, msg in convs3:
        save_conversation(uid3, role, msg)

    print()
    print(f"시드 데이터 삽입 완료!")
    print(f"  사용자 3명 (id: {uid1}, {uid2}, {uid3})")
    print(f"  기억 {len(memories1) + len(memories2) + len(memories3)}개")
    print(f"  대화 {len(convs1) + len(convs2) + len(convs3)}건")


if __name__ == "__main__":
    seed()
