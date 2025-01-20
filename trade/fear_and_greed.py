import requests
from datetime import datetime

def get_fear_greed_data():
    """
    alternative.me API에서 공포&탐욕 지수를 조회하는 함수
    
    Returns:
        dict or None: 공포&탐욕 지수 데이터 또는 오류 시 None
    """
    url = "https://api.alternative.me/fng/?limit=2"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # print("\n 🔥 공포&탐욕 지수")
        
        for item in data['data']:
            date = datetime.fromtimestamp(int(item['timestamp']))
            formatted_date = date.strftime("%Y-%m-%d")
            
            # print(f"날짜: {formatted_date}")
            # print(f"지수: {item['value']}")
            # print(f"상태: {item['value_classification']}")
            
            if 'time_until_update' in item:
                update_in_hours = int(item['time_until_update']) // 3600
                # print(f"다음 업데이트까지: 약 {update_in_hours}시간")
            
            # print("-" * 50)
        
        return data
            
    except Exception as e:
        print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None
