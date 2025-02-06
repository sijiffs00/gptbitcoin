import os
from dotenv import load_dotenv
import pyupbit
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
from trade.fear_and_greed import get_fear_greed_data
from trade.img_capture import capture_chart, encode_image_to_base64, setup_chrome_options
from trade.orderbook_data import get_orderbook_data
from trade.tec_analysis import calculate_indicators, analyze_market_data, get_market_data
from trade.s3_img_upload import upload_chart_to_s3
import pandas as pd
from ds import get_deepseek_decision
import boto3
from trade.request_the_gpt_4o import get_ai_decision
from send_push_msg import send_push_notification

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


  # [3]. 📈 비트코인 시장 데이터 분석
     # 3-1. 업비트에서 30일/60일 일봉과 24시간 시간봉 데이터 가져오기 📈
  df_daily_30, df_daily_60, df_hourly = get_market_data("KRW-BTC")

     # 3-2. 기술적 분석: RSI, MACD, 볼린저밴드 등 계산하기 
  daily_30_analysis, daily_60_analysis, hourly_analysis = analyze_market_data(df_daily_30, df_daily_60, df_hourly)


  # [4]. 😱 공포&탐욕지수 API요청 후 조회
  fear_greed_data = get_fear_greed_data() 

  # [5]. 차트 이미지 캡처하고 S3버킷에 업로드
  chrome_options = setup_chrome_options()
  capture_success = capture_chart(chrome_options) 

  if capture_success:
      success, s3_key = upload_chart_to_s3('chart/my_img.png')
      if success:
          print(f"\n📤 차트 이미지 S3 업로드 완료: {s3_key}")

  # [6]. AI에게 데이터 제공하고 판단 받기
  result = get_ai_decision(
      daily_30_analysis,
      daily_60_analysis,
      hourly_analysis,
      fear_greed_data,
      orderbook_summary,
      'chart/my_img.png'
  )

  # 이미지 파일 이름 변경 (삭제하지 않고)
  if os.path.exists('chart/my_img.png'):  # 이미지가 있을 때만 시도
      try:
          current_time = datetime.now().strftime("%d%H%M%S")
          new_filename = f'chart/my_img{current_time}.png'
          os.rename('chart/my_img.png', new_filename)
          print(f"📸 차트 이미지 파일명 변경 완료: {new_filename}")
      except Exception as e:
          print(f"파일명 변경 중 오류 발생: {e}")

  # [7]. 거래 기록 SQLite 데이터베이스에 저장하기
  from trade.save_the_records import save_the_record
  current_price = pyupbit.get_current_price("KRW-BTC")  # 현재 비트코인 가격 가져오기
  save_the_record(
      price=current_price,
      decision=result['decision'],
      percentage=result['percentage'],
      reason=result['reason']
  )

  # [8]. AI의 판단에 따라 실제로 자동매매 진행하기
  from trade.buy_sell_hold import buy_sell_hold
  buy_sell_hold(result, upbit)

  # [9]. 매매 결과를 푸시 메시지로 보내기 📱
  send_push_notification(
      decision=result['decision'],
      percentage=result['percentage'],
      reason=result['reason']
  )

# while True :
#    import time
#    time.sleep(30)

ai_trading()


