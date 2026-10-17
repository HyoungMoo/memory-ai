Memory Recall AI | 기억 회상 AI 시스템
고령자의 추억을 대화로 연결하는 개인 맞춤형 AI 회상 웹서비스

개인 프로젝트 · 개발 기간: 2025.11 ~ 2025.12
기술 스택: Python · Flask · SQLite · OpenAI API (GPT-3.5) · HTML/CSS/JavaScript
1. 프로젝트 소개
고령화 사회에서 고령자의 정서적 고립과 인지 건강은 중요한 과제입니다. **기억 회상 요법(Reminiscence Therapy)**은 과거의 경험을 떠올리고 이야기하는 활동을 통해 정서적 교류와 인지 자극을 지원하는 비약물적 접근입니다.
이 프로젝트는 기억 회상 활동에 GPT 기반 대화 시스템을 접목한 개인 개발 프로젝트입니다. 사용자 정보와 저장된 추억을 바탕으로 회상 질문을 제공하고, 대화 내용을 기록하여 사용자가 자신의 경험을 이어서 이야기할 수 있도록 설계했습니다. 음성 입력과 회상 내용에 연관된 이미지 표시 기능을 통해 고령자의 사용 편의성과 회상 경험도 고려했습니다.
안내: 이 프로젝트는 기억 회상 활동을 지원하기 위한 연구·학습용 시제품입니다. 치매 예방, 인지 기능 개선 또는 치료 효과가 임상적으로 검증된 의료 서비스는 아닙니다.

2. 개발 목표
- 개인화된 회상: 사용자 프로필과 과거 기억을 바탕으로 관련 질문 및 AI 응답 생성
- 대화 접근성: 키보드 입력 외에 브라우저 음성 인식(STT)을 통한 음성 입력 지원
- 시각적 자극: 대화 키워드에 연결된 이미지와 사용자 등록 사진 제공
- 기억의 연속성: 대화 기록, 회상 세션 및 기억 데이터를 SQLite에 저장
- 회상 활동 기록: 회상 결과를 확인할 수 있는 통계·보고서 화면 제공
3. 주요 기능
기능	구현 내용
AI 대화	OpenAI GPT-3.5 모델을 호출해 대화 맥락에 맞는 응답 생성
맞춤형 회상 질문	사용자 기억과 회상 주제를 반영한 질문 생성 및 답변 기록
기억 저장·검색	SQLite 기반 기억 관리, 임베딩·코사인 유사도를 활용한 관련 기억 검색 로직
감정 분석	사용자 발화에 대한 감정 분류
대화 요약	일정 대화 횟수마다 대화 내용을 요약해 기록하는 로직
음성 입력(STT)	브라우저 SpeechRecognition / webkitSpeechRecognition을 이용한 한국어 음성 입력
이미지 연계	등록된 개인 사진 또는 미리 정의된 이미지와 대화 키워드 매칭
회상 기록	회상 세션, 결과 통계 및 보고서 조회 기능


구현 범위에 관한 안내
원래 기획에는 음성 합성(TTS) 및 실시간 외부 이미지 검색도 포함되어 있습니다. 다만 현재 공개 대상 소스에서는 브라우저 STT와 키워드 기반 이미지 매칭을 확인할 수 있으며, TTS 및 외부 이미지 검색 API 연동은 구현 완료 기능으로 표기하지 않았습니다. 또한 임베딩 기반 검색 로직은 존재하지만 모든 기억이 자동으로 임베딩되는 구조는 아닙니다.
4. 기술 스택
구분	기술
Backend	Python, Flask, Flask Blueprint
Database	SQLite
AI	OpenAI Python SDK, gpt-3.5-turbo, text-embedding-ada-002
Frontend	HTML, CSS, JavaScript, Flask Templates
Voice	Web Speech API (브라우저 STT), Python SpeechRecognition 유틸리티
Test	unittest, unittest.mock


5. 시스템 구성
사용자 (웹 브라우저)
  ├─ 프로필 입력 / 채팅 / 회상 세션 / 음성 입력(STT)
  └─ Flask 웹 애플리케이션
       ├─ routes/       HTTP 요청 및 응답 처리
       ├─ services/     AI 대화·기억·회상·통계 로직
       │    ├─ OpenAI API (GPT 대화 / 임베딩)
       │    └─ 기억 검색 및 회상 질문 생성
       ├─ database/     SQLite 데이터 관리
       └─ templates/    사용자 화면
프로젝트 디렉터리
memory-ai-main/
├── app.py                # Flask 애플리케이션 진입점
├── config.py             # 환경변수 및 앱 설정
├── database/             # DB 연결·초기화·샘플 데이터
├── routes/               # 채팅·사용자·기억·회상·세션·이미지·보고서 API
├── services/             # 비즈니스 로직 및 OpenAI API 연동
├── templates/            # 메인·채팅·통계·보고서 화면
├── utils/                # 이미지 매칭 및 음성 인식 유틸리티
├── tests/                # 서비스 단위 테스트
└── requirements.txt      # Python 의존성
6. OpenAI API 활용
- AI 응답 생성: services/ai_service.py에서 chat.completions.create() 호출
- 감정 분류·요약·회상 질문: GPT-3.5 기반 프롬프트 처리
- 관련 기억 검색: services/rag_service.py에서 embeddings.create()로 임베딩 생성 후 코사인 유사도 비교
- 설정: API 키를 코드에 직접 입력하지 않고 OPENAI_API_KEY 환경변수로 로드
관련 기억에 임베딩이 없는 경우에는 최근 기억을 조회하는 대체 로직이 사용됩니다.
7. 로컬 실행 방법
1) 저장소 준비
git clone https://github.com/HyoungMoo/<repository-name>.git
cd <repository-name>
python -m venv .venv
가상환경 활성화:
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
위 GitHub 주소의 <repository-name>은 실제 저장소 이름으로 변경하세요.

2) 의존성 설치
pip install -r requirements.txt
pip install python-dotenv
현재 원본 requirements.txt에는 python-dotenv가 누락되어 있습니다. 저장소를 정리할 때 추가하는 것을 권장합니다. pyaudio는 운영체제에 따라 설치에 추가 설정이 필요할 수 있습니다.

3) 환경변수 설정
프로젝트 루트에 .env 파일을 생성합니다.
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=replace-with-a-secure-random-value
DB_PATH=memory.db
DEBUG=true
4) 서버 실행
python app.py
브라우저에서 http://127.0.0.1:5000에 접속합니다. 앱 실행 시 SQLite 테이블 초기화가 수행됩니다.
주의: .env, 실제 API 키, 개인정보가 포함된 DB 파일은 GitHub에 업로드하지 마세요. API 사용에는 계정 설정 및 비용이 발생할 수 있습니다.
8. 테스트
서비스 로직에 대한 unittest 기반 테스트 코드가 tests/test_services.py에 포함되어 있습니다.
python -m unittest discover -s tests -v
테스트 코드의 존재는 확인했지만, 현재 환경에서 실제 실행 및 전체 테스트 통과까지 검증한 것은 아닙니다.

9. 향후 개선 과제
- 브라우저 음성 합성(TTS) 기능 추가 및 음성 중심 UI 개선
- 외부 이미지 검색 API 연동과 이미지 출처·저작권 관리
- 사용자 인증·권한 검증 및 개인정보 보호 강화
- 기억 저장 과정의 임베딩 생성 흐름 통합
- 입력값 검증, 오류 처리 및 자동화 테스트 보완
- 실제 고령자 대상 사용성 평가를 통한 접근성·회상 경험 검증
10. 프로젝트를 통해 경험한 점
개인 프로젝트로 Flask 웹서비스의 API 구조와 데이터베이스를 구성하고, OpenAI API를 활용한 대화 기능을 연결했습니다. 특히 사용자 정보를 기반으로 회상 질문을 만들고, 저장된 기억을 다음 대화에 활용하는 흐름을 설계·구현하면서 AI 기능을 사용자 목적에 맞게 연결하는 경험을 했습니다.
