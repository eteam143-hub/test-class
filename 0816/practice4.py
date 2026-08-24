# 匯入 Google Gemini AI 套件
from google import genai
# 匯入 dotenv 套件，用來讀取 .env 檔案中的環境變數
from dotenv import load_dotenv
# 匯入 gradio 套件，用來建立網頁介面
import gradio as gr

# 載入 .env 檔案中的環境變數（例如 API 金鑰）
load_dotenv()

# 建立 Gemini AI 客戶端，會自動從環境變數讀取 API 金鑰
client = genai.Client()


# 定義一個函式，接收使用者輸入並回傳 AI 的回覆
def ask_gemini(prompt: str) -> str:
    # 建立一次對話互動，指定模型與輸入問題
    interaction = client.interactions.create(
        model="gemini-3.5-flash",  # 使用 gemini-3.5-flash 模型
        input=prompt               # 輸入的問題
    )
    # 回傳 AI 回覆的文字內容
    return interaction.output_text


# 建立 Gradio 介面
demo = gr.Interface(
    fn=ask_gemini,                        # 要執行的函式
    inputs=gr.Textbox(label="請輸入問題", placeholder="例如：天空為什麼是藍的"),  # 輸入欄位
    outputs=gr.Textbox(label="AI 回覆"),   # 輸出欄位
    title="Gemini AI 聊天介面",            # 介面標題
    description="輸入問題，即可獲得 Gemini AI 的回覆",  # 介面說明
)

# 啟動介面
demo.launch()