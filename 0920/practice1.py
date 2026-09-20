from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
import hmac
import hashlib
import base64

# 載入環境變數
load_dotenv()

# LINE Bot 設定
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

# Gemini API 設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 初始化 Gemini 客戶端
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FastAPI 簡單網頁</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 歡迎使用 FastAPI!</h1>
            <p>這是一個簡單的 FastAPI 網頁應用程式</p>
            <p>運行於 Port 8000</p>
        </div>
    </body>
    </html>
    """
    return html_content

def verify_line_signature(body: bytes, signature: str) -> bool:
    """驗證 LINE 請求的簽章"""
    if not LINE_CHANNEL_SECRET:
        return True  # 開發模式下可以暫時略過
    
    hash_value = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    
    calculated_signature = base64.b64encode(hash_value).decode('utf-8')
    return hmac.compare_digest(calculated_signature, signature)


async def get_gemini_response(user_message: str) -> str:
    """
    使用 Gemini API 生成回應
    """
    try:
        system_instruction = """
        你是一個友善且樂於助人的 LINE Bot 助理。
        請用繁體中文回覆使用者的問題。
        回答要簡潔明瞭，語氣親切自然。
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
        return "抱歉，我現在無法處理您的訊息，請稍後再試。"


async def send_line_reply(reply_token: str, message: str):
    """
    發送回覆訊息給 LINE 使用者
    """
    import aiohttp
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"❌ LINE API 回覆失敗: {error_text}")
            else:
                print("✅ 成功回覆 LINE 訊息")


@app.post("/webhook")
async def line_webhook(request: Request):
    """
    LINE Webhook 專用節點
    接收 LINE 的 webhook 請求，使用 Gemini API 處理並回覆
    """
    # 取得簽章進行驗證
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    
    # 驗證請求來源
    if not verify_line_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 解析 JSON 資料
    try:
        events = json.loads(body.decode('utf-8'))
        print(f"📩 收到 webhook 資料: {events}")
        
        # 處理每一個事件
        for event in events.get("events", []):
            # 只處理文字訊息
            if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
                reply_token = event.get("replyToken")
                user_message = event.get("message", {}).get("text", "")
                user_id = event.get("source", {}).get("userId", "unknown")
                
                print(f"👤 使用者 {user_id} 說: {user_message}")
                
                # 使用 Gemini 生成回應
                ai_response = await get_gemini_response(user_message)
                print(f"🤖 Gemini 回應: {ai_response}")
                
                # 回覆給使用者
                await send_line_reply(reply_token, ai_response)
        
    except Exception as e:
        print(f"❌ 處理 webhook 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # 回傳 status ok 給 LINE 伺服器
    return JSONResponse(content={"status": "ok"}, status_code=200)

if __name__ == "__main__":
    # 使用 port 8000 - 不需要 root 權限
    uvicorn.run(app, host="0.0.0.0", port=8000)