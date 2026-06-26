import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 깃허브 시크릿에서 토큰 가져오기
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# =========================================================================
# [실시간 연동 매장 리스트] 
# 각 매장의 실시간 정보를 긁어올 수 있는 웹 경로(crawl_url)와 실제 배민 연결 링크(order_url)
# =========================================================================
SALAD_STORES = {
    "샐러디 마곡나루역점": {
        "crawl_url": "https://m.place.naver.com/restaurant/1922572528/menu/list", 
        "order_url": "https://baemin.me/마곡나루샐러디_실제링크"
    },
    "슬로우캘리 마곡나루점": {
        "crawl_url": "https://m.place.naver.com/restaurant/1057474431/menu/list",
        "order_url": "https://baemin.me/마곡나루슬로우캘리_실제링크"
    },
    "프레퍼스 다이어트 푸드 마곡나루점": {
        "crawl_url": "https://m.place.naver.com/restaurant/1041113697/menu/list",
        "order_url": "https://baemin.me/마곡나루프레퍼스_실제링크"
    },
    "포케올데이 마곡나루점": {
        "crawl_url": "https://m.place.naver.com/restaurant/1614914101/menu/list",
        "order_url": "https://baemin.me/마곡나루포케올데이_실제링크"
    }
}

def get_realtime_menu(store_name, crawl_url):
    """ 매장 웹페이지에 접속하여 실시간으로 메뉴명과 가격을 긁어오는 함수 """
    menu_items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    
    try:
        response = requests.get(crawl_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 모바일 플레이스 메뉴판 태그 파싱 구조 (현재 기준)
            # 웹사이트 구조에 따라 매칭되는 요소를 유연하게 찾습니다.
            menus = soup.find_all(class_="E2gYt") or soup.select(".menu_title")
            prices = soup.find_all(class_="dBw7q") or soup.select(".menu_price")
            
            for menu, price in zip(menus, prices):
                menu_name = menu.text.strip()
                # 가격 텍스트(예: "11,500원")에서 숫자만 추출
                try:
                    menu_price = int(''.join(filter(str.isdigit, price.text)))
                except:
                    continue
                
                # 💡 [배고픔 방지] 실시간 메뉴명을 분석하여 자동으로 포만감 가중치(weight) 부여
                weight = 1  # 기본 가중치 (채소 위주 가벼운 메뉴)
                desc = "🥗 가볍고 깔끔하게 드실 수 있는 메뉴입니다."
                
                # 든든한 키워드가 들어가면 확률을 4~5배 상향 조정
                heavy_words = ["웜볼", "포케", "밥", "비프", "스테이크", "파스타", "오리", "포크", "삼겹"]
                if any(word in menu_name for word in heavy_words):
                    weight = 5
                    desc = "🥩 탄수화물(곡물/면)이나 고기 토핑이 풍부해 퇴근 전까지 아주 든든합니다!"
                
                menu_items.append({
                    "menu": menu_name,
                    "price": menu_price,
                    "weight": weight,
                    "desc": desc
                })
    except Exception as e:
        print(f"[{store_name}] 실시간 데이터 가져오기 실패: {e}")
        
    return menu_items

def pick_today_lunch():
    budget_limit = 15000  # 식비 예산 상한선
    candidates = []
    weights = []
    
    print("마곡나루역 주변 매장의 실시간 최신 메뉴판을 긁어오는 중입니다...")
    for store_name, store_info in SALAD_STORES.items():
        realtime_items = get_realtime_menu(store_name, store_info["crawl_url"])
        
        # 만약 실시간 크롤링이 실패했을 경우를 대비한 최소한의 기본 메뉴 백업 로직
        if not realtime_items:
            print(f"⚠️ {store_name} 크롤링 실패로 기본 고정 메뉴를 대체 적용합니다.")
            realtime_items = [
                {"menu": "대표 추천 웜볼/포케 상품", "price": 11500, "weight": 4, "desc": "매장 추천 든든한 시그니처 메뉴입니다."}
            ]
            
        for item in realtime_items:
            if item['price'] <= budget_limit:
                candidates.append({
                    "store": store_name,
                    "menu": item['menu'],
                    "price": item['price'],
                    "desc": item['desc'],
                    "url": store_info["order_url"],
                    "weight": item['weight']
                })
                weights.append(item['weight'])
                
    if not candidates:
        return None

    # 실시간 분석된 포만감 가중치(weight)를 반영하여 높은 확률로 든든한 메뉴 선정
    return random.choices(candidates, weights=weights, k=1)[0]

def send_telegram_notification(lunch_info):
    if not lunch_info:
        print("추천할 수 있는 메뉴가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = (
        f"📍 <b>[마곡나루역] 실시간 점심 샐러드 추천</b> 🥗\n\n"
        f"🏪 <b>매장명:</b> {lunch_info['store']}\n"
        f"🍽️ <b>메뉴명:</b> {lunch_info['menu']}\n"
        f"💵 <b>가 격:</b> {lunch_info['price']:,}원 (실시간 반영 가격)\n\n"
        f"💡 <b>자동 분석 포만감 팁:</b>\n{lunch_info['desc']}\n\n"
        f"🔗 <a href='{lunch_info['url']}'>👉 [여기]를 눌러 배민으로 바로 주문</a>\n\n"
        f"🕒 <i>업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
        f"🤖 <i>매일 최신 메뉴판을 긁어와 분석하는 스마트 봇</i>"
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
    lunch_info = pick_today_lunch()
    send_telegram_notification(lunch_info)
