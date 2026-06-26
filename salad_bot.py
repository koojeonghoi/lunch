import os
import random
import requests
from datetime import datetime

# 깃허브 시크릿에서 토큰 가져오기
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# =========================================================================
# [마곡나루역 초근접 매장 데이터베이스 - 잇샐러드 제외] 
# ⚠️ 각 매장의 "order_url"에는 실제 스마트폰 배민 앱에서 '마곡나루점'을 검색해
# '공유하기'로 복사한 주소를 넣어주시면 한 번에 앱으로 연결됩니다!
# =========================================================================
SALAD_STORES = {
    "샐러디 마곡나루역점": {
        "order_url": "https://s.baemin.com/3N000lEqy5xc3", 
        "items": [
            {"menu": "칠리베이컨 웜볼", "price": 8900, "type": "웜볼(곡물밥)", "desc": "🥓 베이컨+곡물밥 조합으로 마곡나루 직장인 가성비&포만감 최강 메뉴.", "weight": 4},
            {"menu": "우삼겹 웜볼", "price": 8700, "type": "웜볼(곡물밥)", "desc": "🥩 단짠 우삼겹과 견과류, 곡물밥이 들어가 오후 내내 에너지가 유지됩니다.", "weight": 4},
            {"menu": "탄단지 샐러디", "price": 8300, "type": "일반 샐러드", "desc": "🐔 치킨, 감자매쉬가 들어가 균형 잡힌 기본 식단. 무난하게 든든합니다.", "weight": 2}
        ]
    },
    "슬로우캘리 마곡나루점": {
        "order_url": "https://s.baemin.com/Wf000fHwF49jZ==",
        "items": [
            {"menu": "클래식 연어 포케", "price": 12500, "type": "포케(현미밥)", "desc": "🐟 슬로우캘리 원탑 메뉴! 현미밥 베이스라 포만감이 아주 오래 갑니다.", "weight": 3},
            {"menu": "블랙페퍼 치킨 포케", "price": 11500, "type": "포케(현미밥)", "desc": "🍗 달콤 짭조름한 아일랜드풍 닭다리살 and 현미밥. 배가 전혀 안 고픕니다.", "weight": 4},
            {"menu": "부채살 스테이크 포케", "price": 13500, "type": "포케(현미밥)", "desc": "🥩 수비드한 소고기 부채살이 올라가 고기 씹는 맛과 든든함을 보장합니다.", "weight": 4}
        ]
    },
    "프레퍼스 다이어트 푸드 마곡나루점": {
        "order_url": "https://s.baemin.com/Ph000CK6Yfj5D=",
        "items": [
            {"menu": "비프 와사비 덮밥", "price": 13900, "type": "보울(흑미밥+소고기)", "desc": "🥩 부드러운 소고기 수비드와 흑미밥의 조화. 사실상 샐러드 탈을 쓴 고기 덮밥이라 배고플 틈이 없습니다.", "weight": 5},
            {"menu": "포크 명란 파스타", "price": 9900, "type": "샐러드 파스타", "desc": "🍝 돼지 안심 수비드 고기와 샐러드 파스타면! 면 종류라 오후 5시가 되어도 끄떡없습니다.", "weight": 4},
            {"menu": "치킨 데리야끼 덮밥", "price": 8900, "type": "보울(흑미밥+닭)", "desc": "🐔 가성비와 포만감 동시 만족! 부드러운 닭가슴살에 짭짤한 소스가 맛있습니다.", "weight": 4}
        ]
    },
    "포케올데이 마곡나루점": {
        "order_url": "https://s.baemin.com/rZ000ftiT306j",
        "items": [
            {"menu": "현미밥 포케 (오리훈제 토핑)", "price": 11900, "type": "포케(현미밥)", "desc": "🦆 오리훈제 기름과 현미밥의 만남. 은근히 기름지고 배가 쉽게 꺼지지 않습니다.", "weight": 4},
            {"menu": "메밀면 포케 (육회 토핑)", "price": 12900, "type": "포케(메밀면)", "desc": "🍜 야채와 고소한 육회, 메밀면의 조합! 별미이면서 은근히 든든한 양을 자랑합니다.", "weight": 3}
        ]
    }
}

def pick_today_lunch():
    budget_limit = 15000  
    candidates = []
    weights = []
    
    for store_name, store_info in SALAD_STORES.items():
        for item in store_info["items"]:
            if item['price'] <= budget_limit:
                candidates.append({
                    "store": store_name,
                    "menu": item['menu'],
                    "price": item['price'],
                    "type": item['type'],
                    "desc": item['desc'],
                    "url": store_info["order_url"]
                })
                weights.append(item['weight'])
                
    if not candidates:
        return None

    # 포만감 가중치(weight)를 반영하여 높은 확률로 든든한 메뉴 선정
    return random.choices(candidates, weights=weights, k=1)[0]

def send_telegram_notification(lunch_info):
    if not lunch_info:
        print("추천할 수 있는 메뉴가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = (
        f"📍 <b>[마곡나루역] 오늘의 점심 샐러드 추천</b> 🥗\n\n"
        f"🏪 <b>매장명:</b> {lunch_info['store']}\n"
        f"🍽️ <b>메뉴명:</b> {lunch_info['menu']} ({lunch_info['type']})\n"
        f"💵 <b>가 격:</b> {lunch_info['price']:,}원\n\n"
        f"💡 <b>마곡나루 직장인을 위한 포만감 팁:</b>\n{lunch_info['desc']}\n\n"
        f"🔗 <a href='{lunch_info['url']}'>👉 [여기]를 눌러 배민으로 주문하기</a>\n\n"
        f"🕒 <i>선정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
        f"🤖 <i>마곡나루역 전용 스마트 샐러드 배고픔 방지 봇</i>"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[{datetime.now()}] 텔레그램 알림 전송 성공!")
        else:
            print(f"텔레그램 전송 실패! 에러코드: {response.status_code}")
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    print("마곡나루역 점심 메뉴 추천 프로세스를 구동합니다...")
    lunch_info = pick_today_lunch()
    send_telegram_notification(lunch_info)
