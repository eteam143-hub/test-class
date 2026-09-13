{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c85ee251-d3e0-4293-a427-6b9346f1e4c0",
   "metadata": {},
   "outputs": [],
   "source": [
    "#國堂_LV名牌包_打到骨折_channel\n",
    "#-4322810613\n",
    "\n",
    "import asyncio\n",
    "import os\n",
    "from dotenv import load_dotenv\n",
    "from telegram import Bot\n",
    "\n",
    "load_dotenv()\n",
    "TELEGRAM_TOKEN = os.environ.get(\"TELEGRAM_BOT_TOKEN\")\n",
    "\n",
    "# 設定不同推播目標\n",
    "TARGET_USER_ID =8753608366  # 個人 (正整數，用戶需先私訊過 Bot)\n",
    "TARGET_GROUP_ID = \"-5522499426\"         # 群組 (負整數，Bot 需在群組內)\n",
    "TARGET_CHANNEL = \"-1004343185574\"     # 頻道 Chat ID (Bot 需為管理員)\n",
    "\n",
    "async def send_broadcast(chat_id: str | int, message: str):\n",
    "    bot = Bot(token=TELEGRAM_TOKEN)\n",
    "    try:\n",
    "        await bot.send_message(chat_id=chat_id, text=message)\n",
    "        print(f\"✅ 成功發送至：{chat_id}\")\n",
    "    except Exception as e:\n",
    "        print(f\"❌ 發送至 {chat_id} 失敗：{e}\")\n",
    "\n",
    "async def main():\n",
    "    text = \"📢 大家好！這是來自 Telegram Bot 的跨平台主動推播通知。\"\n",
    "\n",
    "    # 可同時推送給多個目標\n",
    "    targets = [\n",
    "        TARGET_USER_ID,\n",
    "        TARGET_GROUP_ID,\n",
    "        TARGET_CHANNEL\n",
    "    ]\n",
    "\n",
    "    for chat_id in targets:\n",
    "        await send_broadcast(chat_id, text)\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    asyncio.run(main())"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
