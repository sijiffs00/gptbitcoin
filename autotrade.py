import os
from dotenv import load_dotenv
import pyupbit

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
  print(f"매도 총량: {orderbook['total_ask_size']:.8f} BTC")
  print(f"매수 총량: {orderbook['total_bid_size']:.8f} BTC")
  
  print("\n호가 정보:")
  for unit in orderbook['orderbook_units'][:5]:  # 상위 5개 호가만 출력. 15개가 최대임.
      print(f"매도: {unit['ask_price']:,} KRW ({unit['ask_size']:.8f} BTC)") # 매도 호가와 수량
      print(f"매수: {unit['bid_price']:,} KRW ({unit['bid_size']:.8f} BTC)") # 매수 호가와 수량
      print("-" * 50)


  # 3. 차트 데이터 조회
  # 30일 일봉 데이터
  df_daily = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
  print(f"\n 💗30일 일봉데이터:") 
  print(df_daily.to_json())
  
  # 24시간 시간봉 데이터
  df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
  print(f"\n 💖24시간 시간봉데이터:") 
  print(df_hourly.to_json())



#   # 3. AI에게 데이터 제공하고 판단 받기
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


