import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 이제 고정된 메뉴 대신, 매장의 크롤링 타겟 URL과 배민 주문 링크만 관리합니다.
SALAD_STORES = {
    "샐러디 마곡나루역점": {
        "crawl_url": "https://m.place.naver.com/restaurant/12345678/menu/list", # 예시: 네이버 지도 메뉴판 주소
        "order_url": "https://baemin.me/실제배민링크1"
    },
    "슬로우캘리 마곡나루점": {
        "crawl_url": "https://m.place.naver.com/restaurant/87654321/menu/list",
        "order_url": "https://baemin.me/실제배민링크2"
    },
    "프레퍼스 마곡나루점": {
        "crawl_url": "https://m.place.naver.com/restaurant/56781234/menu/list",
        "order_url": "https://baemin.me/실제배민링크3"
    }
}

# 실시간으로 매장 웹사이트에 접속해 메뉴판을 긁어오는 함수
def get_realtime_menu(store_name, crawl_url):
    menu_items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    
    try:
        response = requests.get(crawl_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 지도 소스에 맞춰 메뉴판 태그를 파싱 (실제 사이트 구조에 맞춰 클래스명 설정 필요)
            menus = soup.select(".E2gYt") # 예시 메뉴 이름 클래스
            prices = soup.select(".dBw7q") # 예시 가격 클래스
            
            for menu, price in zip(menus, prices):
                menu_name = menu.text.strip()
                # 가격 텍스트(예: "11,500원")를 숫자로 변환
                menu_price = int(price.text.replace(",", "").replace("원", "").strip())
                
                # 포만감 단어 필터링을 통해 자동으로 가중치(weight) 부여
                weight = 2 # 기본 가중치
                if any(word in menu_name for word in ["웜볼", "포케", "밥", "비프", "스테이크", "파스타"]):
                    weight = 4 # 든든한 메뉴는 확률 업!
                
                menu_items.append({
                    "menu": menu_name,
                    "price": menu_price,
                    "weight": weight
                })
    except Exception as e:
        print(f"{store_name} 크롤링 중 오류 발생: {e}")
        
    return menu_items

def pick_today_lunch():
    candidates = []
    weights = []
    budget_limit = 15000
    
    # 켜지자마자 매번 실시간으로 매장 정보를 다 긁어와 후보군을 합칩니다.
    for store_name, store_info in SALAD_STORES.items():
        realtime_items = get_realtime_menu(store_name, store_info["crawl_url"])
        
        for item in realtime_items:
            if item['price'] <= budget_limit:
                candidates.append({
                    "store": store_name,
                    "menu": item['menu'],
                    "price": item['price'],
                    "url": store_info["order_url"],
                    "weight": item['weight']
                })
                weights.append(item['weight'])
                
    if not candidates:
        return None

    return random.choices(candidates, weights=weights, k=1)[0]

# (이하 send_telegram_notification 및 __main__ 로직은 기존과 동일)
