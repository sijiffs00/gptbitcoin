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
import json
from trade.fear_and_greed import get_fear_greed_data
from trade.img_capture import capture_chart, encode_image_to_base64
from trade.orderbook_data import get_orderbook_data
from trade.tec_analysis import calculate_indicators, analyze_market_data
import pandas as pd
from ds import get_deepseek_decision

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


  # [2]. 📒 오더북(호가 데이터) 조회
  orderbook_summary = get_orderbook_data()


  # 3. 차트 데이터 조회
  # 30일 일봉 데이터
  df_daily_30 = pyupbit.get_ohlcv("KRW-BTC", count=30, interval="day")
  df_daily_30 = calculate_indicators(df_daily_30, is_daily=True)
  
  # 60일 일봉 데이터
  df_daily_60 = pyupbit.get_ohlcv("KRW-BTC", count=60, interval="day")
  df_daily_60 = calculate_indicators(df_daily_60, is_daily=True)
  
  # 24시간 시간봉 데이터
  df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
  df_hourly = calculate_indicators(df_hourly, is_daily=False)

  # GPT-4o에 보낼 때:
  daily_30_analysis, daily_60_analysis, hourly_analysis = analyze_market_data(df_daily_30, df_daily_60, df_hourly)


  # [5]. 공포&탐욕지수 API요청 후 조회
  fear_greed_data = get_fear_greed_data()  # 데이터 받아오기

  # [6]. 차트 이미지 캡처하기
  from trade.img_capture import capture_chart, encode_image_to_base64
  
  # Chrome 옵션 설정 추가
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # 헤드리스 모드 설정
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument('--disable-gpu')
  
  os.makedirs('chart', exist_ok=True)
  capture_success = capture_chart(chrome_options)  # chrome_options 전달

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



  messages = [
      {
          "role": "system",
          "content": [
              {
                  "type": "text",
                  "text": "You are an expert in Bitcoin investing. Analyze the provided data and respond with a trading decision.\n\n"
                         "You must respond ONLY with this exact JSON format:\n"
                         "{\n"
                         "  \"decision\": \"buy\" or \"sell\" or \"hold\",\n"
                         "  \"reason\": \"detailed analysis reason\"\n"
                         "}\n\n"
                         "The decision field MUST be exactly one of: 'buy', 'sell', or 'hold'.\n"
                         "No other format or additional fields are allowed."
              }
          ]
      },
      {
          "role": "user",
          "content": [
              {
                  "type": "text",
                  "text": f"30 Days Analysis: {json.dumps(daily_30_analysis, indent=2)}\n"
                         f"60 Days Analysis: {json.dumps(daily_60_analysis, indent=2)}\n"
                         f"Hourly Analysis: {json.dumps(hourly_analysis, indent=2)}\n"
                         f"Fear and Greed Data: {fear_greed_data}\n"
                         f"Orderbook Data: {json.dumps(orderbook_summary)}"
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
      response_format={
          "type": "json_object"
      },
      temperature=0.7,
      max_tokens=500
  )
  # API 응답 확인을 위한 출력 추가
  result = response.choices[0].message.content
  
  # 토큰 사용량 출력
  print("\n🎯 토큰 사용량:")
  print(f"프롬프트 토큰: {response.usage.prompt_tokens}개")
  print(f"응답 토큰: {response.usage.completion_tokens}개")
  print(f"전체 토큰: {response.usage.total_tokens}개")
  
  # 응답 테스트
  try:
      result = json.loads(result)
      print(f"\n🔍 응답 타입: {type(result)}")  # dict 타입인지만 확인
      
      # decision 값이 허용된 값인지 확인
      if result['decision'] not in ['buy', 'sell', 'hold']:
          raise ValueError(f"Invalid decision value: {result['decision']}")
          
  except json.JSONDecodeError:
      print("❌ JSON 파싱 실패!")
      raise
  except KeyError as e:
      print(f"❌ 필수 필드 누락: {e}")
      raise
  except Exception as e:
      print(f"❌ 기타 오류 발생: {e}")
      raise

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
  from trade.buy_sell_hold import buy_sell_hold
  buy_sell_hold(result, upbit)

  # DeepSeek-R1으로 투자 판단 요청
  result = get_deepseek_decision(
      daily_30_analysis,
      daily_60_analysis,
      hourly_analysis,
      fear_greed_data,
      orderbook_summary,
      base64_image
  )

  # 결과 확인
  if result:
      print(f"\n🤖 DeepSeek의 판단:")
      print(f"결정: {result['decision']}")
      print(f"이유: {result['reason']}")


# while True :
#    import time
#    time.sleep(30)

ai_trading()


