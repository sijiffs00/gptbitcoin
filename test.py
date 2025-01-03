import os
import json
import time
import pyupbit
from openai import OpenAI
from dotenv import load_dotenv

# 0. env 파일 로드
load_dotenv()

def ai_trading():
  # 1. 업비트 차트 데이터 가져오기
  df_daily = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")  # 30일 일봉
  df_hourly = pyupbit.get_ohlcv("KRW-BTC", count=24, interval="hour") # 24시간 시간봉
  
  # 호가 데이터 (오더북) 가져오기
  orderbook = pyupbit.get_orderbook("KRW-BTC")
  bids = orderbook['orderbook_units'][:5]  # 매수 호가 상위 5개
  asks = orderbook['orderbook_units'][:5]  # 매도 호가 상위 5개

  # 2. 업비트 잔고조회 및 투자 상태 출력
  access = os.environ['UPBIT_ACCESS_KEY']
  secret = os.environ['UPBIT_SECRET_KEY']
  upbit = pyupbit.Upbit(access, secret)
  
  # 현재가 조회
  current_price = pyupbit.get_current_price("KRW-BTC")
  
  print("\n📊 시장 현황:")
  print(f"현재가: {current_price:,} KRW")
  
  print("\n📗 매도 호가:")
  for ask in asks[::-1]:  # 역순으로 출력
      print(f"가격: {ask['ask_price']:,} KRW | 수량: {ask['ask_size']:.4f} BTC")
      
  print("\n📕 매수 호가:")
  for bid in bids:
      print(f"가격: {bid['bid_price']:,} KRW | 수량: {bid['bid_size']:.4f} BTC")

  print(f"\n💰 내 자산:")
  krw_balance = upbit.get_balance("KRW")
  btc_balance = upbit.get_balance("KRW-BTC")
  btc_value = btc_balance * current_price if btc_balance else 0
  
  print(f"보유 현금: {krw_balance:,.0f} KRW")
  print(f"보유 비트코인: {btc_balance:.8f} BTC")
  print(f"비트코인 평가금액: {btc_value:,.0f} KRW")
  print(f"총 평가금액: {(krw_balance + btc_value):,.0f} KRW")

  # 3. AI에게 전달할 데이터 구성
  market_data = {
      "daily_chart": df_daily.to_dict(orient='records'),
      "hourly_chart": df_hourly.to_dict(orient='records'),
      "orderbook": orderbook,
      "current_price": current_price
  }

  # market_data를 JSON 문자열로 변환
  market_data_str = json.dumps(market_data, default=str)

  # 3. AI에게 데이터 제공하고 판단 받기
  from openai import OpenAI
  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are an expert in Bitcoin investing.\nAnalyze all market data including daily chart, hourly chart, orderbook, and current price.\nTell me whether to buy, sell, or hold at the moment.\nResponse in json format.\n\nResponse Example:\n{\"decision\": \"buy|sell|hold\", \"reason\": \"detailed analysis based on all provided data\"}"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": market_data_str
          }
        ]
      }
    ],
    response_format={
      "type": "json_object"
    },
  )


  # API 응답 확인을 위한 출력 추가
  result = response.choices[0].message.content

  # 4. AI의 판단에 따라 실제로 자동매매 진행하기
  result = json.loads(result)
  print(f"\n🤖:") 
  print(f"응답 내용 확인:\n     decision: {result["decision"]}")
  print(f"     reason: {result["reason"]}") 

  if result["decision"] == "buy":
      print("🖖🏻사라")
      my_krw = upbit.get_balance("KRW")

      # 살때는 수수료제외하고 5000원이상이여야 살 수 있음.
      # if my_krw*0.9995 > 5000:
      #     print(upbit.buy_market_order("KRW-BTC", my_krw*0.9995))

  elif result["decision"] == "sell":
      print("👆🏼팔아라")
      # my_btc = upbit.get_balance("KRW-BTC")
      # current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
      
      # 코인을 팔때는 체결금액에서 수수료제외하고 한화로 입금되니까 수수료 계산할필요X
      # if my_btc*current_price > 5000:
      #   print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
      
  elif result["decision"] == "hold":   
      print("🖐🏻홀드홀드")



while True:
    ai_trading()
    time.sleep(5)

# 푸시테스트