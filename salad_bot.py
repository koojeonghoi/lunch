import os
import sys
import random
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 깃허브 액션이 실행될 때 우리가 입력한 대화 내용(가게 이름)을 읽어옵니다.
try:
    USER_INPUT = os.environ.get("USER_MESSAGE", "").strip()
except:
    USER_INPUT = ""

# 마곡나루 매장별 실제 선호하시는 최애 메뉴판 데이터 (튕기지 않는 배민 표준 ID 반영)
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
            {"name": "클래식 연어 포케", "price": 12500, "tip": "🐟 현미밥 베이스라 물리지 않고 오후 내내 든든해요."},
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

def respond_to_user():
    if not USER_INPUT:
        print("입력된 메시지가 없습니다.")
        return

    # 사용자가 입력한 글자에 매장 이름이 들어있는지 감지
    matched_store = None
    for store_name in MY_FAVORITE_POOLS.keys():
        if store_name in USER_INPUT:
            matched_store = store_name
            break

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    if matched_store:
        store_info = MY_FAVORITE_POOLS[matched_store]
        selected_menu = random.choice(store_info["menus"])
        
        message = (
            f"🎯 <b>마곡나루 [{matched_store}] 취향 저격 추천</b> 🥗\n\n"
            f"🍽️ <b>추천 메뉴:</b> {selected_menu['name']}\n"
            f"💵 <b>가 격:</b> {selected_menu['price']:,}원\n\n"
            f"💡 <b>오늘의 포만감 가이드:</b>\n{selected_menu['tip']}\n\n"
            f"🔗 <a href='{store_info['shop_url']}'>👉 [여기]를 눌러 배민으로 바로 주문</a>"
        )
    else:
        message = (
            f"❓ <b>알림 실패</b>\n\n"
            f"'{USER_INPUT}' 은(는) 등록되지 않은 가게입니다.\n"
            f"👉 <code>샐러디</code>, <code>슬로우캘리</code>, <code>프레퍼스</code> 중 알고 싶은 마곡나루 매장명을 포함해서 다시 입력해주세요!"
        )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    requests.post(url, json=payload)

if __name__ == "__main__":
    respond_to_user()
