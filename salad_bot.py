import os
import random
import requests
from datetime import datetime

# 깃허브 시크릿에서 토큰 가져오기
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# =========================================================================
# [데이터베이스 업데이트] 
# 각 매장의 배민/쿠팡이츠 주문 링크(order_url)와 메뉴별 '든든함 정도(weight)' 추가
# weight가 3인 메뉴는 1인 메뉴보다 추천될 확률이 3배 높습니다. (포만감 가중치)
# =========================================================================
SALAD_STORES = {
    "샐러디 마곡나루점": {
        "order_url": "https://baemin.me/example1", # 👈 여기에 실제 배민 매장 주소 넣기
        "items": [
            {"menu": "칠리베이컨 웜볼", "price": 8900, "type": "웜볼(곡물밥 포함)", "desc": "🥓 베이컨+곡물밥 조합으로 오후 내내 든든합니다!", "weight": 3},
            {"menu": "우삼겹 웜볼", "price": 8700, "type": "웜볼(곡물밥 포함)", "desc": "🥩 우삼겹과 견과류, 곡물밥이 들어가 포만감이 오래 가요.", "weight": 3},
            {"menu": "시저치킨 샐러디", "price": 6900, "type": "가벼운 샐러드", "desc": "🐔 닭가슴살 중심의 기본 샐러드. 깔끔하고 가볍습니다.", "weight": 1}
        ]
    },
    "슬로우가든": {
        "order_url": "https://baemin.me/example2",
        "items": [
            {"menu": "프리메이플 베이컨 샐러드", "price": 12500, "type": "든든한 샐러드", "desc": "🍳 두툼한 베이컨과 계란이 들어가 배가 쉽게 꺼지지 않아요.", "weight": 3},
            {"menu": "수비드 닭가슴살 샐러드", "price": 11500, "type": "가벼운 샐러드", "desc": "🥑 부드러운 닭가슴살 위주의 정석 다이어트 식단!", "weight": 1}
        ]
    },
    "잇샐러드": {
        "order_url": "https://baemin.me/example3",
        "items": [
            {"menu": "스트레스 릴리즈", "price": 13400, "type": "찹샐러드(헤비)", "desc": "🧀 돼지고기, 나초, 치즈가 들어가 샐러드계의 국밥 수준 포만감!", "weight": 4},
            {"menu": "에너자이저", "price": 13900, "type": "찹샐러드(미디움)", "desc": "🐓 닭가슴살과 블랙올리브 등으로 적당한 포만감을 줍니다.", "weight": 2},
            {"menu": "시그니처 로맨틱 시트러스", "price": 12900, "type": "가벼운 샐러드", "desc": "🍊 과일 중심의 상큼한 구성. 조금 배고플 수 있어요.", "weight": 1}
        ]
    }
}

def pick_today_lunch():
    budget_limit = 14000  # 물가 감안 예산 상한선 살짝 상향
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
                # 가중치를 리스트에 추가 (weight가 높을수록 당첨 확률 상승)
                weights.append(item['weight'])
                
    if not candidates:
        return None

    # 가중치(포만감 점수)를 반영하여 랜덤 추출
    selected = random.choices(candidates, weights=weights, k=1)[0]
    return selected

def send_telegram_notification(lunch_info):
    if not lunch_info:
        print("추천할 수 있는 메뉴가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # 메시지에 설명(desc)과 주문 링크(url)를 이쁘게 포함시켰습니다.
    message = (
        f"🥗 <b>오늘의 점심 샐러드 추천</b> 🥗\n\n"
        f"🏪 <b>매장명:</b> {lunch_info['store']}\n"
        f"🍽️ <b>메뉴명:</b> {lunch_info['menu']} ({lunch_info['type']})\n"
        f"💵 <b>가 격:</b> {lunch_info['price']:,}원\n\n"
        f"💡 <b>포만감 팁:</b>\n{lunch_info['desc']}\n\n"
        f"🔗 <a href='{lunch_info['url']}'>👉 [여기]를 눌러 배민으로 주문하기</a>\n\n"
        f"🕒 <i>선정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
        f"🤖 <i>오후에 배고프지 않게 설계된 샐러드 봇</i>"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True # 배민 링크 미리보기창이 길게 뜨는 것을 방지
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
    print("스마트 점심 메뉴 추천 프로세스를 구동합니다...")
    lunch_info = pick_today_lunch()
    send_telegram_notification(lunch_info)
