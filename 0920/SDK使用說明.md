# 📚 LINE Bot SDK 使用說明

## ✅ 安裝完成

已成功安裝 `line-bot-sdk` 版本 3.25.0

```bash
uv add line-bot-sdk
```

---

## 🎯 使用 LINE Bot SDK 的優點

### 1. **程式碼更簡潔**
- 不需要手動處理 HTTP 請求
- 不需要自己寫簽章驗證邏輯
- 自動解析 webhook 事件

### 2. **更安全**
- SDK 內建簽章驗證
- 自動處理錯誤

### 3. **更易維護**
- 使用官方提供的類別和方法
- 有完整的型別提示
- 減少出錯機會

---

## 📝 主要改動說明

### 之前 (手動處理)

```python
# 需要自己寫簽章驗證
def verify_line_signature(body: bytes, signature: str) -> bool:
    hash_value = hmac.new(...)
    # ...複雜的驗證邏輯

# 需要手動發送 HTTP 請求
async def send_line_reply(reply_token: str, message: str):
    async with aiohttp.ClientSession() as session:
        await session.post("https://api.line.me/v2/bot/message/reply", ...)

# 需要手動解析 JSON
events = json.loads(body.decode('utf-8'))
for event in events.get("events", []):
    if event.get("type") == "message":
        # ...複雜的條件判斷
```

### 現在 (使用 SDK)

```python
# SDK 自動處理簽章驗證
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 使用裝飾器處理訊息,超級簡單!
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    user_message = event.message.text
    
    # 直接使用 SDK 回覆
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_response)]
            )
        )

# Webhook 端點變得超簡單
@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    
    # 一行搞定!SDK 會自動驗證並呼叫對應的處理器
    handler.handle(body.decode('utf-8'), signature)
    return "OK"
```

---

## 🔧 核心元件說明

### 1. Configuration (配置)

```python
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
```

儲存 LINE Bot 的認證資訊。

### 2. WebhookHandler (事件處理器)

```python
handler = WebhookHandler(LINE_CHANNEL_SECRET)
```

負責:
- 驗證 webhook 簽章
- 解析 webhook 事件
- 呼叫對應的處理函式

### 3. MessagingApi (訊息 API)

```python
with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_api.reply_message_with_http_info(...)
```

用於發送訊息給使用者。

### 4. 事件處理裝飾器

```python
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    # 處理文字訊息
```

當收到符合條件的事件時,自動呼叫這個函式。

---

## 📦 程式架構

```
LINE 使用者發送訊息
    ↓
LINE 平台推送 webhook 到你的伺服器
    ↓
FastAPI 接收 POST /webhook
    ↓
WebhookHandler 驗證簽章
    ↓
WebhookHandler 解析事件類型
    ↓
呼叫 @handler.add 裝飾的函式
    ↓
Gemini API 生成回應
    ↓
MessagingApi 發送回覆
    ↓
使用者收到訊息
```

---

## 🎨 可擴展的功能

### 1. 處理不同類型的訊息

```python
# 處理圖片訊息
@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    print("收到圖片訊息")
    # 處理圖片...

# 處理貼圖訊息
@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    print("收到貼圖訊息")
    # 處理貼圖...
```

### 2. 處理不同事件類型

```python
# 處理加入好友事件
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    print(f"使用者 {user_id} 加入好友!")
    # 發送歡迎訊息...

# 處理取消好友事件
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print("使用者取消好友")
```

### 3. 發送不同類型的訊息

```python
# 發送文字訊息
TextMessage(text="你好!")

# 發送貼圖
StickerMessage(package_id="1", sticker_id="1")

# 發送圖片
ImageMessage(
    original_content_url="https://example.com/image.jpg",
    preview_image_url="https://example.com/preview.jpg"
)

# 發送多則訊息
line_bot_api.reply_message_with_http_info(
    ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[
            TextMessage(text="訊息1"),
            TextMessage(text="訊息2"),
            StickerMessage(package_id="1", sticker_id="1")
        ]
    )
)
```

---

## 🚀 執行方式

### 方法 1: 直接執行

```bash
cd /home/pi/Documents/github/test-class/0920
uv run python practice1.py
```

### 方法 2: 使用 uvicorn

```bash
cd /home/pi/Documents/github/test-class/0920
uv run uvicorn practice1:app --host 0.0.0.0 --port 8000 --reload
```

`--reload` 參數會在程式碼變更時自動重新載入,方便開發。

---

## 🧪 測試步驟

1. **啟動伺服器**
   ```bash
   uv run python practice1.py
   ```

2. **檢查首頁**
   - 瀏覽器開啟 `http://localhost:8000`
   - 應該會看到「LINE Bot + Gemini AI」的歡迎頁面

3. **設定 Webhook**
   - 如果在本地,使用 ngrok: `ngrok http 8000`
   - 複製 ngrok URL 到 LINE Developers Console
   - Webhook URL: `https://你的ngrok網址/webhook`

4. **測試 Bot**
   - 用 LINE 手機 App 加入你的 Bot 為好友
   - 發送訊息給 Bot
   - Bot 應該會用 Gemini AI 回覆你!

---

## 📖 參考資源

### 官方文件
- [LINE Messaging API SDK for Python](https://github.com/line/line-bot-sdk-python)
- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Bot SDK v3 文件](https://line.github.io/line-bot-sdk-python/)

### 常用方法
- `reply_message` - 回覆訊息
- `push_message` - 主動推送訊息
- `multicast` - 群發訊息
- `broadcast` - 廣播訊息

---

## 💡 小技巧

### 1. 除錯模式

在程式中加入更多 log:

```python
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    print(f"事件類型: {event.type}")
    print(f"訊息 ID: {event.message.id}")
    print(f"使用者 ID: {event.source.user_id}")
    print(f"訊息內容: {event.message.text}")
    # ...
```

### 2. 錯誤處理

```python
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        # 你的處理邏輯
        pass
    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        # 回覆錯誤訊息給使用者
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉,發生錯誤了")]
                )
            )
```

### 3. 環境檢查

啟動時檢查環境變數:

```python
if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    print("❌ 錯誤: 請在 .env 中設定 LINE Bot 憑證!")
    exit(1)

if not GEMINI_API_KEY:
    print("❌ 錯誤: 請在 .env 中設定 GEMINI_API_KEY!")
    exit(1)
```

---

## ✅ 總結

使用 LINE Bot SDK 後:
- ✅ 程式碼從 ~220 行減少到 ~180 行
- ✅ 更容易理解和維護
- ✅ 自動處理簽章驗證和錯誤
- ✅ 可以輕鬆擴展更多功能

現在你的 LINE Bot 已經使用官方 SDK 了,更專業也更穩定! 🎉
