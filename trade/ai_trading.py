import os
from dotenv import load_dotenv
import pyupbit
import time
from trade.fear_and_greed import get_fear_greed_data
from trade.orderbook_data import get_orderbook_data
from trade.tec_analysis import calculate_indicators, analyze_market_data, get_market_data
from trade.wallet_manager import WalletManager
from trade.request_the_deepseek import get_ai_decision
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

        # [5]. AI에게 데이터 제공하고 판단 받기
        result = get_ai_decision(
            daily_30_analysis,
            daily_60_analysis,
            hourly_analysis,
            fear_greed_data,
            orderbook_summary
        )

        # [6]. 거래 기록 SQLite 데이터베이스에 저장하기
        current_price = pyupbit.get_current_price("KRW-BTC")  # 현재 비트코인 가격 가져오기
        korean_reason = save_the_record(  # 번역된 한국어 텍스트 받아오기
            price=current_price,
            decision=result['decision'],
            reason=result['reason']
        )

        # [7]. AI의 판단에 따라 실제로 자동매매 진행하기
        buy_sell_hold(result, upbit)

        # [8]. 🔔 매매 결과를 푸시 메시지로 보내기 
        send_push_notification(
            decision=result['decision'],
            reason=korean_reason  # 번역된 한국어 텍스트 사용
        )
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}") 