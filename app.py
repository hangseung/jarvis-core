import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. 환경변수 로드
load_dotenv()

# 2. Gemini 모델 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# 3. Slack App 초기화
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# --- 🤖 공통 AI 답변 함수 ---
def get_ai_response(text):
    try:
        response = llm.invoke(text)
        return response.content
    except Exception as e:
        return f"⚠️ 에러가 발생했습니다: {e}"

# --- 👂 1. 채널에서 멘션했을 때 (@Jarvis 안녕) ---
@app.event("app_mention")
def handle_mention(body, say):
    user_text = body["event"]["text"]
    # 멘션 부분(<@U1234>)이 텍스트에 포함되므로, AI가 헷갈리지 않게 처리하면 좋지만 일단 그냥 보냄
    say(f"🤖 (채널) 분석 중...: {user_text}")
    
    answer = get_ai_response(user_text)
    say(answer)

# --- 👂 2. DM(1:1)으로 말을 걸었을 때 ---
@app.event("message")
def handle_message(event, say):
    # 봇 자신이 보낸 메시지나, 메시지 수정 이벤트 등은 무시 (무한루프 방지)
    if event.get("subtype") or event.get("bot_id"):
        return

    # DM(im)인 경우에만 반응하도록 설정 (채널 잡담에 끼어들지 않게)
    if event.get("channel_type") == "im":
        user_text = event["text"]
        say(f"📩 (DM) 생각 중...: {user_text}")
        
        answer = get_ai_response(user_text)
        say(answer)

# --- ❤️ 서버 실행 ---
if __name__ == "__main__":
    print("⚡️ Jarvis Core(Mk1) is active on Socket Mode!")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

