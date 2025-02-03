import pyupbit

def buy_sell_hold(result, upbit):
    print(f"\n🤖:") 
    print(f"응답 내용 확인:\n     decision: {result['decision']}")
    print(f"     percentage: {result['percentage']}%")
    print(f"     reason: {result['reason']}") 

    if result["decision"] == "buy":
        print("🖖🏻사라")
        my_krw = upbit.get_balance("KRW")
        buy_amount = my_krw * (result["percentage"] / 100) * 0.9995  # 수수료 고려
        
        # 살때는 수수료제외하고 5000원이상이여야 살 수 있음.
        if buy_amount > 5000:
            print(f"💰 KRW의 {result['percentage']}%인 {buy_amount}원으로 매수 시도")
            # print(upbit.buy_market_order("KRW-BTC", buy_amount))

    elif result["decision"] == "sell":
        print("👆🏼팔아라")
        my_btc = upbit.get_balance("KRW-BTC")
        sell_amount = my_btc * (result["percentage"] / 100)
        current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
        
        # 코인을 팔때는 체결금액에서 수수료제외하고 한화로 입금되니까 수수료 계산할필요X
        if sell_amount * current_price > 5000:
            print(f"💰 BTC의 {result['percentage']}%인 {sell_amount}BTC 매도 시도")
            # print(upbit.sell_market_order("KRW-BTC", sell_amount))
        
    elif result["decision"] == "hold":   
        print("🖐🏻홀드홀드") 