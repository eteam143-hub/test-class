# LINE Bot + Gemini AI 整合教學

這個專案整合了 LINE Bot Webhook 與 Google Gemini AI,讓你的 LINE Bot 能夠使用 AI 智慧回覆訊息。

## 功能特色

- ✅ 接收 LINE 使用者的訊息
- ✅ 使用 Google Gemini API 生成智慧回應
- ✅ 自動回覆 LINE 使用者
- ✅ 支援簽章驗證(安全性)
- ✅ 繁體中文友善對話

## 環境設定

### 1. 安裝依賴套件

專案使用 uv 虛擬環境,已經安裝好所需套件:
- fastapi
- uvicorn
- google-genai
- aiohttp
- python-dotenv

### 2. 設定環境變數

編輯根目錄的 `.env` 檔案,填入以下資訊:

```env
# Gemini API Key (已設定)
GEMINI_API_KEY=你的_GEMINI_API_KEY

# LINE Bot 設定
LINE_CHANNEL_SECRET=你的_LINE_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_CHANNEL_ACCESS_TOKEN
```

### 3. 取得 LINE Bot 憑證

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 或選擇現有的
3. 建立新的 Messaging API Channel
4. 在 Channel 設定頁面找到:
   - **Channel Secret** → 複製到 `LINE_CHANNEL_SECRET`
   - **Channel Access Token** → 複製到 `LINE_CHANNEL_ACCESS_TOKEN`

### 4. 設定 Webhook URL

1. 在 LINE Developers Console 的 Webhook 設定區域
2. 輸入你的 webhook URL: `https://你的網址/webhook`
   - 如果在本地測試,可以使用 ngrok 等工具建立 HTTPS 通道
3. 啟用「Use webhook」
4. 關閉「Auto-reply messages」(自動回覆訊息)

## 執行方式

### 啟動伺服器

```bash
cd /home/pi/Documents/github/test-class/0920
uv run python practice1.py
```

或使用 uvicorn:

```bash
cd /home/pi/Documents/github/test-class/0920
uv run uvicorn practice1:app --host 0.0.0.0 --port 8000
```

伺服器將會在 `http://0.0.0.0:8000` 啟動

### 測試首頁

瀏覽器開啟 `http://localhost:8000`,應該會看到歡迎頁面。

### 測試 Webhook

使用 LINE 手機 App 加入你的 Bot 為好友,然後發送訊息,Bot 就會使用 Gemini AI 回覆你!

## 程式架構說明

### 主要函式

1. **`verify_line_signature()`** - 驗證 LINE webhook 請求的簽章,確保請求來自 LINE 伺服器
2. **`get_gemini_response()`** - 呼叫 Gemini API,生成 AI 回應
3. **`send_line_reply()`** - 使用 LINE Messaging API 回覆訊息給使用者
4. **`line_webhook()`** - Webhook 端點,處理 LINE 的事件

### 運作流程

```
LINE 使用者發送訊息
    ↓
LINE 伺服器推送到你的 Webhook
    ↓
驗證簽章 (安全性檢查)
    ↓
解析訊息內容
    ↓
呼叫 Gemini API 生成回應
    ↓
使用 LINE API 回覆使用者
```

## 本地開發測試

如果要在本地開發並測試 LINE webhook,需要使用 ngrok:

```bash
# 安裝 ngrok (如果還沒安裝)
# 參考: https://ngrok.com/download

# 啟動 ngrok (在另一個終端機視窗)
ngrok http 8000

# 複製 ngrok 提供的 HTTPS URL (例如: https://xxxx.ngrok.io)
# 在 LINE Developers Console 設定 Webhook URL: https://xxxx.ngrok.io/webhook
```

## 客製化設定

### 修改 Gemini 回應風格

編輯 `get_gemini_response()` 函式中的 `system_instruction`:

```python
system_instruction = """
你是一個友善且樂於助人的 LINE Bot 助理。
請用繁體中文回覆使用者的問題。
回答要簡潔明瞭,語氣親切自然。

# 可以在這裡加入更多指示,例如:
- 你擅長回答關於 XXX 的問題
- 回答時請保持專業但不失親切
- 如果不知道答案,請誠實告知
"""
```

### 修改 Gemini 模型

目前使用的是 `gemini-3.1-flash-lite`,你可以改用其他模型:

```python
model="gemini-3.5-flash-lite",  # 更快速的回應
# 或
model="gemini-3.8-flash",  # 更準確的回應
```

## 疑難排解

### 問題: Bot 沒有回應

1. 檢查 LINE Developers Console 的 Webhook 設定是否正確
2. 確認 `.env` 中的憑證是否正確
3. 查看終端機的 log 訊息
4. 確認伺服器正在運行且可從外部訪問

### 問題: Gemini API 錯誤

1. 確認 `GEMINI_API_KEY` 是否正確
2. 檢查 API 配額是否用完
3. 確認網路連線正常

### 問題: 簽章驗證失敗

1. 確認 `LINE_CHANNEL_SECRET` 是否正確
2. 檢查是否有多餘的空白或換行字元

## 參考資源

- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [Google Gemini API 文件](https://ai.google.dev/docs)
- [FastAPI 文件](https://fastapi.tiangolo.com/)

## 授權

本專案僅供教學使用。
