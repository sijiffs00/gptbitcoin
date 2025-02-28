import pyupbit

def buy_sell_hold(result, upbit):
    # 매매 결정 출력
    print(f"\n💡 AI 매매 결정:")
    print(f"     decision: {result['decision']}")
    print(f"     reason: {result['reason']}")

    # 매매 비율은 항상 5%로 고정
    TRADE_PERCENTAGE = 5

    if result["decision"] == "buy":
        my_krw = upbit.get_balance("KRW")  # 보유 현금 조회
        if my_krw > 0:
            # 보유 현금의 5%로 매수
            buy_amount = my_krw * (TRADE_PERCENTAGE / 100) * 0.9995  # 수수료 고려
            
            if buy_amount >= 5000:  # 최소 주문 금액 5000원
                print(f"💰 KRW의 {TRADE_PERCENTAGE}%인 {buy_amount}원으로 매수 시도")
                upbit.buy_market_order("KRW-BTC", buy_amount)
            else:
                print("💡 매수하려는 금액이 너무 작아서 매수하지 않음")

    elif result["decision"] == "sell":
        my_btc = upbit.get_balance("KRW-BTC")  # 보유 BTC 조회
        if my_btc > 0:
            # 보유 BTC의 5%를 매도
            sell_amount = my_btc * (TRADE_PERCENTAGE / 100)
            
            if sell_amount * pyupbit.get_current_price("KRW-BTC") >= 5000:  # 최소 주문 금액 5000원
                print(f"💰 BTC의 {TRADE_PERCENTAGE}%인 {sell_amount}BTC 매도 시도")
                upbit.sell_market_order("KRW-BTC", sell_amount)
            else:
                print("💡 매도하려는 금액이 너무 작아서 매도하지 않음")

    else:  # "hold"
        print("💎 홀딩! 매매하지 않음") 