from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# LINE Bot SDK
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# 載入環境變數
load_dotenv()

# LINE Bot 設定
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

# Gemini API 設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 初始化 Gemini 客戶端
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# 初始化 LINE Bot
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """首頁 - 顯示歡迎訊息"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LINE Bot + Gemini AI</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #06C755 0%, #00B900 100%);
            }
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                color: #06C755;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                font-size: 18px;
            }
            .emoji {
                font-size: 48px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🤖💬</div>
            <h1>LINE Bot + Gemini AI</h1>
            <p>智慧聊天機器人已啟動!</p>
            <p>運行於 Port 8000</p>
        </div>
    </body>
    </html>
    """
    return html_content


def get_gemini_response(user_message: str) -> str:
    """
    使用 Gemini API 生成回應
    """
    try:
        system_instruction = """
        你是一個友善且樂於助人的 LINE Bot 助理。
        請用繁體中文回覆使用者的問題。
        回答要簡潔明瞭,語氣親切自然。
        """
        
        response = gemini_client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            ),
        )
        
        return response.text
    except Exception as e:
        print(f"❌ Gemini API 錯誤: {e}")
        return "抱歉,我現在無法處理您的訊息,請稍後再試。"


# LINE Bot 訊息處理器
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """
    處理 LINE 文字訊息事件
    當使用者發送訊息時,這個函式會被自動呼叫
    """
    user_message = event.message.text
    user_id = event.source.user_id
    
    print(f"👤 使用者 {user_id} 說: {user_message}")
    
    # 使用 Gemini 生成回應
    ai_response = get_gemini_response(user_message)
    print(f"🤖 Gemini 回應: {ai_response}")
    
    # 使用 LINE Bot SDK 回覆訊息
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_response)]
            )
        )
    
    print("✅ 成功回覆 LINE 訊息")


@app.post("/webhook")
async def webhook(request: Request):
    """
    LINE Webhook 端點
    接收 LINE 平台發送的事件通知
    """
    # 取得 LINE 的簽章,用於驗證請求來源
    signature = request.headers.get("X-Line-Signature", "")
    
    # 取得 request body
    body = await request.body()
    body_str = body.decode('utf-8')
    
    print(f"📩 收到 webhook 請求")
    
    try:
        # 使用 LINE Bot SDK 的 handler 處理 webhook
        # 會自動驗證簽章並呼叫對應的處理器
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        print("❌ 簽章驗證失敗 - 請求可能不是來自 LINE 平台")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"❌ 處理 webhook 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return "OK"


if __name__ == "__main__":
    print("🚀 啟動 LINE Bot + Gemini AI 服務...")
    print("📝 請確認 .env 中已設定:")
    print("   - LINE_CHANNEL_SECRET")
    print("   - LINE_CHANNEL_ACCESS_TOKEN")
    print("   - GEMINI_API_KEY")
    print("\n💡 伺服器運行於: http://0.0.0.0:8000")
    print("💡 Webhook URL: http://你的網址/webhook\n")
    
    # 使用 port 8000 - 不需要 root 權限
    uvicorn.run(app, host="0.0.0.0", port=8000)
