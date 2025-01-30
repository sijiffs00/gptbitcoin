# 뉴스기사 수집을 위해 SerpApi 사용해서 Google News 실시간검색내용을 API 요청으로 받을 수 있음.

import os
import requests
from typing import Dict, List

class GoogleNewsAPI:
    def __init__(self):
        
        self.api_key = os.getenv('SERPAPI_API_KEY')
        self.base_url = "https://serpapi.com/search"
    
    def get_btc_news(self) -> List[Dict]:
        """BTC 관련 뉴스 기사를 가져오는 메서드"""
        
        # 검색 파라미터 설정
        params = {
            'api_key': self.api_key,
            'engine': 'google',
            'q': 'BTC OR Bitcoin',  # BTC 또는 Bitcoin 검색
            'tbm': 'nws',           # 뉴스 검색 지정
            'gl': 'us',             # 검색 국가 설정 (미국)
            'hl': 'ko',             # 한국어 결과 선호
        }
        
        try:
            # GET 요청 보내기
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # HTTP 에러 체크
            
            # JSON 응답 파싱
            data = response.json()
            
            # 뉴스 결과 추출 및 가공
            news_results = data.get('news_results', [])
            
            # 필요한 정보만 추출하여 반환
            processed_results = [
                {
                    'title': article['title'],
                    'link': article['link'],
                    'source': article['source'],
                    'date': article['date'],
                    'snippet': article['snippet']
                }
                for article in news_results
            ]
            
            return processed_results
            
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return []

# 사용 예시
if __name__ == "__main__":
    news_api = GoogleNewsAPI()
    news = news_api.get_btc_news()
    
    # 결과 출력
    for article in news:
        print(f"\n제목: {article['title']}")
        print(f"출처: {article['source']}")
        print(f"날짜: {article['date']}")
        print(f"링크: {article['link']}")
        print(f"내용: {article['snippet']}\n")
