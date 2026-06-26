import os
import random
import telebot  # 👈 실시간 대화를 위한 라이브러리 추가 필요 (pip install pyTelegramBotAPI)
from datetime import datetime

# 내 토큰 입력
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 마곡나루 매장별 실제 사용자가 선호하는 맞춤형 '최애 메뉴 리스트' 매핑
MY_FAVORITE_POOLS = {
    "샐러디": {
        "shop_url": "https://m.baemin.com/shop/13612543",
        "menus": [
            {"name": "칠리베이컨 웜볼", "price": 8900, "tip": "🥓 아는 맛이 무섭다! 곡물밥 가득이라 퇴근 때까지 배부름 보장."},
            {"name": "우삼겹 웜볼", "price": 8700, "tip": "🥩 단짠 우삼겹 토핑 조합. 단백질과 탄수화물 밸런스 최고."}
        ]
    },
    "슬로우캘리": {
        "shop_url": "https://m.baemin.com/shop/14210985",
        "menus": [
            {"name": "클래식 연어 포케", "price": 12500, "tip": "🐟 현미밥 베이스에 스파이시 마요 소스 추가하면 물리지 않고 든든해요."},
            {"name": "부채살 스테이크 포케", "price": 13500, "tip": "🥩 역시 고기가 들어가야 배가 안 꺼집니다. 굽기 상태 최고."}
        ]
    },
    "프레퍼스": {
        "shop_url": "https://m.baemin.com/shop/12554789",
        "menus": [
            {"name": "비프 와사비 덮밥", "price": 13900, "tip": "🥩 수비드 소고기가 가득 올라간 사실상의 든든한 고기 덮밥 식단!"},
            {"name": "포크 명란 파스타", "price": 9900, "tip": "🍝 부드러운 안심과 샐러드 파스타면의 조합이라 포만감이 매우 오래 갑니다."}
        ]
    }
}

# 텔레그램 메시지가 들어오면 실행되는 로직
@bot.message_handler(func=lambda message: True)
def respond_menu_recommendation(message):
    user_text = message.text.strip()
    
    # 입력한 글자에 매장 이름이 포함되어 있는지 확인
    matched_store = None
    for store_name in MY_FAVORITE_POOLS.keys():
        if store_name in user_text:
            matched_store = store_name
            break
            
    if matched_store:
        store_info = MY_FAVORITE_POOLS[matched_store]
        # 해당 매장의 최애 메뉴 풀에서 하나를 무작위 추천
        selected_menu = random.choice(store_info["menus"])
        
        response_msg = (
            f"🎯 <b>마곡나루 [{matched_store}] 취향 저격 추천</b>\n\n"
            f"🍽️ <b>추천 메뉴:</b> {selected_menu['name']}\n"
            f"💵 <b>가 격:</b> {selected_menu['price']:,}원\n\n"
            f"💡 <b>오늘의 포만감 가이드:</b>\n{selected_menu['tip']}\n\n"
            f"🔗 <a href='{store_info['shop_url']}'>👉 [여기]를 눌러 배민 주문 페이지로 이동</a>"
        )
        bot.reply_to(message, response_msg, parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "❓ '샐러디', '슬로우캘리', '프레퍼스' 중 알고 싶은 마곡나루 매장명을 정확히 입력해주세요!")

if __name__ == "__main__":
    print("🤖 마곡나루 맞춤형 대화 봇이 실시간 구동 중입니다...")
    bot.infinity_polling() # 봇이 꺼지지 않고 메시지를 계속 기다리게 만듦
