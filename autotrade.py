import os
from dotenv import load_dotenv
import pyupbit
import requests
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands
import base64 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from trade.fear_and_greed import get_fear_greed_data
from trade.img_capture import capture_chart, encode_image_to_base64

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
  # print(f"\n📒 : 오더북 (호가데이터):")
  
  # BTC-KRW 마켓에 대한 주요 정보만 출력
  # print(f"매도 총량: {orderbook['total_ask_size']:.8f} BTC")
  # print(f"매수 총량: {orderbook['total_bid_size']:.8f} BTC")
  
  # print("\n호가 정보:")
  for unit in orderbook['orderbook_units'][:5]:
      # print(f"매도: {unit['ask_price']:,} KRW ({unit['ask_size']:.8f} BTC)")
      # print(f"매수: {unit['bid_price']:,} KRW ({unit['bid_size']:.8f} BTC)")
      # print("-" * 50)
      pass


  # 3. 차트 데이터 조회
  # 30일 일봉 데이터
  df_daily = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
  
  # RSI 계산
  rsi = RSIIndicator(df_daily['close'], window=14)
  df_daily['rsi'] = rsi.rsi()
  
  # MACD 계산
  macd = MACD(df_daily['close'])
  df_daily['macd'] = macd.macd()
  df_daily['macd_signal'] = macd.macd_signal()
  
  # 볼린저 밴드 계산
  bollinger = BollingerBands(df_daily['close'])
  df_daily['bb_high'] = bollinger.bollinger_hband()
  df_daily['bb_low'] = bollinger.bollinger_lband()
  
  # 20일 이동평균선
  sma = SMAIndicator(df_daily['close'], window=20)
  df_daily['sma_20'] = sma.sma_indicator()
  
  # print(f"\n 💗 30일 일봉데이터:") 
  # print(df_daily.to_json())
  
  # 24시간 시간봉 데이터도 같은 방식으로 지표 계산
  df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
  
  # RSI 계산
  rsi = RSIIndicator(df_hourly['close'], window=14)
  df_hourly['rsi'] = rsi.rsi()
  
  # MACD 계산
  macd = MACD(df_hourly['close'])
  df_hourly['macd'] = macd.macd()
  df_hourly['macd_signal'] = macd.macd_signal()
  
  # 볼린저 밴드 계산
  bollinger = BollingerBands(df_hourly['close'])
  df_hourly['bb_high'] = bollinger.bollinger_hband()
  df_hourly['bb_low'] = bollinger.bollinger_lband()
  
  # 20시간 이동평균선
  sma = SMAIndicator(df_hourly['close'], window=20)
  df_hourly['sma_20'] = sma.sma_indicator()

#   print(f"\n 💖 24시간 시간봉데이터:") 
#   print(df_hourly.to_json())


  # 4. Ta 라이브러리를 활용한 기술적 분석
  # 4-1) 일봉 데이터에 대한 기술적 지표 계산
  print("\n📊 일봉 기술적 지표:")
  print(df_daily[['close', 'rsi', 'macd', 'macd_signal', 'bb_high', 'bb_low', 'sma_20']].tail().to_string())
  
  # 4-2) 시간봉 데이터에 대한 기술적 지표 계산
  print("\n⏰ 시간봉 기술적 지표:")
  print(df_hourly[['close', 'rsi', 'macd', 'macd_signal', 'bb_high', 'bb_low', 'sma_20']].tail().to_string())

  # [5]. 공포&탐욕지수 API요청 후 조회
  fear_greed_data = get_fear_greed_data()  # 데이터 받아오기

  # [6]. 차트 이미지 캡처하기
  from trade.img_capture import capture_chart, encode_image_to_base64
  os.makedirs('chart', exist_ok=True) 
  capture_success = capture_chart() # 캡쳐된 이미지는 'chart'폴더안에 저장됨.

  # 7. AI에게 데이터 제공하고 판단 받기
  from openai import OpenAI
  client = OpenAI()

  # 이미지 인코딩
  try:
      base64_image = encode_image_to_base64('chart/my_img.png')
      print("\n📸 이미지 인코딩 성공!")
      print(f"인코딩된 이미지 길이: {len(base64_image)} 문자")
  except FileNotFoundError:
      print("차트 이미지를 찾을 수 없어 :(")
      base64_image = None

  # API 요청 메시지 준비
  messages = [
      {
          "role": "system",
          "content": [
              {
                  "type": "text",
                  "text": "You are an expert in Bitcoin investing. Analyze the following data:\n"
                         "1. Technical indicators:\n"
                         "- RSI (oversold < 30, overbought > 70)\n"
                         "- MACD and MACD Signal crossovers\n"
                         "- Bollinger Bands position\n"
                         "- SMA 20 trend\n"
                         "2. Fear and Greed Index:\n"
                         "- Current market sentiment\n"
                         "- Recent trend in sentiment\n\n"
                         "Provide buy/sell/hold decision based on both technical and sentiment analysis.\n"
                         "Response in json format: {\"decision\": \"buy\", \"reason\": \"technical and sentiment analysis reason\"}"
              }
          ]
      },
      {
          "role": "user",
          "content": [
              {
                  "type": "text",
                  "text": f"Daily Data: {df_daily.to_json()}\n"
                         f"Hourly Data: {df_hourly.to_json()}\n"
                         f"Fear and Greed Data: {fear_greed_data}"
              }
          ]
      }
  ]

  # 이미지가 있으면 메시지에 추가
  if base64_image:
      messages[1]["content"].append({
          "type": "image_url",
          "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
      })
      print("🎨 API 요청에 이미지가 포함되었어!")
  else:
      print("⚠️ API 요청에 이미지가 포함되지 않았어!")

  response = client.chat.completions.create(
      model="gpt-4o",
      messages=messages,
      response_format={"type": "json_object"},
  )
  # API 응답 확인을 위한 출력 추가
  result = response.choices[0].message.content

  # 이미지 파일 이름 변경 (삭제하지 않고)
  if base64_image:  # 이미지가 있었을 때만 시도
      try:
          # 현재 시간을 원하는 형식으로 포맷팅 (예: 2501181428)
          current_time = datetime.now().strftime("%d%H%M%S")
          new_filename = f'chart/my_img{current_time}.png'
          
          # 파일 이름 변경
          os.rename('chart/my_img.png', new_filename)
          print(f"📸 차트 이미지 파일명 변경 완료: {new_filename}")
      except FileNotFoundError:
          print("❌ 이미지 파일을 찾을 수 없어")
      except Exception as e:
          print(f"파일명 변경 중 오류 발생: {e}")

  # [4]. AI의 판단에 따라 실제로 자동매매 진행하기
  import json
  from trade.buy_sell_hold import buy_sell_hold
  
  result = json.loads(result)
  buy_sell_hold(result, upbit)


# while True :
#    import time
#    time.sleep(30)

ai_trading()


