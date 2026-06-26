import os
import random
import requests
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv  # .env 파일을 읽어오기 위한 라이브러리

# 1. 같은 폴더에 있는 .env 파일의 내용을 프로그램에 가져옵니다.
load_dotenv()

# 2. .env 파일에 적어둔 토큰과 ID를 환경 변수에서 꺼내옵니다.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 3. 주변 단골 샐러드 매장 및 메뉴 데이터베이스
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

RECENT_MENU_HISTORY = [] 
MAX_HISTORY_SIZE = 2

def pick_today_lunch():
    global RECENT_MENU_HISTORY
    budget_limit = 13000
    candidates = []
    
    for store_name, menu_list in SALAD_STORES.items():
        for item in menu_list:
            unique_name = f"{store_name} - {item['menu']}"
            if item['price'] <= budget_limit and unique_name not in RECENT_MENU_HISTORY:
                candidates.append({
                    "store": store_name,
                    "menu": item['menu'],
                    "price": item['price'],
                    "type": item['type'],
                    "unique_name": unique_name
                })
                
    if not candidates:
        RECENT_MENU_HISTORY.clear()
        return pick_today_lunch()

    selected = random.choice(candidates)
    RECENT_MENU_HISTORY.append(selected['unique_name'])
    if len(RECENT_MENU_HISTORY) > MAX_HISTORY_SIZE:
        RECENT_MENU_HISTORY.pop(0)
        
    return selected

def send_telegram_notification(lunch_info):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = (
        f"🥗 <b>오늘의 점심 샐러드 추천</b> 🥗\n\n"
        f"🏪 <b>매장명:</b> {lunch_info['store']}\n"
        f"🍽️ <b>메뉴명:</b> {lunch_info['menu']} ({lunch_info['type']})\n"
        f"💵 <b>가 격:</b> {lunch_info['price']:,}원\n\n"
        f"🕒 <i>선정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
        f"🤖 <i>평일 매일 배달되는 샐러드 알림</i>"
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
            print(f"텔레그램 전송 실패! .env 파일의 토큰과 ID를 확인해주세요. 에러코드: {response.status_code}")
    except Exception as e:
        print(f"에러 발생: {e}")

def job():
    print("평일 점심 메뉴 추천 프로세스를 구동합니다...")
    lunch_info = pick_today_lunch()
    send_telegram_notification(lunch_info)

# 4. 평일(월~금) 오전 11시 00분에 실행되도록 설정
schedule.every().monday.at("11:00").do(job)
schedule.every().tuesday.at("11:00").do(job)
schedule.every().wednesday.at("11:00").do(job)
schedule.every().thursday.at("11:00").do(job)
schedule.every().friday.at("11:00").do(job)

# -------------------------------------------------------------------------
# [테스트 구역] 11시까지 기다리지 않고 바로 메시지가 오는지 확인하는 코드입니다.
# 텔레그램방으로 불쑥 메시지가 잘 오는지 보려면 아래 job() 앞의 '#'을 지우고 저장 후 실행해보세요!
# -------------------------------------------------------------------------
# job()

print("평일 11시 샐러드 추천 스케줄러가 대기 중입니다... (창을 닫지 마세요)")
while True:
    schedule.run_pending()
    time.sleep(1)

