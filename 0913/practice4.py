# 國堂_LV名牌包_打到骨折_channel
# 整合 Gemini 聯網搜尋 + Telegram 圖文推播

import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 設定推播目標
TARGET_USER_ID  = 8753608366
TARGET_GROUP_ID = "-5522499426"
TARGET_CHANNEL_ID = "-1004343185574"

# 圖片路徑（與此程式同一資料夾）
PHOTO_PATH = os.path.join(os.path.dirname(__file__), "lv_bag.jpg")


def fetch_luxury_news() -> str:
    """使用 Gemini 聯網搜尋最新國際精品新聞"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = "請查詢並告訴我今天最新的重要國際精品新聞三則（包含發生時間與簡要說明），使用繁體中文。"

    print(f"💬 提問：{prompt}\n")
    print("🌐 Gemini 正在自主聯網搜尋最新資料中...")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    print("\n🤖 Gemini 聯網搜尋回答：")
    print(response.text)
    return response.text


async def send_photo_broadcast(
    chat_id: str | int,
    photo_source: str,
    caption: str,
    keyboard: InlineKeyboardMarkup | None = None
):
    """
    發送帶有排版說明的圖片推播
    :param photo_source: 本地圖片路徑 或 圖片 URL
    :param caption: 說明文字 (上限 1024 字元)
    :param keyboard: 訊息底部的按鈕 (選填)
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        if os.path.exists(photo_source):
            with open(photo_source, "rb") as photo_file:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
        else:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_source,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        print(f"✅ 成功發送圖文至：{chat_id}")
    except Exception as e:
        print(f"❌ 發送至 {chat_id} 失敗：{e}")


async def main():
    # Step 1：Gemini 搜尋最新精品新聞
    news_text = fetch_luxury_news()

    # Step 2：組合 Telegram 推播內文（限 1024 字元，截斷保險）
    caption_text = (
        "🔥 <b>【限時下殺】LV Neverfull 經典老花托特包 打到骨折！</b>\n\n"
        "專櫃熱銷爆款，限量釋出只有 3 顆！\n\n"
        "▫️ <b>成色狀況：</b> 95 新極美品\n"
        "▫️ <b>專櫃售價：</b> <s>NT$ 86,000</s>\n"
        "▫️ <b>骨折特價：</b> <b>NT$ 29,800</b> 💥\n\n"
        "<i>配件完整附防塵袋、保證卡，提供正品檢驗保證。</i>\n\n"
        "📰 <b>最新精品動態：</b>\n"
        f"{news_text[:400]}...\n\n"   # Gemini 新聞節錄（避免超過 1024 字元）
        "#精品特賣 #LV #Neverfull #限時優惠"
    )

    # Step 3：底部互動按鈕
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛍️ 立即下單", url="https://t.me/Guotang_LV"),
            InlineKeyboardButton("💬 聯絡店長", url="https://t.me/Guotang_LV")
        ]
    ])

    # Step 4：推播給所有目標
    targets = [
        TARGET_USER_ID,
        TARGET_GROUP_ID,
        TARGET_CHANNEL_ID
    ]

    for chat_id in targets:
        await send_photo_broadcast(chat_id, PHOTO_PATH, caption_text, keyboard)


if __name__ == "__main__":
    asyncio.run(main())
