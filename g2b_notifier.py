import requests
import json
from datetime import datetime, timedelta

# 1. 경환 님이 제공해주신 실제 정보 적용
# 주의: 브라우저에서 'Unexpected errors'가 났다면 Decoding 키 대신 Encoding 키를 넣어보세요.
SERVICE_KEY = "c931063a6a78de90174a145888564cfba283d12ade1701a9edf1abd2225abe7a"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# 아이코어 인턴 업무용 키워드
KEYWORDS = ["인공지능", "AI", "데이터", "클라우드", "소프트웨어"]

def get_g2b_data():
    # 경환 님의 API 명세에 적힌 정확한 엔드포인트 (2번: 용역조회)
    base_url = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServc"
    
    # 날짜 설정
    now = datetime.now()
    yesterday = now - timedelta(days=7) # 테스트를 위해 7일치로 범위를 넓혀볼게요
    
    params = {
        'serviceKey': SERVICE_KEY,
        'numOfRows': '50',
        'pageNo': '1',
        'inqryDiv': '1', # 1: 등록일시 기준
        'inqryBgnDt': yesterday.strftime('%Y%m%d%H%M'),
        'inqryEndDt': now.strftime('%Y%m%d%H%M'),
        'type': 'json'
    }

    try:
        # 인증키가 특수문자를 포함하고 있어 500 에러가 날 경우를 대비한 처리
        # 만약 계속 500이 나면 아래 params에서 serviceKey를 빼고 URL에 직접 더하는 방식을 써야 합니다.
        response = requests.get(base_url, params=params, timeout=15)
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', {}).get('body', {}).get('items', [])
        else:
            print(f"서버 응답 오류: {response.text}")
            return []
            
    except Exception as e:
        print(f"오류 발생: {e}")
        return []

def send_to_slack(title, org, link):
    payload = {
        "text": f"📢 *[아이코어] 신규 입찰 공고 발견*",
        "attachments": [{
            "color": "#36a64f",
            "fields": [
                {"title": "공고명", "value": title, "short": False},
                {"title": "공고기관", "value": org, "short": True}
            ],
            "actions": [{
                "type": "button",
                "text": "공고 확인하기",
                "url": link
            }]
        }]
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("🔍 조달청 용역 공고 수집 시작...")
    items = get_g2b_data()
    
    match_count = 0
    if items:
        for item in items:
            title = item.get('bidNtceNm', '')
            if any(key in title for key in KEYWORDS):
                org = item.get('ntceInsttNm', '알 수 없음')
                link = item.get('bidNtceDtlUrl', '#')
                send_to_slack(title, org, link)
                print(f"✅ 매칭: {title}")
                match_count += 1
    
    print(f"🏁 완료! {match_count}건 전송됨.")