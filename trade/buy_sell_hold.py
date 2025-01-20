import pyupbit

def buy_sell_hold(result, upbit):
    """
    AI의 투자 판단(buy/sell/hold)에 따라 매매를 실행하는 함수
    
    Args:
        result (dict): AI의 투자 판단 결과 {"decision": str, "reason": str}
        upbit (pyupbit.Upbit): 업비트 API 객체
    
    Returns:
        None
    """
    print(f"\n🤖:") 
    print(f"응답 내용 확인:\n     decision: {result['decision']}")
    print(f"     reason: {result['reason']}") 

    if result["decision"] == "buy":
        print("🖖🏻사라")
        # my_krw = upbit.get_balance("KRW")

        # # 살때는 수수료제외하고 5000원이상이여야 살 수 있음.
        # if my_krw*0.9995 > 5000:
        #     print(upbit.buy_market_order("KRW-BTC", my_krw*0.9995))

    elif result["decision"] == "sell":
        print("👆🏼팔아라")

        # my_btc = upbit.get_balance("KRW-BTC")
        # current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]["ask_price"]
        
        # # 코인을 팔때는 체결금액에서 수수료제외하고 한화로 입금되니까 수수료 계산할필요X
        # if my_btc*current_price > 5000:
        #   print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
        
    elif result["decision"] == "hold":   
        print("🖐🏻홀드홀드") 