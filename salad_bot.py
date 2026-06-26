import os
import random
import requests
from datetime import datetime

# =========================================================================
# [수정된 부분] .env 파일 대신, 깃허브 시스템(Environment)에서 직접 토큰을 가져옵니다.
# =========================================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 주변 단골 샐러드 매장 및 메뉴 데이터베이스
SALAD_STORES = {
    "샐러디 마곡나루점": [
        {"menu": "칠리베이컨 웜볼", "price": 8900, "type": "웜볼"},
        {"menu": "우삼겹 웜볼", "price": 8700, "type": "웜볼"},
        {"menu": "시저치킨 샐러디", "price": 6900, "type": "샐러드"}
    ],
    "슬로우가든": [
        {"menu": "프리메이플 베이컨 샐러드", "price": 12500, "type": "샐러드"},
        {"menu": "수비드 닭가슴살 샐러드", "price": 11500, "type": "샐러드"}
    ],
    "잇샐러드": [
        {"menu": "시그니처 로맨틱 시트러스", "price": 12900, "type": "찹샐러드"},
        {"menu": "에너자이저", "price": 13900, "type": "찹샐러드"}
    ]
}

def pick_today_lunch():
    budget_limit = 13000
    candidates = []
    
    for store_name, menu_list in SALAD_STORES.items():
        for item in menu_list:
            candidates.append({
                "store": store_name,
                "menu": item['menu'],
                "price": item['price'],
                "type": item['type']
            })
                
    # 후보군 중 랜덤으로 1개 추출
    return random.choice(candidates)

def send_telegram_notification(lunch_info):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = (
        f"🥗 <b>오늘의 점심 샐러드 추천</b> 🥗\n\n"
        f"🏪 <b>매장명:</b> {lunch_info['store']}\n"
        f"🍽️ <b>메뉴명:</b> {lunch_info['menu']} ({lunch_info['type']})\n"
        f"💵 <b>가 격:</b> {lunch_info['price']:,}원\n\n"
        f"🕒 <i>선정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
        f"🤖 <i>GitHub Actions로 발송된 평일 알림</i>"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[{datetime.now()}] 텔레그램 알림 전송 성공!")
        else:
            print(f"텔레그램 전송 실패! 에러코드: {response.status_code}, 메시지: {response.text}")
    except Exception as e:
        print(f"에러 발생: {e}")

# 프로그램이 켜지면 딱 한 번 실행하고 종료됩니다.
if __name__ == "__main__":
    print("점심 메뉴 추천 프로세스를 구동합니다...")
    lunch_info = pick_today_lunch()
    send_telegram_notification(lunch_info)
