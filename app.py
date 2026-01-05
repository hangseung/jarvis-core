import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# 1. 환경변수 로드
load_dotenv()

# 2. Gemini 모델 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 3. Slack App 초기화
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# 4. Manifesto 로드 (시스템 프롬프트)
try:
    with open("JARVIS_MANIFESTO.md", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are a helpful AI assistant."
    print("⚠️ Warning: JARVIS_MANIFESTO.md not found. Using default prompt.")

# --- 🤖 공통 AI 답변 함수 ---
def get_ai_response(text):
    try:
        # [시스템 페르소나] + [사용자 질문] 결합
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=text)
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"⚠️ 에러가 발생했습니다: {e}"

# --- 👂 1. 채널 멘션 핸들러 ---
@app.event("app_mention")
def handle_mention(body, say):
    user_text = body["event"]["text"]
    # 멘션 ID(<@U1234>) 제거 처리는 추후 고도화
    say(f"🤖 (분석 중...): {user_text}")
    answer = get_ai_response(user_text)
    say(answer)

# --- 👂 2. DM 핸들러 ---
@app.event("message")
def handle_message(event, say):
    if event.get("subtype") or event.get("bot_id"):
        return

    if event.get("channel_type") == "im":
        user_text = event["text"]
        # say(f"📩 (DM 수신): {user_text}") # 로그가 너무 시끄러우면 주석 처리
        
        answer = get_ai_response(user_text)
        say(answer)

# --- ❤️ 서버 실행 ---
if __name__ == "__main__":
    print("⚡️ Jarvis Core(Mk1) is active on Socket Mode!")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()