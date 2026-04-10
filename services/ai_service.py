from __future__ import annotations

from openai import OpenAI
from config import Config

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY)
    return _client


EMOTIONS = ["행복", "슬픔", "그리움", "불안", "평온", "설렘"]

SESSION_CATEGORIES = {
    "childhood": "유년기 (태어나서 초등학교 입학 전)",
    "school":    "학창시절 (초·중·고등학교)",
    "career":    "직업·사회생활 (일했던 시절)",
    "family":    "결혼·가족 (배우자, 자녀, 손자)",
    "recent":    "최근 생활 (요즘 일상, 건강, 취미)",
}

# ────────────────────────────────────────────────
# 감정 분석
# ────────────────────────────────────────────────
_EMOTION_SYSTEM = f"""
당신은 감정 분류기입니다. 아래 규칙을 반드시 따르세요.

[출력 규칙]
- 반드시 다음 6개 단어 중 하나만 출력하세요: {", ".join(EMOTIONS)}
- 단어 외에 어떤 문자도 출력하지 마세요 (설명, 구두점, 줄바꿈 금지)

[분류 기준]
- 행복: 기쁨, 만족, 감사, 웃음 표현
- 슬픔: 울음, 상실감, 아쉬움, 외로움 표현
- 그리움: 과거 사람/장소/시절을 떠올리는 표현
- 불안: 걱정, 두려움, 긴장 표현
- 평온: 인사말(안녕/반가워 등), 중립적 대화, 감정 없는 짧은 문장
- 설렘: 기대감, 흥분, 새로운 것에 대한 긍정적 반응

[예시]
입력: "안녕하세요" → 평온
입력: "아들이 보고 싶다" → 그리움
입력: "오늘 너무 즐거웠어요" → 행복
입력: "요즘 잠을 못 자요" → 불안
입력: "손자가 다음 주에 온대요" → 설렘
입력: "그냥 있어요" → 평온
""".strip()


def analyze_emotion(text: str) -> str:
    response = _get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": _EMOTION_SYSTEM},
            {"role": "user", "content": text},
        ],
        max_tokens=5,
        temperature=0,
    )
    result = response.choices[0].message.content.strip()
    return result if result in EMOTIONS else "평온"


# ────────────────────────────────────────────────
# 대화 요약
# ────────────────────────────────────────────────
_SUMMARY_SYSTEM = """
당신은 노인 기억 회상 앱의 대화 요약 담당입니다.

[출력 규칙]
- 반드시 2~3문장으로만 작성하세요
- 어르신이 말한 내용을 중심으로 요약하세요 (AI 발화 제외)
- 언급된 인물, 장소, 시절, 감정을 포함하세요
- 존댓말 사용 금지 — 메모 형태로 간결하게 작성
- 추측하거나 없는 내용을 추가하지 마세요

[형식 예시]
아들이 서울에 산다고 언급함. 결혼 초기 부산 생활을 그리워함. 전반적으로 차분하고 회상적인 대화를 나눔.
""".strip()


def summarize_conversations(conversations: list[dict]) -> str:
    lines = "\n".join(
        f"{'어르신' if c['role'] == 'user' else 'AI'}: {c['message']}"
        for c in conversations
    )
    response = _get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": _SUMMARY_SYSTEM},
            {"role": "user", "content": lines},
        ],
        max_tokens=150,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


# ────────────────────────────────────────────────
# 세션 기반 응답 생성
# ────────────────────────────────────────────────
_SESSION_RESPONSE_TEMPLATE = """
당신은 {user_name}님 전담 기억 회상 치료사입니다.

[오늘 회상 주제]
{category_label}

[{user_name}님의 관련 기억]
{memory_context}

[역할]
치매 예방을 위한 회상 치료(Reminiscence Therapy)를 진행합니다.
오늘 주제({category_label})에 집중해서 어르신이 관련 기억을 구체적으로 떠올릴 수 있도록 유도하세요.

[응답 규칙 — 반드시 준수]
1. 오늘 주제와 관련된 질문만 하세요
2. 질문은 마지막에 1개만, 구체적으로 (예: "몇 살 때였나요?", "어떤 느낌이었나요?")
3. 기억이 떠오르면 "맞아요, 그때 ~하셨군요" 처럼 공감하며 구체화
4. 기억 정보에 있는 내용은 자연스럽게 언급해 회상 유도
5. 기억 정보에 없는 내용을 지어내지 말 것
6. 문장 짧게, 쉬운 단어만, 반드시 존댓말
7. 응답 2~4문장 이내

[금지]
- AI/언어모델 정체 언급 금지
- "기억 정보에 따르면" 등 메타 언급 금지
- 주제에서 벗어난 질문 금지
""".strip()

_FREE_RESPONSE_TEMPLATE = """
당신은 {user_name}님 전담 기억 회상 도우미입니다.

[{user_name}님의 기억 정보]
{memory_context}

[응답 규칙 — 반드시 준수]
1. 문장은 짧게 (1문장 = 15자 이내 권장)
2. 질문은 반드시 1개만, 대화 마지막에 배치
3. 어려운 단어 사용 금지 (한자어, 외래어 최소화)
4. 반말 사용 금지 — 항상 존댓말
5. 기억 정보에 있는 내용은 자연스럽게 언급해 공감대 형성
6. 기억 정보에 없는 사실을 지어내거나 추측하지 말 것
7. 부정적 감정(슬픔, 불안)을 표현할 때는 공감 먼저, 긍정적 전환 유도
8. 응답 길이: 2~4문장 이내

[금지 사항]
- "AI입니다", "저는 언어 모델입니다" 등 정체 언급 금지
- "기억 정보에 따르면" 같은 메타 언급 금지
- 같은 질문 반복 금지
""".strip()


def generate_response(
    user_input: str,
    memory_context: str,
    user_name: str = "어르신",
    session_category: str = None,
) -> str:
    if session_category and session_category in SESSION_CATEGORIES:
        template = _SESSION_RESPONSE_TEMPLATE
        system_prompt = template.format(
            user_name=user_name,
            category_label=SESSION_CATEGORIES[session_category],
            memory_context=memory_context or "아직 등록된 기억이 없습니다.",
        )
    else:
        system_prompt = _FREE_RESPONSE_TEMPLATE.format(
            user_name=user_name,
            memory_context=memory_context or "아직 등록된 기억이 없습니다.",
        )

    response = _get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        max_tokens=200,
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()


# ────────────────────────────────────────────────
# 회상 테스트 - 질문 생성
# ────────────────────────────────────────────────
_RECALL_QUESTION_SYSTEM = """
당신은 치매 예방 회상 테스트 출제자입니다.

[역할]
주어진 기억 문장을 바탕으로 노인이 답할 수 있는 간단한 질문을 만드세요.

[출력 형식 — JSON만 출력, 다른 말 금지]
{"question": "질문 내용", "expected": "정답 핵심어"}

[규칙]
- 질문은 짧고 명확하게 (20자 이내)
- 정답은 기억 문장에서 직접 추출 (5단어 이내 핵심어)
- 예/아니오로 답하는 질문 금지
- 어려운 단어 금지

[예시]
기억: "아들 민준이는 서울 강남구 역삼동에 살고 있다"
출력: {"question": "아드님이 사는 동네가 어디인가요?", "expected": "역삼동"}

기억: "1977년 10월 결혼식을 진주 중앙예식장에서 올렸다"
출력: {"question": "결혼식을 어느 달에 올리셨나요?", "expected": "10월"}
""".strip()


def generate_recall_question(memory_content: str) -> dict:
    import json
    response = _get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": _RECALL_QUESTION_SYSTEM},
            {"role": "user", "content": f"기억: {memory_content}"},
        ],
        max_tokens=80,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"question": "이 기억에 대해 말씀해 주실 수 있나요?", "expected": memory_content[:20]}


# ────────────────────────────────────────────────
# 회상 테스트 - 답변 평가
# ────────────────────────────────────────────────
_RECALL_EVAL_SYSTEM = """
당신은 회상 테스트 채점자입니다.

[역할]
어르신의 답변이 정답과 일치하는지 평가하세요.

[출력 형식 — JSON만 출력, 다른 말 금지]
{"success": true or false, "feedback": "한 문장 피드백"}

[규칙]
- 완벽히 일치하지 않아도 핵심 의미가 맞으면 true
- feedback은 따뜻하고 짧게 (20자 이내)
- 정답일 때: 칭찬과 격려
- 오답일 때: 부드럽게 정답 알려주기

[예시]
정답: "역삼동", 답변: "강남에 사는 것 같아요"
출력: {"success": false, "feedback": "역삼동이에요. 잘 기억해보셨어요!"}

정답: "10월", 답변: "가을에 했죠"
출력: {"success": true, "feedback": "맞아요, 가을 10월이었죠!"}
""".strip()


def evaluate_recall_answer(question: str, expected: str, user_answer: str) -> dict:
    import json
    prompt = f"질문: {question}\n정답: {expected}\n어르신 답변: {user_answer}"
    response = _get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": _RECALL_EVAL_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=60,
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"success": False, "feedback": "다시 한번 생각해 보세요."}
