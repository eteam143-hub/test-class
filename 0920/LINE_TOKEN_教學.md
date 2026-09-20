# 🔑 如何取得 LINE Channel Access Token 完整教學

## 前置需求
- LINE 帳號
- 電腦瀏覽器

---

## 📋 步驟總覽

1. 建立 LINE Official Account (LINE 官方帳號)
2. 啟用 Messaging API
3. 取得 Channel Access Token 和 Channel Secret

---

## 🚀 詳細步驟

### 步驟 1: 建立 LINE Official Account

#### 1-1. 前往 LINE Official Account Manager

開啟瀏覽器,前往:
```
https://manager.line.biz/
```

使用你的 LINE 帳號登入。

#### 1-2. 建立新的官方帳號

1. 點擊右上角的 **「建立」** 或 **「Create」** 按鈕
2. 填寫必要資訊:
   - **帳號名稱**: 輸入你的 Bot 名稱(例如: 我的智慧助理)
   - **類別**: 選擇適合的分類
   - **子類別**: 選擇子分類
   - **電子郵件**: 填入你的信箱
3. 閱讀並同意服務條款
4. 點擊 **「建立」**

---

### 步驟 2: 啟用 Messaging API

#### 2-1. 進入帳號設定

1. 在 LINE Official Account Manager 中,選擇剛建立的帳號
2. 點擊右上角的 **「設定」**

#### 2-2. 啟用 Messaging API

1. 在左側選單找到並點擊 **「Messaging API」**
2. 向下滾動找到 **「Messaging API」** 區塊
3. 點擊 **「使用 Messaging API」** 按鈕

#### 2-3. 選擇 Provider

如果這是你第一次使用:
1. 系統會要求你建立或選擇一個 **Provider**(提供者)
2. 你可以建立新的 Provider(輸入名稱)或選擇現有的
3. **建議**: 使用專案名稱作為 Provider 名稱

---

### 步驟 3: 取得 Token 和 Secret

#### 3-1. 前往 LINE Developers Console

在 Messaging API 設定頁面中,點擊 **「LINE Developers」** 連結,會開啟新分頁到 LINE Developers Console。

或直接前往:
```
https://developers.line.biz/console/
```

#### 3-2. 選擇你的 Channel

1. 在 LINE Developers Console 首頁
2. 選擇你剛建立的 Provider
3. 點擊你的 Channel (官方帳號)

#### 3-3. 取得 Channel Secret

1. 在 Channel 頁面,點擊上方的 **「Basic settings」** 分頁
2. 向下滾動找到 **「Channel secret」** 區塊
3. 複製 Channel secret 的值

```
這就是你的 LINE_CHANNEL_SECRET ✅
```

#### 3-4. 取得 Channel Access Token

1. 點擊上方的 **「Messaging API」** 分頁
2. 向下滾動找到 **「Channel access token」** 區塊
3. 如果還沒有 token,點擊 **「Issue」**(發行)按鈕
4. 會出現一個長期有效的 token (Channel access token (long-lived))
5. 複製這個 token

```
這就是你的 LINE_CHANNEL_ACCESS_TOKEN ✅
```

---

## 📝 填入 .env 檔案

將取得的兩個值填入專案根目錄的 `.env` 檔案:

```env
# LINE Bot 設定
LINE_CHANNEL_SECRET=你剛複製的_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你剛複製的_Channel_Access_Token
```

**範例:**
```env
LINE_CHANNEL_SECRET=abc123def456ghi789jkl012mno345pq
LINE_CHANNEL_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
```

---

## ⚙️ 其他重要設定

### 關閉自動回覆訊息

在 LINE Official Account Manager 中:

1. 進入 **「設定」** → **「回應設定」**
2. 找到 **「自動回應訊息」**
3. 將它設為 **「關閉」**
4. 將 **「Webhook」** 設為 **「開啟」**

這樣 Bot 才能正確接收並回覆訊息!

### 設定 Webhook URL

在 LINE Developers Console 的 Messaging API 分頁:

1. 找到 **「Webhook settings」** 區塊
2. 點擊 **「Edit」**
3. 輸入你的 Webhook URL:
   ```
   https://你的網址/webhook
   ```
4. 點擊 **「Update」**
5. 開啟 **「Use webhook」** 開關
6. 點擊 **「Verify」** 測試連線(需要伺服器已啟動)

### 本地開發使用 ngrok

如果在本地測試,需要使用 ngrok 建立 HTTPS 通道:

```bash
# 安裝 ngrok (參考 https://ngrok.com/download)

# 啟動 FastAPI 伺服器
cd /home/pi/Documents/github/test-class/0920
uv run python practice1.py

# 在另一個終端機視窗啟動 ngrok
ngrok http 8000

# 複製 ngrok 提供的 HTTPS URL (例如: https://abc123.ngrok.io)
# 在 LINE Developers Console 設定 Webhook URL: https://abc123.ngrok.io/webhook
```

---

## ✅ 完成檢查清單

- [ ] 已建立 LINE Official Account
- [ ] 已啟用 Messaging API
- [ ] 已取得 Channel Secret
- [ ] 已取得 Channel Access Token
- [ ] 已填入 .env 檔案
- [ ] 已關閉自動回應訊息
- [ ] 已開啟 Webhook
- [ ] 已設定 Webhook URL
- [ ] 已測試 Bot 回應

---

## 🔗 快速連結

- [LINE Developers Console](https://developers.line.biz/console/)
- [LINE Official Account Manager](https://manager.line.biz/)
- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [ngrok 官網](https://ngrok.com/)

---

## ❓ 常見問題

### Q: Channel Access Token 會過期嗎?

A: 「Channel access token (long-lived)」是長期有效的 token,不會過期。但建議定期更換以確保安全。

### Q: 可以在多個地方使用同一個 token 嗎?

A: 可以,但要注意同一時間只能有一個 Webhook URL。如果設定多個,只有最後設定的會生效。

### Q: 如何測試 Webhook 是否正常?

A: 在 LINE Developers Console 的 Messaging API 分頁,找到 Webhook URL 設定,點擊「Verify」按鈕即可測試。

### Q: Bot 沒有回應怎麼辦?

A: 檢查:
1. Webhook URL 是否正確設定
2. 伺服器是否正在運行
3. 自動回應訊息是否已關閉
4. Use webhook 開關是否已開啟
5. .env 中的憑證是否正確

---

## 📞 需要協助?

如果遇到問題,可以:
1. 檢查終端機的 log 訊息
2. 查看 LINE Developers Console 的錯誤訊息
3. 參考 [LINE API 官方文件](https://developers.line.biz/en/docs/)

祝你開發順利! 🎉
