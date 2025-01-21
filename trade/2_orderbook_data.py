import pyupbit

def get_orderbook_data():
    """
    업비트의 BTC-KRW 마켓의 오더북(호가 데이터)을 조회하는 함수
    
    Returns:
        dict: 정리된 오더북 데이터
        {
            "total_ask": float,  # 매도 총량
            "total_bid": float,  # 매수 총량
            "ask_bid_ratio": float,  # 매도/매수 비율
            "top5_orders": list  # 상위 5개 호가 정보
        }
    """
    # 오더북 데이터 조회
    orderbook = pyupbit.get_orderbook("KRW-BTC")
    
    # 데이터 정리
    orderbook_summary = {
        "total_ask": orderbook['total_ask_size'],
        "total_bid": orderbook['total_bid_size'],
        "ask_bid_ratio": orderbook['total_ask_size'] / orderbook['total_bid_size'],
        "top5_orders": [{
            "ask_price": unit['ask_price'],
            "ask_size": unit['ask_size'],
            "bid_price": unit['bid_price'],
            "bid_size": unit['bid_size']
        } for unit in orderbook['orderbook_units'][:5]]
    }
    
    # # 데이터 출력
    # print(f"\n📒 : 오더북 (호가데이터):")
    # print(f"매도 총량: {orderbook['total_ask_size']:.8f} BTC")
    # print(f"매수 총량: {orderbook['total_bid_size']:.8f} BTC")
    
    # print("\n호가 정보:")
    # for unit in orderbook['orderbook_units'][:5]:
    #     print(f"매도: {unit['ask_price']:,} KRW ({unit['ask_size']:.8f} BTC)")
    #     print(f"매수: {unit['bid_price']:,} KRW ({unit['bid_size']:.8f} BTC)")
    #     print("-" * 50)
    
    return orderbook_summary
