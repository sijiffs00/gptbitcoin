import os
from dotenv import load_dotenv
import pyupbit
import requests
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands

# 0. env 파일 로드
load_dotenv()

def ai_trading():


  # 1. 현재 투자상태 조회
  access = os.environ['UPBIT_ACCESS_KEY']
  secret = os.environ['UPBIT_SECRET_KEY']
  upbit = pyupbit.Upbit(access, secret)
  print(f"\n💰:") 
  print(f"보유 현금: {upbit.get_balance('KRW')} KRW")  # 원화 잔고 조회
  print(f"보유 비트코인: {upbit.get_balance('KRW-BTC')} BTC")  # 비트코인 잔고 조회


  # 2. 오더북(호가 데이터) 조회
  orderbook = pyupbit.get_orderbook("KRW-BTC")
  print(f"\n📒 오더북 (호가데이터):")
  
  # BTC-KRW 마켓에 대한 주요 정보만 출력
  print(f"매도 총량: {orderbook['total_ask_size']:.8f} BTC") # 매도주문의 총 비트코인 수량
  print(f"매수 총량: {orderbook['total_bid_size']:.8f} BTC") # 매수 주문의 총 비트코인 수량
  
  print("\n호가 정보:")
  for unit in orderbook['orderbook_units'][:5]:  # 상위 5개 호가만 출력. 15개가 최대임.
      print(f"매도: {unit['ask_price']:,} KRW ({unit['ask_size']:.8f} BTC)") # 매도 호가와 수량
      print(f"매수: {unit['bid_price']:,} KRW ({unit['bid_size']:.8f} BTC)") # 매수 호가와 수량
      print("-" * 50)


  # 3. 차트 데이터 조회
  # 30일 일봉 데이터
  df_daily = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
  print(f"\n 💗 30일 일봉데이터:") 
  print(df_daily.to_json())
  
  # 24시간 시간봉 데이터
  df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
  print(f"\n 💖 24시간 시간봉데이터:") 
  print(df_hourly.to_json())

  # 4. Ta 라이브러리를 활용한 기술적 분석
  
  # 4-1) 일봉 데이터에 대한 기술적 지표 계산
  print("\n📊 일봉 기술적 지표:")
  # RSI (상대강도지수)
  df_daily['rsi'] = RSIIndicator(df_daily['close']).rsi()
  # MACD
  macd = MACD(df_daily['close'])
  df_daily['macd'] = macd.macd()
  df_daily['macd_signal'] = macd.macd_signal()
  # 볼린저 밴드
  bollinger = BollingerBands(df_daily['close'])
  df_daily['bb_high'] = bollinger.bollinger_hband()
  df_daily['bb_low'] = bollinger.bollinger_lband()
  # 이동평균선
  df_daily['sma_20'] = SMAIndicator(df_daily['close'], window=20).sma_indicator()
  
  print(df_daily[['close', 'rsi', 'macd', 'macd_signal', 'bb_high', 'bb_low', 'sma_20']].tail().to_string())
  
  # 4-2) 시간봉 데이터에 대한 기술적 지표 계산
  print("\n⏰ 시간봉 기술적 지표:")
  # RSI
  df_hourly['rsi'] = RSIIndicator(df_hourly['close']).rsi()
  # MACD
  macd = MACD(df_hourly['close'])
  df_hourly['macd'] = macd.macd()
  df_hourly['macd_signal'] = macd.macd_signal()
  # 볼린저 밴드
  bollinger = BollingerBands(df_hourly['close'])
  df_hourly['bb_high'] = bollinger.bollinger_hband()
  df_hourly['bb_low'] = bollinger.bollinger_lband()
  # 이동평균선
  df_hourly['sma_20'] = SMAIndicator(df_hourly['close'], window=20).sma_indicator()
  
  print(df_hourly[['close', 'rsi', 'macd', 'macd_signal', 'bb_high', 'bb_low', 'sma_20']].tail().to_string())

  # 5. 공포&탐욕지수 API요청 후 조회
  def get_fear_greed_data():
      url = "https://api.alternative.me/fng/?limit=2"
      
      try:
          response = requests.get(url)
          data = response.json()
          
          print("\n 🔥 공포&탐욕 지수")
          print("-" * 50)
          
          for item in data['data']:
              date = datetime.fromtimestamp(int(item['timestamp']))
              formatted_date = date.strftime("%Y-%m-%d")
              
              print(f"날짜: {formatted_date}")
              print(f"지수: {item['value']}")
              print(f"상태: {item['value_classification']}")
              
              if 'time_until_update' in item:
                  update_in_hours = int(item['time_until_update']) // 3600
                  print(f"다음 업데이트까지: 약 {update_in_hours}시간")
              
              print("-" * 50)
              
      except Exception as e:
          print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
          return None

  # 함수 호출
  get_fear_greed_data()



#   # 6. AI에게 데이터 제공하고 판단 받기
#   from openai import OpenAI
#   client = OpenAI()
#   response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#       {
#         "role": "system",
#         "content": [
#           {
#             "type": "text",
#             "text": "You are an expert in Bitcoin investing.\nTell me whether to buy, sell, or hold at the moment based on the chart data provided.\nresponse in json format.\n\nResponse Example :\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"},\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"},\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"},"
#           }
#         ]
#       },
#       {
#         "role": "user",
#         "content": [
#           {
#             "type": "text",
#             "text": df_daily.to_json()
#           }
#         ]
#       },
#       {
#         "role": "assistant",
#         "content": [
#           {
#             "type": "text",
#             "text": "{\"decision\": \"hold\", \"reason\": \"Bitcoin prices have shown some volatility but appear to be stabilizing. After a peak, there was a slight decline, and the volume of trading is decreasing. This might indicate consolidation before another move. With no major sell-off or breakout signals, holding is advisable.\"}"
#           }
#         ]
#       }
#     ],
#     response_format={
#       "type": "json_object"
#     },
#   )
#   # API 응답 확인을 위한 출력 추가
#   result = response.choices[0].message.content


#   # 4. AI의 판단에 따라 실제로 자동매매 진행하기
#   import json
#   result = json.loads(result)
#   print(f"\n🤖:") 
#   print(f"응답 내용 확인:\n     decision: {result["decision"]}")
#   print(f"     reason: {result["reason"]}") 
#   if result["decision"] == "buy":
#       print("🖖🏻사라")
#       # my_krw = upbit.get_balance("KRW")

#       # # 살때는 수수료제외하고 5000원이상이여야 살 수 있음.
#       # if my_krw*0.9995 > 5000:
#       #     print(upbit.buy_market_order("KRW-BTC", my_krw*0.9995))

#   elif result["decision"] == "sell":
#       print("👆🏼팔아라")

#       # my_btc = upbit.get_balance("KRW-BTC")
#       # current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
      
#       # # 코인을 팔때는 체결금액에서 수수료제외하고 한화로 입금되니까 수수료 계산할필요X
#       # if my_btc*current_price > 5000:
#       #   print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
      
#   elif result["decision"] == "hold":   
#       print("🖐🏻홀드홀드")


# # while True :
# #    import time
# #    time.sleep(30)

ai_trading()


