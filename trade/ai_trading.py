import os
from dotenv import load_dotenv
import pyupbit
import threading
import time
from trade.fear_and_greed import get_fear_greed_data
from trade.img_capture import capture_chart, encode_image_to_base64, setup_chrome_options
from trade.orderbook_data import get_orderbook_data
from trade.tec_analysis import calculate_indicators, analyze_market_data, get_market_data
from trade.s3_img_upload import upload_chart_to_s3
from trade.wallet_manager import WalletManager
from trade.request_the_gpt_4o import get_ai_decision
from trade.send_push_msg import send_push_notification
from trade.save_the_records import save_the_record
from trade.buy_sell_hold import buy_sell_hold

def ai_trading():
    try:
        # 업비트 객체 초기화
        upbit = pyupbit.Upbit(os.getenv('UPBIT_ACCESS_KEY'), os.getenv('UPBIT_SECRET_KEY'))

        # 1. 현재 투자상태 조회 (지갑 매니저 사용)
        wallet = WalletManager()
        wallet_info = wallet.get_wallet()
        print(f"\n💰 지갑:") 
        print(f"원금: {wallet_info['seed']:,} 원")
        print(f"보유 현금: {wallet_info['krw_balance']:,} KRW")
        print(f"보유 비트코인: {wallet_info['btc_balance']} BTC")
        print(f"마지막 업데이트: {wallet_info['last_updated']}")

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

        # S3 이미지 URL 초기화
        img_url = None
        
        if capture_success:
            success, s3_key = upload_chart_to_s3('chart/my_img.png')
            if success:
                print(f"\n📤 차트 이미지 S3 업로드 완료: {s3_key}")
                # S3 이미지 URL 생성
                img_url = f"https://aibitcoin-chart-img.s3.ap-northeast-2.amazonaws.com/{s3_key}"

        # [6]. AI에게 데이터 제공하고 판단 받기
        result = get_ai_decision(
            daily_30_analysis,
            daily_60_analysis,
            hourly_analysis,
            fear_greed_data,
            orderbook_summary,
            'chart/my_img.png'
        )

        # 이미지 분석이 끝났으니 이제 로컬 파일 삭제
        try:
            os.remove('chart/my_img.png')
            print("🗑️ 로컬 차트 이미지 삭제 완료")
        except Exception as e:
            print(f"로컬 이미지 파일 삭제 중 오류 발생: {e}")

        # [7]. 거래 기록 SQLite 데이터베이스에 저장하기
        current_price = pyupbit.get_current_price("KRW-BTC")  # 현재 비트코인 가격 가져오기
        korean_reason = save_the_record(  # 번역된 한국어 텍스트 받아오기
            price=current_price,
            decision=result['decision'],
            reason=result['reason'],
            img_url=img_url  # 이미지 URL 전달
        )

        # [8]. AI의 판단에 따라 실제로 자동매매 진행하기
        buy_sell_hold(result, upbit)

        # [9]. 🔔 매매 결과를 푸시 메시지로 보내기 
        send_push_notification(
            decision=result['decision'],
            reason=korean_reason  # 번역된 한국어 텍스트 사용
        )
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}") 